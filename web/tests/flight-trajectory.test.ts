import test from 'node:test';
import assert from 'node:assert/strict';
import { createFlightTrial, exportFlight, flightHash, reconstructFlight } from '../src/lib/engineeringFlight';
import { REFERENCE_INPUT_HASH, REFERENCE_RESULT_HASH } from '../src/lib/flightProgram';
import { compareRecordedFlights, recordedFlightMarkers, recordedFlightPositions, visibleFlightMarkers, visibleFlightVertexCount } from '../src/lib/flightTrajectory';

function editedTurnTrial() {
  const trial = createFlightTrial();
  const commands = trial.commands.map(command => command.id === 'climbing-turn' ? { ...command, turn: .3 } : command);
  return createFlightTrial(commands, trial.stop_step, trial.presentation.preset);
}

test('recorded vertices preserve the exact Y-up XYZ boundary samples and cursor never reveals future points', () => {
  const trial = createFlightTrial(), engine = reconstructFlight(trial, 200), frames = engine.frames();
  const vertices = recordedFlightPositions(frames);
  assert.equal(vertices.length, 201);
  for (const step of [0, 50, 76, 150, 200]) assert.deepEqual(vertices[step], frames[step].position);
  assert(vertices.some(([, y]) => y > trial.model.ground_y), 'the actual path includes altitude changes');
  assert.equal(visibleFlightVertexCount(vertices.length, 0), 1);
  assert.equal(visibleFlightVertexCount(vertices.length, 25), 26);
  assert.equal(visibleFlightVertexCount(vertices.length, 999), vertices.length);
  assert.equal(visibleFlightVertexCount(vertices.length, 0, true), vertices.length);
  assert.throws(() => recordedFlightPositions([{ ...trial.initial, time: .02 }]));
  assert.throws(() => recordedFlightPositions([{ ...trial.initial, position: [0, NaN, 0] }]));
  assert.throws(() => visibleFlightVertexCount(3, -1));
});

test('event markers use only recorded transitions and contacts at their recorded world coordinates', () => {
  const trial = createFlightTrial(), prefix = reconstructFlight(trial, 50);
  assert(!recordedFlightMarkers(prefix.frames(), trial, 'prefix').some(marker => marker.kind === 'takeoff'));
  const engine = reconstructFlight(trial), frames = engine.frames(), markers = recordedFlightMarkers(frames, trial, 'reference');
  const takeoff = markers.find(marker => marker.kind === 'takeoff')!;
  const airborne = markers.find(marker => marker.kind === 'airborne')!;
  const contact = markers.find(marker => marker.kind === 'contact')!;
  const landed = markers.find(marker => marker.kind === 'landed')!;
  const endpoint = markers.find(marker => marker.kind === 'endpoint')!;
  assert.equal(takeoff.step, 50); assert.deepEqual(takeoff.position, frames[50].position);
  assert.equal(airborne.step, frames.findIndex(frame => frame.state === 'flying'));
  assert.deepEqual(contact.position, frames[contact.step].position);
  assert.deepEqual(landed.position, frames[landed.step].position);
  assert.deepEqual(endpoint.position, frames.at(-1)!.position);
  assert.equal(visibleFlightMarkers(markers, 49).some(marker => marker.kind === 'takeoff'), false);
  assert.equal(visibleFlightMarkers(markers, 50).some(marker => marker.kind === 'takeoff'), true);
  assert.equal(visibleFlightMarkers(markers, 0, true).length, markers.length);
  assert(!markers.some(marker => marker.kind === 'contact' && marker.label.includes('CEILING')));

  const boundaryTrial = createFlightTrial([{ id: 'launch', step: 0, forward: 1, turn: 0, vertical: 1, intent: 'TAKEOFF' }]);
  const boundaryEngine = reconstructFlight(boundaryTrial);
  const boundaryMarkers = recordedFlightMarkers(boundaryEngine.frames(), boundaryTrial, 'boundary-run').filter(marker => marker.kind === 'contact');
  assert(boundaryMarkers.some(marker => marker.label.includes('CEILING') || marker.label.includes('X_WALL') || marker.label.includes('Z_WALL')));
  for (const marker of boundaryMarkers) assert.deepEqual(marker.position, boundaryEngine.frame(marker.step).position);
});

test('reference/custom overlays compare independent plant histories at matched boundaries', async () => {
  const referenceTrial = createFlightTrial(), customTrial = editedTurnTrial();
  const reference = reconstructFlight(referenceTrial), custom = reconstructFlight(customTrial);
  const referenceResult = await exportFlight(reference, 'normal');
  assert.equal(await flightHash(referenceTrial), REFERENCE_INPUT_HASH);
  assert.equal(referenceResult.result_sha256, REFERENCE_RESULT_HASH);
  assert.deepEqual(compareRecordedFlights(reference.frames(), reference.frames(), 600, 600, 600)?.separation, 0);
  const result = compareRecordedFlights(custom.frames(), reference.frames(), 600, 600, 600)!;
  assert.notDeepEqual(result.current, result.reference);
  assert(Math.abs(result.finalSeparation! - .204279) < 1e-6);
  assert.deepEqual(result.current, custom.frame(600).position);
  assert.deepEqual(result.reference, reference.frame(600).position);
  assert.equal(result.finalSeparation, result.separation);
  assert.equal(compareRecordedFlights(custom.frames().slice(0, 40), reference.frames(), 100, 600, 600), null);
  const shortTrial = createFlightTrial(referenceTrial.commands.filter(command => command.step < 300), 300);
  const short = reconstructFlight(shortTrial);
  assert.equal(compareRecordedFlights(short.frames(), reference.frames(), 300, 300, 600)?.finalSeparation, null,
    'completed runs with different horizons have no same-time final separation');
});

test('a run ending airborne has no invented landing marker or completed endpoint', () => {
  const base = createFlightTrial();
  const trial = createFlightTrial(base.commands.filter(command => command.step < 300), 300);
  const engine = reconstructFlight(trial);
  assert.equal(engine.snapshot().state, 'flying');
  const markers = recordedFlightMarkers(engine.frames(), trial, 'airborne-run');
  assert(markers.some(marker => marker.kind === 'airborne'));
  assert(!markers.some(marker => marker.kind === 'landed'));
  assert(markers.some(marker => marker.kind === 'endpoint'), 'a completed run may mark its final state even when it ends airborne');
  for (const marker of markers.filter(event => event.kind === 'contact')) assert.deepEqual(marker.position, engine.frame(marker.step).position);
});
