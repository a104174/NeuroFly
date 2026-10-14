import { type LocomotionReplay, type LocomotionRun, locomotionBounds } from "./experimentalLocomotion";
export const NEURAL_LOCOMOTION_URL = "/experiments/experimental_locomotion_v1.json";
export const NEURAL_LOCOMOTION_SHA256 = "17d335358a4f5cf4ed98b9682b103a81419cf82504203ce1bc72a7d76285d748";
type Policy = { experiment_id: string; schema_version: string; body_dt_ms: number; neural_dt_ms: number; neural_substeps_per_interval: number; duration_s: number; steering_gain_rad_per_orientation_eq: number; max_abs_angular_velocity_rad_s: number; landmark_x: number[]; conditions: { id: string; neural: boolean; apply: boolean; plane_z: number }[]; random_policy: string };
export type NeuralArtifact = { schema: string; config: { body: LocomotionReplay["config"]; policy: Policy; policy_sha256: string; dataset: string; dataset_uuid: string; model_mode: string; v0_artifact_id: string; v0_raw_sha256: string; source_sha256: Record<string, string>; sources: { neural: { dt_ms: number; source_identities: {body_id: number}[]; target_identities: {body_id: number}[] }; yaw: { orientation_model: { normalization_horizon_ms: number } } } }; result: { runs: LocomotionRun[]; causal_metrics: Record<string, number | boolean> }; artifact_id: string; config_sha256: string; result_sha256: string };
const close = (a: number, b: number) => Number.isFinite(a) && Number.isFinite(b) && Math.abs(a - b) < 1e-10;
const fail = () => { throw new Error("Replay neural incompatível ou corrompido. Nenhum steering de substituição foi criado."); };
const finite = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);

/** Recorded Python dynamics only. This checks timing, causal equations and scene bounds;
 * it never executes HS/DNp15 or makes browser motor decisions. */
