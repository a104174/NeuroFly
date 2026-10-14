"use client";
import { useEffect, useMemo } from "react";
import { BufferGeometry, Line as ThreeLine, LineDashedMaterial, Vector3 } from "three";
import type { comparisonOverview, comparisonScenes } from "@/lib/neuralSteeringComparison";
export type ArenaComparisonProps = {
  overview: ReturnType<typeof comparisonOverview>;
  states: ReturnType<typeof comparisonScenes>;
  time: number;
  focus?: string;
};
/** Rendering shape only; the historical B/C/D scientific contract stays intact. */
export type ArenaOverlayProps={overview:{tracks:{key:string;points:[number,number,number][];color:string;label:string;symbol:string;plane:number}[];landmarkX:number[]};states:{key:string;color:string;symbol:string;label:string;scene:ReturnType<typeof comparisonScenes>[number]['scene']}[];time:number;focus?:string};
function Trail({ points, color, index, time }: { points: [number,number,number][]; color:string; index:number; time:number }) {
  const line=useMemo(()=> {
    const result=new ThreeLine(new BufferGeometry().setFromPoints(points.map(p=>new Vector3(p[0], .003+index*.001, p[2]))),new LineDashedMaterial({color,transparent:true,opacity:.8,dashSize:index===0?10:index===1?.025:.008,gapSize:index===0?0:.012}));
    result.computeLineDistances(); return result;
  },[points,color,index]);
  useEffect(()=>()=>{line.geometry.dispose();line.material.dispose();},[line]);
  // Reveal only completed stored segments. The marker uses the interpolated pose.
  line.geometry.setDrawRange(0,Math.floor(time/.02)+1);
  return <primitive object={line} dispose={null}/>;
}
export function ArenaComparison({overview,states,time}:ArenaOverlayProps) {
  return <>
    {overview.tracks.map((track,index)=><Trail key={track.key} points={track.points} color={track.color} index={index} time={time}/>)}
    {states.map((s,index)=><group key={s.key} name={`ComparisonMarker${s.key}`} position={[s.scene.pose.anchor[0],.009+index*.002,s.scene.pose.anchor[2]]} rotation={[0,s.scene.pose.rotation,0]}>
      <mesh rotation={[-Math.PI/2,0,index===2?Math.PI/4:0]}>
        {index===0?<ringGeometry args={[.017,.025,24]}/>:<planeGeometry args={[.036,.036]}/>}
        <meshBasicMaterial color={s.color} transparent opacity={.85} depthWrite={false}/>
      </mesh>
      <mesh position={[0,0,.052]} rotation={[Math.PI/2,0,0]}><coneGeometry args={[.013,.032,3]}/><meshBasicMaterial color={s.color}/></mesh>
    </group>)}
    {overview.tracks.filter((t,i,a)=>a.findIndex(s=>s.plane===t.plane)===i).map((track,index)=><group key={track.plane}>{overview.landmarkX.map(x=><mesh key={x} position={[x,.006,track.plane]} rotation={[-Math.PI/2,0,0]}><ringGeometry args={[.015,.027,24]}/><meshBasicMaterial color={index===0?"#67d3e0":"#c6a8f5"} transparent opacity={.6}/></mesh>)}</group>)}
  </>;
}
