/** Downstream visual kinematics only. Never writes scientific pose or telemetry. */
import {Bone,BufferAttribute,Mesh,Object3D,Quaternion,Skeleton,SkinnedMesh,Vector3} from 'three';
import rig from '@/assets/fly_gait_v6.json';
export const GAIT=rig;
export function validateGaitRig(value:unknown=GAIT){const r=value as typeof GAIT;if(!r||r.schema!=='engineering_fly_gait_rig_v6'||r.legs.length!==6||new Set(r.legs.map(l=>l.id)).size!==6||r.legs.some(l=>l.pivots.length!==4||l.pivots.some(p=>p.length!==3||!p.every(Number.isFinite))||![0,1].includes(l.tripod)))throw new Error('Invalid six-leg visual rig');for(const [k,v] of Object.entries(r.animation))if(!Number.isFinite(v)||v<=0)throw new Error('Invalid gait parameter '+k);if(r.animation.stance_fraction>=1||r.animation.reach_fraction>=1||r.animation.swing_height>.03||r.animation.stride>.1)throw new Error('Unsafe gait bounds');return r;}
validateGaitRig();
export type BodySample={time:number;position:readonly number[];heading:number};
export type GaitMotion={frames:readonly {time:number;position:readonly number[];orientation:number}[];end:BodySample;time:number};
export type FootState={phase:number;foot:number[];from:number[];to:number[];swingStart?:number};
export type GaitState={body:BodySample;cycle:number;moving:boolean;feet:FootState[]};
const vec=(p:readonly number[])=>new Vector3(p[0],p[1],p[2]);
const smooth=(t:number)=>t*t*(3-2*t);
const nominal=(i:number,b:BodySample)=>vec(GAIT.legs[i].pivots[3]).sub(vec(GAIT.anchor)).multiplyScalar(.3).applyAxisAngle(new Vector3(0,1,0),b.heading).add(vec(b.position)).setY(GAIT.animation.floor_y);
export function bodySamples(m:GaitMotion):BodySample[]{if(m.frames.length!==Math.round(m.end.time/.02)||Math.abs(m.end.time-m.frames.length*.02)>1e-8||m.frames.length&&m.frames[0].time!==0)throw new Error('Incomplete presentation body history');return [...m.frames.map(f=>({time:f.time,position:f.position,heading:f.orientation})),m.end];}
export function gaitHistory(samples:readonly BodySample[],previous:readonly GaitState[]=[]):GaitState[]{
 if(!samples.length)return [];
 for(let i=0;i<samples.length;i++){const b=samples[i];if(b.position.length!==3||![b.time,b.heading,...b.position].every(Number.isFinite)||i&&Math.abs(b.time-samples[i-1].time-.02)>1e-8)throw new Error('Invalid gait body history');}
 let reusable=0;while(reusable<Math.min(samples.length,previous.length)){const a=samples[reusable],b=previous[reusable].body;if(a.time!==b.time||a.heading!==b.heading||a.position.some((v,i)=>v!==b.position[i]))break;reusable++;}
 const first=samples[0],states:GaitState[]=reusable?previous.slice(0,reusable):[{body:first,cycle:0,moving:false,feet:GAIT.legs.map((l,i)=>{const p=nominal(i,first).toArray();return {phase:(l.tripod*.5+GAIT.animation.stance_fraction*.5)%1,foot:p,from:p,to:p};})}];
 for(let n=Math.max(1,states.length);n<samples.length;n++){
  const b=samples[n],prev=states[n-1],dt=b.time-prev.body.time,delta=vec(b.position).sub(vec(prev.body.position)),yaw=b.heading-prev.body.heading,travel=Math.hypot(delta.x,delta.z)+Math.abs(yaw)*GAIT.animation.turn_radius,moving=travel>GAIT.animation.motion_threshold,cycle=prev.cycle+(moving?travel/GAIT.animation.stride:0);
  const feet=GAIT.legs.map((l,i)=>{const old=prev.feet[i],phase=(cycle+l.tripod*.5+GAIT.animation.stance_fraction*.5)%1,was=(prev.cycle+l.tripod*.5+GAIT.animation.stance_fraction*.5)%1,foot=vec(old.foot);let from=vec(old.from),to=vec(old.to),swingStart=old.swingStart??GAIT.animation.stance_fraction;
   if(!moving){const target=nominal(i,b);foot.lerp(target,1-Math.exp(-dt/GAIT.animation.settle_s));if(foot.y-GAIT.animation.floor_y<1e-5)foot.y=GAIT.animation.floor_y;return {phase:old.phase,foot:foot.toArray(),from:foot.toArray(),to:foot.toArray()};}
   if(phase>=GAIT.animation.stance_fraction&&(was<GAIT.animation.stance_fraction||!prev.moving)){
    swingStart=prev.moving?GAIT.animation.stance_fraction:phase;from=foot.clone();const duration=GAIT.animation.stride/(travel/dt),lead=Math.min(.18,duration*(1-GAIT.animation.stance_fraction+.5*GAIT.animation.stance_fraction));const prediction={...b,position:vec(b.position).addScaledVector(delta,lead/dt).toArray(),heading:b.heading+yaw*lead/dt};to=nominal(i,prediction);
   }
   if(phase>=GAIT.animation.stance_fraction){const t=(phase-swingStart)/(1-swingStart);foot.copy(from).lerp(to,smooth(t));foot.y=GAIT.animation.floor_y+GAIT.animation.swing_height*Math.sin(Math.PI*t)**2;}
   else if(was>=GAIT.animation.stance_fraction)foot.copy(to);
   return {phase,foot:foot.toArray(),from:from.toArray(),to:to.toArray(),swingStart};
  });states.push({body:b,cycle,moving,feet});
 }
 return states;
}
const presentationCaches=new WeakMap<object,GaitState[]>();
/** Append-only presentation cache; validate every reused pose, never mutate old states. */
export function presentationGaitHistory(m:GaitMotion){const key=m.frames[0]??m.end.position,result=gaitHistory(bodySamples(m),presentationCaches.get(key));presentationCaches.set(key,result);return result;}
export function gaitAt(states:readonly GaitState[],time:number):GaitState{
 if(!states.length||!Number.isFinite(time)||time<states[0].body.time-1e-8||time>states.at(-1)!.body.time+1e-8)throw new Error('Gait cursor outside body history');
 const index=Math.min(states.length-1,Math.floor((time-states[0].body.time)/.02+1e-9)),a=states[index],b=states[Math.min(index+1,states.length-1)],t=Math.min(1,Math.max(0,(time-a.body.time)/.02));return {...a,body:{time,position:vec(a.body.position).lerp(vec(b.body.position),t).toArray(),heading:a.body.heading+(b.body.heading-a.body.heading)*t},feet:a.feet.map((f,i)=>({...f,foot:vec(f.foot).lerp(vec(b.feet[i].foot),t).toArray()}))};
}
/** Two-link IK + a rigid visual foot. Reach clamping is reported, never moves body. */
export function legJoints(index:number,worldFoot:readonly number[],body:BodySample){
 const p=GAIT.legs[index].pivots.map(vec),foot=vec(worldFoot).sub(vec(body.position)).applyAxisAngle(new Vector3(0,1,0),-body.heading).multiplyScalar(1/.3).add(vec(GAIT.anchor)),toe=p[3].clone().sub(p[2]),target=foot.clone().sub(toe),a=p[0],l1=p[1].distanceTo(a),l2=p[2].distanceTo(p[1]),d=target.distanceTo(a),reach=Math.min((l1+l2)*GAIT.animation.reach_fraction,Math.max(Math.sqrt(l1*l1+l2*l2+2*l1*l2*Math.cos(GAIT.animation.max_knee_bend_rad)),d)),axis=target.clone().sub(a).normalize();
 if(!d||!Number.isFinite(d))throw new Error('Degenerate gait target');
 const pole=p[1].clone().sub(a);pole.addScaledVector(axis,-pole.dot(axis));if(pole.lengthSq()<1e-12)pole.set(index<3?-1:1,0,0).addScaledVector(axis,-pole.dot(axis));pole.normalize();
 const along=(l1*l1-l2*l2+reach*reach)/(2*reach),knee=a.clone().addScaledVector(axis,along).addScaledVector(pole,Math.sqrt(Math.max(0,l1*l1-along*along))),ankle=a.clone().addScaledVector(axis,reach);
 let clamped=Math.abs(reach-d)>1e-8;const restHip=p[1].clone().sub(a).normalize(),hip=knee.clone().sub(a).normalize(),angle=restHip.angleTo(hip);if(angle>GAIT.animation.max_hip_deviation_rad){const q=new Quaternion().setFromUnitVectors(restHip,hip);q.slerp(new Quaternion(),1-GAIT.animation.max_hip_deviation_rad/angle);knee.copy(a).addScaledVector(restHip.applyQuaternion(q),l1);ankle.copy(knee).addScaledVector(target.clone().sub(knee).normalize(),l2);clamped=true;}
 const proximal=knee.clone().sub(a).normalize(),distal=ankle.clone().sub(knee).normalize(),bend=proximal.angleTo(distal);if(bend>GAIT.animation.max_knee_bend_rad){const q=new Quaternion().setFromUnitVectors(proximal,distal);q.slerp(new Quaternion(),1-GAIT.animation.max_knee_bend_rad/bend);ankle.copy(knee).addScaledVector(proximal.applyQuaternion(q),l2);clamped=true;}
 return {points:[a,knee,ankle,ankle.clone().add(toe)],clamped};
}
function nearest(p:Vector3,a:Vector3,b:Vector3){const ab=b.clone().sub(a),t=Math.max(0,Math.min(1,p.clone().sub(a).dot(ab)/ab.lengthSq()));return {distance:p.distanceTo(a.clone().addScaledVector(ab,t)),t};}
/** Skin existing source surfaces and their assigned bristles, no extra limbs. */
export function articulateFly(scene:Object3D,identities:Map<string,Object3D>){
 const root=identities.get('FlyV2B.GeometryRoot');if(!root)throw new Error('Missing gait root');
 validateGaitRig();for(const leg of GAIT.legs)for(const name of [leg.id,...leg.details]){const node=identities.get(name);if(!(node instanceof Mesh)||node instanceof SkinnedMesh||!root.getObjectById(node.id)||node.position.lengthSq()||node.scale.toArray().some(v=>v!==1)||node.quaternion.toArray().some((v,i)=>v!==(i===3?1:0)))throw new Error('Missing gait surface or incompatible transform '+name);}
 const geometries:Mesh['geometry'][]=[],skeletons:Skeleton[]=[],chains:Bone[][]=[],rest:Quaternion[][]=[];let meshes=0;
 GAIT.legs.forEach((leg,index)=>{
  const points=leg.pivots.map(vec),bones:Bone[]=[],qs:Quaternion[]=[];
  for(let j=0;j<3;j++){const b=new Bone();b.name=`Gait.${leg.id}.${['Hip','Distal','Foot'][j]}`;const q=new Quaternion().setFromUnitVectors(new Vector3(0,1,0),points[j+1].clone().sub(points[j]).normalize());qs.push(q);if(j){b.position.set(0,points[j].distanceTo(points[j-1]),0);b.quaternion.copy(qs[j-1].clone().invert().multiply(q));bones[j-1].add(b);}else{b.position.copy(points[0]);b.quaternion.copy(q);root.add(b);}bones.push(b);}
  scene.updateMatrixWorld(true);const skeleton=new Skeleton(bones);skeleton.calculateInverses();skeletons.push(skeleton);chains.push(bones);rest.push(qs);
  for(const name of [leg.id,...leg.details]){const node=identities.get(name);if(!(node instanceof Mesh)||node instanceof SkinnedMesh)throw new Error('Missing gait surface '+name);if(name===leg.id&&node.geometry.getAttribute('position').count!==leg.vertices)throw new Error('Gait geometry mismatch');
   const g=node.geometry.clone(),position=g.getAttribute('position'),indices=new Uint16Array(position.count*4),weights=new Float32Array(position.count*4);
   for(let k=0;k<position.count;k++){const p=new Vector3().fromBufferAttribute(position,k),dist=[0,1,2].map(j=>({...nearest(p,points[j],points[j+1]),j})).sort((a,b)=>a.distance-b.distance),best=dist[0],width=Math.min(.25,GAIT.animation.joint_blend_asset/points[best.j].distanceTo(points[best.j+1]));let bone=best.j,other=best.j,blend=0;if(best.t<width&&bone>0){other=bone-1;blend=.5*(1-best.t/width);}else if(best.t>1-width&&bone<2){other=bone+1;blend=.5*(best.t-(1-width))/width;}indices[k*4]=bone;indices[k*4+1]=other;weights[k*4]=1-blend;weights[k*4+1]=blend;}
   g.setAttribute('skinIndex',new BufferAttribute(indices,4));g.setAttribute('skinWeight',new BufferAttribute(weights,4));const skinned=new SkinnedMesh(g,node.material);skinned.name=node.name;skinned.castShadow=node.castShadow;skinned.receiveShadow=node.receiveShadow;skinned.frustumCulled=false;node.parent!.add(skinned);node.parent!.remove(node);skinned.bind(skeleton);identities.set(name,skinned);geometries.push(g);meshes++;
  }
 });
 return {meshes,bones:18,apply(state:GaitState,body:BodySample=state.body){let clamped=0;const feet:number[][]=[],joints:number[][][]=[];for(let i=0;i<6;i++){const solved=legJoints(i,state.feet[i].foot,body);if(solved.clamped)clamped++;const desired:Quaternion[]=[];for(let j=0;j<3;j++){const restDir=vec(GAIT.legs[i].pivots[j+1]).sub(vec(GAIT.legs[i].pivots[j])).normalize(),newDir=solved.points[j+1].clone().sub(solved.points[j]).normalize(),q=new Quaternion().setFromUnitVectors(restDir,newDir).multiply(rest[i][j]);desired.push(q);chains[i][j].quaternion.copy(j?desired[j-1].clone().invert().multiply(q):q);}joints.push(solved.points.map(p=>p.toArray()));feet.push(solved.points[3].clone().sub(vec(GAIT.anchor)).multiplyScalar(.3).applyAxisAngle(new Vector3(0,1,0),body.heading).add(vec(body.position)).toArray());}scene.updateWorldMatrix(true,true);const actualFeet=chains.map((bones,i)=>bones[2].localToWorld(new Vector3(0,vec(GAIT.legs[i].pivots[3]).distanceTo(vec(GAIT.legs[i].pivots[2])),0)).toArray());return {time:body.time,body:{position:[...body.position],heading:body.heading},feet,actualFeet,joints,clamped,cycle:state.cycle,moving:state.moving};},dispose(){geometries.forEach(g=>g.dispose());skeletons.forEach(s=>s.dispose());}};
}