export function parseNeuralLocomotion(value: unknown): NeuralArtifact {
  try {
    const a = value as NeuralArtifact, c = a.config.body, p = a.config.policy;
    if (a.schema !== "experimental_neural_locomotion_replay_v1" || p.schema_version !== a.schema || p.experiment_id !== "EXPERIMENTAL_LOCOMOTION_V1" || a.config.dataset !== "male-cns:v1.0" || a.config.dataset_uuid !== "4b2087c0fbe046bfaf0d60bc970e3e5d" || a.config.model_mode !== "CONNECTOME_INFORMED_NEURAL_STEERING" || p.random_policy !== "NONE") fail();
    if (p.body_dt_ms !== 20 || p.neural_dt_ms !== .1 || p.neural_substeps_per_interval !== 200 || p.duration_s !== 8 || p.steering_gain_rad_per_orientation_eq !== 2.5 || p.max_abs_angular_velocity_rad_s !== .5 || JSON.stringify(p.landmark_x) !== "[0.6,-0.6]") fail();
    if (a.config.policy_sha256 !== "760328e025b4256dc2bbb2fe5e680d0a80f56d8f83e1bda774c84696b49812ef" || a.config.v0_artifact_id !== "c33154916a33f3c88ba9d7421e0337e74b6def01eff674483427d4a0e8c64509" || a.config.v0_raw_sha256 !== "fc6d9882af59e63b4000d2426cc954342ce810ac2094f1e90f92d2d26cf2f893") fail();
    if (JSON.stringify(a.config.sources.neural.source_identities.map(n => n.body_id)) !== "[10015,10016,10023,10034,10181,10419]" || JSON.stringify(a.config.sources.neural.target_identities.map(n => n.body_id)) !== "[11215,12069]" || a.config.sources.neural.dt_ms !== .1 || a.config.sources.yaw.orientation_model.normalization_horizon_ms !== 50) fail();
    if (a.result.runs.length !== 4 || p.conditions.length !== 4 || ![a.artifact_id, a.config_sha256, a.result_sha256, ...Object.values(a.config.source_sha256)].every(h => /^[a-f0-9]{64}$/.test(h))) fail();
    const [lx,lz] = locomotionBounds(c);
    const ids=["ENGINEERING_BASELINE","NEURAL_STEERING","NEURAL_OUTPUT_DISABLED","VISUAL_PLANE_INTERVENTION"];
    const neuralFlags=[false,true,true,true], applyFlags=[false,true,false,true];
    a.result.runs.forEach((run,index)=>{
      const condition=p.conditions[index];
      if (run.id!==ids[index] || condition.id!==run.id || condition.neural!==neuralFlags[index] || condition.apply!==applyFlags[index] || condition.plane_z!==(index===3?-.4:.4) || JSON.stringify(run.condition)!==JSON.stringify(condition) || run.speed!==.18 || run.frames.length!==401 || run.neural_substeps!==(condition.neural?80000:0) || run.termination_reason!=="DURATION_COMPLETED") fail();
      let distance=0;
      const events: LocomotionRun["contact_events"]=[];
      run.frames.forEach((f,n)=>{
        if(f.step!==n || !close(f.time,n*.02) || !f.position.every(finite) || !finite(f.orientation) || !finite(f.angular_velocity) || !finite(f.distance) || f.position.length!==3 || f.propulsion_model_value!==.18 || f.steering_applied!==condition.apply || typeof f.steering_clipped!=="boolean" || f.model_mode!==(condition.apply?"CONNECTOME_INFORMED_NEURAL_STEERING":"EXPERIMENTAL_KINEMATIC_ONLY")) fail();
        const prev=run.frames[n-1];
        const expected=prev?[Math.max(-lx,Math.min(lx,prev.position[0]+prev.linear_velocity[0]*.02)),c.initial_position[1],Math.max(-lz,Math.min(lz,prev.position[2]+prev.linear_velocity[2]*.02))]:c.initial_position;
        if(!f.position.every((v,i)=>close(v,expected[i])) || Math.abs(f.position[0])>lx+1e-12 || Math.abs(f.position[2])>lz+1e-12 || !close(f.orientation,prev?prev.orientation+prev.angular_velocity*.02:c.initial_heading_rad))fail();
        const vx=.18*Math.sin(f.orientation), vz=.18*Math.cos(f.orientation);
        const contact=prev?.contact ?? ((f.position[0]>=lx&&vx>0)||(f.position[0]<=-lx&&vx<0)?"X_WALL":(f.position[2]>=lz&&vz>0)||(f.position[2]<=-lz&&vz<0)?"Z_WALL":null);
        const velocity=contact?[0,0,0]:[vx,0,vz];
        if(f.contact!==contact || f.linear_velocity.length!==3 || !f.linear_velocity.every((v,i)=>close(v,velocity[i])))fail();
        if(contact&&!prev?.contact)events.push({step:n,time:f.time,wall:contact});
        if(prev)distance+=Math.hypot(f.position[0]-prev.position[0],f.position[2]-prev.position[2]);
        if(!close(f.distance,distance))fail();
        if(n===0){if(f.sensory_summary!==null)fail();}else{
          const s=f.sensory_summary;
          if(!s || s.available_step!==n || s.before_step!==n-1 || !close(s.interval_ms,20) || s.pose_origin!=="PYTHON_COMPUTED_BODY_POSE_NOT_PRESCRIBED_TRAJECTORY" || !close(s.heading_increment_eq,(f.orientation-prev.orientation)/(2*Math.PI)))fail();
          p.landmark_x.forEach((x,i)=>{
            const bx=x-prev.position[0],bz=condition.plane_z-prev.position[2],ax=x-f.position[0],az=condition.plane_z-f.position[2];
            const shift=Math.atan2(bz*ax-bx*az,bx*ax+bz*az);
            const raw=50*((shift/(2*Math.PI)-s!.heading_increment_eq)/s!.interval_ms)*(i===0?1:-1);
            if(!close(s!.bearing_shift_rad[i],shift)||!close(s!.raw_normalized[i],raw)||!close(i===0?s!.right:s!.left,Math.max(-1,Math.min(1,raw)))||s!.clipped[i] !== (raw>1||raw< -1))fail();
          });
        }
        if(condition.neural){
          const ns=f.neural_summary;
          if(!ns || ns.hs_states.length!==6 || ns.dnp15_states.length!==2 || ![...ns.hs_states,...ns.dnp15_states].every(v=>finite(v)&&Math.abs(v)<=1) || ns.substeps!==(n===400?0:200))fail();
          if(n===400){if(ns!.mean_yaw_drive_eq!==null||ns!.orientation_increment_eq!==null||f.angular_velocity!==0)fail();}
          else{
            if(!finite(ns!.mean_yaw_drive_eq)||!finite(ns!.orientation_increment_eq)||!close(ns!.orientation_increment_eq!,ns!.mean_yaw_drive_eq!*.4))fail();
            const raw=2.5*ns!.orientation_increment_eq!/.02, bounded=Math.max(-.5,Math.min(.5,raw));
            if(!close(f.angular_velocity,condition.apply?bounded:0)||f.steering_clipped!==(raw!==bounded))fail();
          }
        }else if(f.neural_summary!==null||f.angular_velocity!==0)fail();
        if(f.steering_model_value!==f.angular_velocity)fail();
      });
      if(!close(run.distance,distance)||JSON.stringify(events)!==JSON.stringify(run.contact_events.map(e=>({step:e.step,time:e.time,wall:e.wall}))))fail();
    });
    return a;
  }catch{return fail();}
}

export async function loadNeuralLocomotion(fetcher: typeof fetch = fetch): Promise<{replay: LocomotionReplay; authority: NeuralArtifact}> {
  const r=await fetcher(NEURAL_LOCOMOTION_URL);if(!r.ok)throw Error(`Replay neural indisponível (HTTP ${r.status}).`);
  const bytes=await r.arrayBuffer();const hash=Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",bytes)),v=>v.toString(16).padStart(2,"0")).join("");if(hash!==NEURAL_LOCOMOTION_SHA256)fail();
  const authority=parseNeuralLocomotion(JSON.parse(new TextDecoder().decode(bytes)));
  return {authority,replay:{...authority,config:authority.config.body}};
}
