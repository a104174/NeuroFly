/** Read-only presentation helpers for already validated engineering-flight records. */
import type { FlightFrame, FlightTrial, Vec3 } from './engineeringFlight';

export type FlightTrajectoryEventKind = 'takeoff' | 'airborne' | 'landing' | 'landed' | 'contact' | 'endpoint';
export type FlightTrajectoryMarker = {
  id: string;
  kind: FlightTrajectoryEventKind;
  label: string;
  step: number;
  time: number;
  position: Vec3;
  source: string;
};

export type FlightTrajectoryLayer = { id: string; trial: FlightTrial; frames: readonly FlightFrame[] };
export type FlightTrajectoryDisplay = { current: FlightTrajectoryLayer; reference?: FlightTrajectoryLayer; cursorStep: number; fullRecorded: boolean };

export function recordedFlightPositions(frames: readonly FlightFrame[]): Vec3[] {
  if (!Array.isArray(frames) || frames.length === 0) throw new Error('A recorded flight must include its initial boundary.');
  return frames.map((frame, index) => {
    const position: unknown = frame.position;
    if (frame.step !== index || !Number.isFinite(frame.time) || Math.abs(frame.time - frame.step * .02) > 1e-10 ||
        !Array.isArray(position) || position.length !== 3 || position.some((value: unknown) => typeof value !== 'number' || !Number.isFinite(value))) {
      throw new Error(`Invalid recorded flight coordinate at boundary ${index}.`);
    }
    return [position[0] as number, position[1] as number, position[2] as number] as Vec3;
  });
}

/** Number of recorded vertices visible at this cursor. Full-path display is an explicit user choice. */
export function visibleFlightVertexCount(recordedCount: number, cursorStep: number, fullRecorded = false): number {
  if (!Number.isInteger(recordedCount) || recordedCount < 0 || !Number.isInteger(cursorStep) || cursorStep < 0) {
    throw new Error('Invalid trajectory cursor or recorded vertex count.');
  }
  return fullRecorded ? recordedCount : Math.min(recordedCount, cursorStep + 1);
}

export function visibleFlightMarkers(markers: readonly FlightTrajectoryMarker[], cursorStep: number, fullRecorded = false): FlightTrajectoryMarker[] {
  if (!Number.isInteger(cursorStep) || cursorStep < 0) throw new Error('Invalid trajectory marker cursor.');
  return fullRecorded ? [...markers] : markers.filter(marker => marker.step <= cursorStep);
}

/** Events are read from engine-produced frames and placed at their recorded event boundary. */
export function recordedFlightMarkers(frames: readonly FlightFrame[], trial: FlightTrial, source: string): FlightTrajectoryMarker[] {
  if (!frames.length || !source) return [];
  const positions = recordedFlightPositions(frames);
  const markers: FlightTrajectoryMarker[] = [];
  const seen = new Set<string>();
  for (const owner of frames) for (const event of owner.events) {
    if (event.kind !== 'TRANSITION' && event.kind !== 'CONTACT') continue;
    const step = event.step;
    if (!Number.isInteger(step) || step < 0 || step >= positions.length || Math.abs(event.time - step * .02) > 1e-10) continue;
    let kind: FlightTrajectoryEventKind | undefined;
    let label = event.detail;
    if (event.kind === 'CONTACT') {
      kind = 'contact';
      label = `Contact · ${event.detail}`;
    } else {
      const destination = event.detail.split('->')[1];
      if (destination === 'takeoff') { kind = 'takeoff'; label = 'Takeoff'; }
      else if (destination === 'flying') { kind = 'airborne'; label = 'Flying'; }
      else if (destination === 'landing') { kind = 'landing'; label = 'Landing'; }
      else if (destination === 'grounded') { kind = 'landed'; label = 'Landed'; }
    }
    if (!kind) continue;
    const id = `${source}:${kind}:${step}:${event.detail}`;
    if (seen.has(id)) continue;
    seen.add(id);
    markers.push({ id, kind, label, step, time: event.time, position: positions[step], source });
  }
  const last = frames.at(-1)!;
  if (last.step === trial.stop_step) {
    const step = last.step, id = `${source}:endpoint:${step}`;
    markers.push({ id, kind: 'endpoint', label: 'Final recorded position', step, time: last.time, position: positions[step], source });
  }
  return markers.sort((a, b) => a.step - b.step || a.kind.localeCompare(b.kind) || a.source.localeCompare(b.source));
}

export type FlightTrajectoryComparison = {
  step: number;
  time: number;
  current: Vec3;
  reference: Vec3;
  separation: number;
  finalSeparation: number | null;
};

/** Matched-boundary metrics are calculated from authoritative frame records, never rendered vertices. */
export function compareRecordedFlights(
  current: readonly FlightFrame[], reference: readonly FlightFrame[], step: number,
  currentStopStep: number, referenceStopStep: number,
): FlightTrajectoryComparison | null {
  if (!Number.isInteger(step) || step < 0 || step >= current.length || step >= reference.length) return null;
  const a = current[step], b = reference[step];
  if (a.step !== step || b.step !== step || Math.abs(a.time - b.time) > 1e-10) return null;
  const separation = Math.hypot(a.position[0] - b.position[0], a.position[1] - b.position[1], a.position[2] - b.position[2]);
  const ca = current.at(-1)!, rb = reference.at(-1)!;
  const complete = ca.step === currentStopStep && rb.step === referenceStopStep && ca.step === rb.step && Math.abs(ca.time - rb.time) <= 1e-10;
  const finalSeparation = complete
    ? Math.hypot(ca.position[0] - rb.position[0], ca.position[1] - rb.position[1], ca.position[2] - rb.position[2])
    : null;
  return { step, time: a.time, current: [...a.position], reference: [...b.position], separation, finalSeparation };
}
