/** One active body integrator per global interval; engine counters remain episode-local. */
import { FlightEngine, FLIGHT_MODEL, createFlightTrial, flightHash, flightCanonical, type FlightFrame, flightBounds } from './engineeringFlight';
import { TouchAndGoSession, TOUCH_AND_GO_CONFIG, decideTouchAndGo, type TouchAndGoState } from './flightTouchAndGo';
import { LiveGroundSession, type LiveSample } from './liveGroundSession';
import { locomotionBounds } from './experimentalLocomotion';
import type { NeuralArtifact } from './neuralLocomotion';
import { observeFlightArena } from './flightArenaObservations';
import { decideReactiveFlight, reactiveFlightMetrics, type ReactiveControllerState, type ReactiveFlightStatus } from './reactiveFlightExploration';

export const MIXED_PROTOCOL = {
  schema: 'mixed_ground_flight_v1', version: 1, reference_revision: '6a5708a8f5f68f8e7f7c58b24f84013cc02d2076',
  initial_flight_configuration: TOUCH_AND_GO_CONFIG,
  plant: FLIGHT_MODEL.schema, ground: 'live_ground_session_v1', ground_mode: 'baseline_v10_5b',
  neural_policy: 'FRESH_ZERO_HS_DNP15_EPISODE_ON_LANDING_NO_FLIGHT_NEURAL_CONTINUITY',
  walking_distance_units: .05, minimum_takeoff_clearance_units: .06,
  interval_s: .02, maximum_steps: 1500, randomness: 'NONE', seed: null,
  flight_initialization: 'ACCEPTED_WALKING_XYZ_HEADING_AND_PLANAR_VELOCITY_VY_ZERO',
  termination: 'SECOND_FLIGHT_WITH_SUBSEQUENT_EXPLORATION_INTERVAL',
} as const;
export const SUSTAINED_MIXED_PROTOCOL = {
  ...MIXED_PROTOCOL, schema: 'mixed_ground_flight_sustained_v2', version: 2,
  reference_revision: 'b76481accc006c4665c93db1af4fc1f67ef14083',
  walking_distance_units: .18, minimum_walking_intervals: 50, maximum_steps: 3000,
  termination: 'FINITE_60_SECOND_WINDOW_WITH_STATE_DEPENDENT_REPEATED_EPISODES',
  landing_recovery: 'ABORT_BRAKING_WHEN_EXISTING_LANDING_CLEARANCE_IS_UNSATISFIED',
  ground_envelope: 'ACTUAL_GROUND_BOUNDS; FLIGHT_BOUNDS_REVALIDATED_AT_TAKEOFF',
  acceptance: 'TWO_COMPLETED_GROUND_EPISODES_AND_AT_LEAST_THREE_TAKEOFFS_WITH_SAFE_CONTINUITY',
} as const;
export function sustainedTakeoffEligible(distance: number, frame: FlightFrame, walkingIntervals: number) {
  if (!Number.isFinite(distance) || distance < SUSTAINED_MIXED_PROTOCOL.walking_distance_units ||
      !Number.isSafeInteger(walkingIntervals) || walkingIntervals < SUSTAINED_MIXED_PROTOCOL.minimum_walking_intervals ||
      frame.contacts.some(c=>c!=='FLOOR')) return false;
  const bounds=flightBounds();
  if(frame.position.some((v,i)=>!Number.isFinite(v)||v<bounds.min[i]||v>bounds.max[i])) return false;
  return walkingTakeoffEligible(distance,frame);
}
type Source = 'flight_initial' | 'ground' | 'flight_resumed';
export type BodyHandoff = {
  global_step: number; global_time_s: number; from: Source; to: Source; reason: string;
  position: [number,number,number]; heading: number; velocity: [number,number,number];
  position_discontinuity: number; heading_discontinuity: number;
  neural_initialization: { hs: number[]; dn: number[]; first_observation: null } | null;
};
export function validateLandingHandoff(frame: FlightFrame, authority: NeuralArtifact) {
  const limits = locomotionBounds(authority.config.body);
  if (frame.state !== 'grounded' || !frame.contacts.includes('FLOOR') ||
      ![...frame.position,...frame.velocity,frame.heading].every(Number.isFinite) || frame.velocity.some(v => v !== 0) ||
      frame.position[1] !== authority.config.body.initial_position[1] ||
      Math.abs(frame.position[0]) > limits[0] || Math.abs(frame.position[2]) > limits[1])
    throw new Error('Inadmissible flight-to-ground handoff');
  return { position: [...frame.position] as [number,number,number], heading: frame.heading };
}
export function walkingTakeoffEligible(distance: number, frame: FlightFrame) {
  const o = observeFlightArena(frame);
  return Number.isFinite(distance) && distance >= MIXED_PROTOCOL.walking_distance_units && frame.state === 'grounded' &&
    frame.velocity[1] === 0 && o.floor_clearance_units === 0 &&
    Math.min(o.forward_wall_clearance_units,o.left_wall_clearance_units,o.right_wall_clearance_units) >= MIXED_PROTOCOL.minimum_takeoff_clearance_units &&
    o.ceiling_clearance_units >= .36;
}
type Interval = {
  global_step: number; global_time_s: number; active_engine: Source; source_local_step: number;
  controller_phase_before: string; controller_phase_after: string; numerical_validity: 'FINITE_AND_WITHIN_CONSERVATIVE_BOUNDS';
  observation: ReturnType<typeof observeFlightArena>; decision: { reason: string };
  sustained?: { episode_id: number; ground_path_since_landing: number; retakeoff_eligible: boolean; landing_eligible: boolean | null; ground_neural: LiveSample['interval']['neural_summary'] | null };
  native_evidence: unknown; accepted: FlightFrame; command_origin: string;
};
export class MixedGroundFlightSession {
  private first = new TouchAndGoSession();
  private ground: LiveGroundSession | null = null;
  private resumed: FlightEngine | null = null;
  private source: Source = 'flight_initial';
  private body = this.first.snapshot();
  private readonly frames: FlightFrame[] = [this.body];
  private readonly intervals: Interval[] = [];
  private readonly handoffs: BodyHandoff[] = [];
  private reactive: ReactiveControllerState = { phase: 'takeoff', avoidance_turn: 0 };
  private distance = 0;
  private episodeId = 0;
  private touchState: TouchAndGoState = {phase:'takeoff',reactive:{phase:'takeoff',avoidance_turn:0},floor_verified:false};
  private failure: string | null = null;
  private termination: string | null = null;
  status: ReactiveFlightStatus = 'ready';
  constructor(private readonly authority: NeuralArtifact, readonly sustained = false) {}
  private bounds(source: Source) {
    if (!this.sustained || source !== 'ground') return flightBounds();
    const [x,z]=locomotionBounds(this.authority.config.body), b=flightBounds();
    return {min:[-x,b.min[1],-z] as [number,number,number],max:[x,b.max[1],z] as [number,number,number]};
  }
  get controllerPhase() { return this.source === 'ground' ? 'walking' : this.source === 'flight_initial' ? this.first.controllerPhase : this.sustained ? this.touchState.phase : this.reactive.phase; }
  get stopStep() { return this.termination ? this.body.step : this.sustained ? SUSTAINED_MIXED_PROTOCOL.maximum_steps : MIXED_PROTOCOL.maximum_steps; }
  get error() { return this.failure; }
  snapshot() { return structuredClone(this.body); }
  latestInterval() { return structuredClone(this.intervals.at(-1) ?? null); }
  records() { return structuredClone(this.intervals); }
  start() {
    if (!['ready','paused'].includes(this.status)) throw new Error('Mixed session cannot start');
    this.status = 'running';
    if (this.source === 'flight_initial') this.first.start();
    if (this.source === 'ground') this.ground!.start();
  }
  pause() { if (this.status === 'running') { this.status = 'paused'; this.first.pause(); this.ground?.pause(); } }
  dispose() { this.pause(); this.ground?.stop(); }
  private transfer(to: Source, reason: string, destination: {position: number[]; heading: number}, neural: BodyHandoff['neural_initialization'] = null) {
    this.handoffs.push({ global_step: this.body.step, global_time_s: this.body.time, from: this.source, to, reason,
      position_discontinuity: Math.hypot(...this.body.position.map((v,i)=>v-destination.position[i])), heading_discontinuity: Math.abs(this.body.heading-destination.heading),
      position: [...this.body.position], heading: this.body.heading, velocity: [...this.body.velocity], neural_initialization: neural });
    this.source = to; if(this.sustained)this.episodeId++;
  }
  advance() {
    if (this.status !== 'running') throw new Error('Mixed session is not running');
    try {
      const phaseBefore = this.controllerPhase;
      const before = this.snapshot(), source = this.source, observation = observeFlightArena(before,this.bounds(source));
      let accepted: FlightFrame, native: unknown, local: number, reason: string;
      if (source === 'flight_initial') {
        accepted = this.first.advance(); native = this.first.latestInterval(); local = before.step;
        reason = this.first.latestInterval()!.decision.reason;
      } else if (source === 'ground') {
        const previous = this.ground!.snapshot(); const sample: LiveSample = this.ground!.advance();
        const f = sample.accepted; if (!this.sustained && (f.contact || sample.interval.contact)) throw new Error('Ground contact prevents safe handoff episode'); local = previous.step; native = sample; reason = 'EXISTING_NEURAL_INFLUENCED_GROUND_INTERVAL';
        const velocity = f.position.map((v,i) => (v-previous.position[i])/.02) as [number,number,number];
        this.distance += Math.hypot(f.position[0]-previous.position[0],f.position[2]-previous.position[2]);
        accepted = { ...before, position: [...f.position], heading: f.heading, velocity, state: 'grounded', contacts: ['FLOOR',...(this.sustained && f.contact ? [f.contact] : [])], events: this.sustained && f.contact && f.contact!==previous.contact ? [{kind:'CONTACT',step:before.step+1,time:(before.step+1)*.02,detail:f.contact}] : [], commandId: null };
      } else {
        const f = this.resumed!.snapshot(); local = f.step;
        const o = observeFlightArena(f);
        const command = f.state === 'grounded' ? { id: 'mixed-retakeoff', step:f.step, forward:0, turn:0, vertical:.8, intent:'TAKEOFF' as const } : null;
        let decision = command ? null : this.sustained ? decideTouchAndGo(this.touchState,o) : decideReactiveFlight(this.reactive,o);
        if (this.sustained && decision && 'landing_eligible' in decision &&
            decision.state_after.phase === 'braking' &&
            Math.min(o.forward_wall_clearance_units,o.left_wall_clearance_units,o.right_wall_clearance_units) < TOUCH_AND_GO_CONFIG.minimum_horizontal_clearance) {
          const recovery=decideReactiveFlight({phase:'exploring',avoidance_turn:0},o);
          decision={...decision,state_after:{...this.touchState,phase:'exploring',reactive:recovery.state_after},command:recovery.command,
            reason:'UNSAFE_LANDING_CLEARANCE_RETURN_TO_REACTIVE_EXPLORATION',reactive_decision:recovery};
        }
        accepted = this.resumed!.advanceWithCommand(command ?? decision!.command);
        if (decision) {
          if(this.sustained)this.touchState=decision.state_after as TouchAndGoState;
          else this.reactive=decision.state_after as ReactiveControllerState;
        }
        native = { observation:o, command:command ?? decision!.command, decision, accepted };
        reason = command ? 'ACCEPTED_WALKING_ENDPOINT_REQUESTS_TAKEOFF' : decision!.reason;
        const offset = before.step-local;
        accepted = { ...accepted, stateSince: accepted.stateSince+offset*.02, events: accepted.events.map(e => ({...e,step:e.step+offset,time:(e.step+offset)*.02})) };
      }
      accepted = { ...accepted, step:before.step+1, time:(before.step+1)*.02 };
      observeFlightArena(accepted,this.bounds(source));
      if (accepted.events.some(e => e.kind === 'REJECTED_COMMAND')) throw new Error('Rejected mixed flight command');
      this.body = structuredClone(accepted); this.frames.push(this.body);
      this.intervals.push({global_step:before.step,global_time_s:before.time,active_engine:source,source_local_step:local,controller_phase_before:phaseBefore,controller_phase_after:this.controllerPhase,numerical_validity:'FINITE_AND_WITHIN_CONSERVATIVE_BOUNDS',observation,decision:{reason},native_evidence:native,accepted:this.body,command_origin:source === 'ground' ? 'EXISTING_GROUND_HS_DNP15_AND_ENGINEERING_DRIVE' : 'ENGINEERING_FLIGHT_FEEDBACK'});
      if(this.sustained) {
        const sample=source==='ground'?native as LiveSample:null;
        const nativeDecision=source==='flight_initial'?this.first.latestInterval()!.decision:(native as {decision?:{landing_eligible?:boolean}}).decision;
        this.intervals.at(-1)!.sustained={episode_id:this.episodeId,ground_path_since_landing:this.distance,
          retakeoff_eligible:source==='ground'&&sustainedTakeoffEligible(this.distance,this.body,this.ground!.snapshot().step),
          landing_eligible:nativeDecision && 'landing_eligible' in nativeDecision ? nativeDecision.landing_eligible ?? null : null,
          ground_neural:sample?.interval.neural_summary ?? null};
      }
      if ((source === 'flight_initial' || (this.sustained && source === 'flight_resumed')) && accepted.state === 'grounded' && accepted.step > 0) {
        const pose = validateLandingHandoff(accepted,this.authority); this.first.pause(); if(this.sustained)this.distance=0;
        this.ground = new LiveGroundSession(this.authority,true,'mixed-ground-episode-v1'+(this.sustained?'-'+this.episodeId:''),undefined,pose);
        const f = this.ground.snapshot();
        if (flightCanonical(f.position) !== flightCanonical(accepted.position) || f.heading !== accepted.heading || f.hs.some(v=>v!==0) || f.dn.some(v=>v!==0)) throw new Error('Ground initialization mismatch');
        this.transfer('ground','ACCEPTED_LANDING_FLOOR_CONTACT',f,{hs:[...f.hs],dn:[...f.dn],first_observation:null}); this.ground.start();
      } else if (source === 'ground' && (this.sustained ? sustainedTakeoffEligible(this.distance,this.body,this.ground!.snapshot().step) : walkingTakeoffEligible(this.distance,this.body))) {
        this.touchState={phase:'takeoff',reactive:{phase:'takeoff',avoidance_turn:0},floor_verified:false};
        this.resumed = new FlightEngine(createFlightTrial([],1500),FLIGHT_MODEL.arena,{ position:[...this.body.position], heading:this.body.heading, velocity:[...this.body.velocity] });
        const f = this.resumed.snapshot();
        if (flightCanonical(f.position)!==flightCanonical(this.body.position) || f.heading!==this.body.heading) throw new Error('Flight initialization mismatch');
        this.ground!.stop(); this.transfer('flight_resumed','ACCEPTED_WALKING_DISTANCE_AND_CLEARANCE',f);
      } else if (!this.sustained && source === 'flight_resumed' && before.state === 'flying' && accepted.state === 'flying') {
        this.termination='SECOND_FLIGHT_CONFIRMED'; this.status='completed';
      }
      this.intervals.at(-1)!.controller_phase_after = this.controllerPhase;
      if(this.sustained && accepted.step>=SUSTAINED_MIXED_PROTOCOL.maximum_steps) {
        this.termination='DURATION_WINDOW_COMPLETED';this.status='completed';this.ground?.stop();
      }
      if (!this.sustained && !this.termination && accepted.step>=1500) { this.termination='DURATION_LIMIT_REACHED'; this.failure='Mixed sequence not completed'; this.status='failed'; this.ground?.stop(); }
      return this.snapshot();
    } catch (error) {
      this.failure=error instanceof Error?error.message:String(error);this.termination='FAILED';this.status='failed';this.first.pause();this.ground?.stop();throw error;
    }
  }
  presentationBodySamples(frame = this.body) {
    const walking=this.intervals.filter(i=>i.active_engine==='ground' && (!this.sustained || i.sustained?.episode_id===this.episodeId));
    return this.source==='ground' && walking.length
      ? [walking[0].observation.accepted,...walking.map(i=>i.accepted)].map(f=>({time:f.time,position:f.position,heading:f.heading}))
      : [{time:frame.time,position:frame.position,heading:frame.heading}];
  }
  metrics() {
    const events=this.frames.flatMap(f=>f.events);
    const base=reactiveFlightMetrics(this.frames[0],this.frames,[],events);
    const ground=this.intervals.filter(i=>i.active_engine==='ground');
    const metrics = {...base,steering_response_count:this.first.metrics().steering_response_count,
      minimum_observed_wall_clearance_units:this.intervals.length?Math.min(...this.intervals.flatMap(i=>[i.observation.forward_wall_clearance_units,i.observation.left_wall_clearance_units,i.observation.right_wall_clearance_units])):null,
      airborne_duration_s:this.intervals.filter(i=>['flying','landing'].includes(i.observation.accepted.state)).length*.02,
      walking_distance_units:this.distance,walking_duration_s:ground.length*.02,
      walking_heading_change:ground.length?ground.at(-1)!.accepted.heading-ground[0].observation.accepted.heading:0,
      handoffs:this.handoffs,transitions:events.filter(e=>e.kind==='TRANSITION'),
      maximum_handoff_position_discontinuity:Math.max(0,...this.handoffs.map(h=>h.position_discontinuity)), maximum_timestamp_discontinuity:Math.max(0,...this.frames.map((f,i)=>Math.abs(f.time-i*.02)))};
    if(!this.sustained)return metrics;
    const episodes: {id:number;type:Source;start_s:number;end_s:number;duration_s:number;distance_units:number;heading_change:number;contacts:FlightFrame['events'];complete:boolean;controller_transitions:{time_s:number;from:string;to:string;reason:string}[];neural_initialization:BodyHandoff['neural_initialization']}[]=[];
    for(const i of this.intervals){
      const id=i.sustained!.episode_id;
      let e=episodes.at(-1);
      if(!e||e.id!==id) {
        e={id,type:i.active_engine,start_s:i.global_time_s,end_s:i.global_time_s,duration_s:0,distance_units:0,heading_change:0,contacts:[],complete:false,controller_transitions:[],
          neural_initialization:this.handoffs.find(h=>h.global_step===i.global_step)?.neural_initialization??null};episodes.push(e);
      }
      e.end_s=i.accepted.time;e.duration_s+=.02;e.distance_units+=Math.hypot(i.accepted.position[0]-i.observation.accepted.position[0],i.accepted.position[2]-i.observation.accepted.position[2]);
      e.heading_change+=i.accepted.heading-i.observation.accepted.heading;e.contacts.push(...i.accepted.events.filter(v=>v.kind==='CONTACT'));
      if(i.controller_phase_before!==i.controller_phase_after || i.decision.reason==='UNSAFE_LANDING_CLEARANCE_RETURN_TO_REACTIVE_EXPLORATION')
        e.controller_transitions.push({time_s:i.global_time_s,from:i.controller_phase_before,to:i.controller_phase_after,reason:i.decision.reason});
      e.complete=this.handoffs.some(h=>h.global_step===i.accepted.step);
    }
    const walked=episodes.filter(e=>e.type==='ground');
    const violations=this.intervals.filter(i=>i.accepted.position.some((v,a)=>v<this.bounds(i.active_engine).min[a]||v>this.bounds(i.active_engine).max[a])).length;
    return {...metrics,accepted_bound_violations:violations,
      walking_heading_change:walked.reduce((sum,e)=>sum+e.heading_change,0),
      steering_response_count:this.intervals.filter(i=>{
        const n=i.native_evidence as {decision?:{reactive_decision?:{boundary_response?:string}}};
        return ['started','redirected'].includes(n.decision?.reactive_decision?.boundary_response??'');
      }).length,
      walking_distance_units:walked.reduce((sum,e)=>sum+e.distance_units,0),
      takeoff_count:events.filter(e=>e.detail==='grounded->takeoff').length,
      landing_count:events.filter(e=>e.detail==='landing->grounded').length,
      ground_episode_count:walked.length,episodes};

  }
  result() {
    if(!this.termination)throw new Error('Mixed session not terminal');
    return structuredClone({schema:this.sustained?'mixed_ground_flight_sustained_result_v2':'mixed_ground_flight_result_v1',configuration:this.sustained?SUSTAINED_MIXED_PROTOCOL:MIXED_PROTOCOL,initial:this.frames[0],
      provenance:{ground_source:this.authority.artifact_id,ground_config:this.authority.config_sha256,ground_neural_policy:MIXED_PROTOCOL.neural_policy},
      intervals:this.intervals,handoffs:this.handoffs,metrics:this.metrics(),termination:this.termination,failure:this.failure});
  }
}
export function runMixedGroundFlight(authority:NeuralArtifact) {
  const s=new MixedGroundFlightSession(authority);s.start();while(s.status==='running'){try{s.advance();}catch{break;}}return s.result();
}
export const mixedGroundFlightHash=(value:ReturnType<MixedGroundFlightSession['result']>)=>flightHash(value);

export function runSustainedMixedGroundFlight(authority:NeuralArtifact) {
  const s=new MixedGroundFlightSession(authority,true);s.start();while(s.status==='running'){try{s.advance();}catch{break;}}
  const result=s.result(), m=result.metrics;
  const episodes='episodes' in m?m.episodes:[];
  return {...result,acceptance:{passed:result.termination==='DURATION_WINDOW_COMPLETED' &&
    episodes.filter(e=>e.type==='ground'&&e.complete&&e.duration_s>=1-1e-10&&e.distance_units>=.15).length>=2 &&
    ('takeoff_count' in m && m.takeoff_count>=3) && m.accepted_bound_violations===0 && m.invalid_command_count===0 && m.maximum_handoff_position_discontinuity===0}};
}
