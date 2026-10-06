"use client";

import { Canvas } from "@react-three/fiber";
import { Component, type ReactNode } from "react";
import { courseScene, type CoursePlaybackResult } from "@/lib/courseControlPlayback";
import { ScenarioFlyVisual } from "./ScenarioFlyVisual";

class PresentationBoundary extends Component<{children: ReactNode},{failed: boolean}> {
  state={failed:false};
  static getDerivedStateFromError(){return {failed:true};}
  render(){return this.state.failed ? <p role="alert">3D presentation unavailable. Authoritative orientation telemetry remains below.</p> : this.props.children;}
}
const assetStatus = () => {}; // Loading a specimen does not alter scientific state.

/** No client integrator, observation operator or autonomous animation loop. */
export default function CourseControlWorld({result,cursor}:{result:CoursePlaybackResult;cursor:number}) {
  const {frame,renderRotation,relativeView}=courseScene(result,cursor);
  return <div className="scenario-world course-world" aria-label="Exploratory model-space orientation presentation">
    <PresentationBoundary><Canvas frameloop="demand" dpr={[1,1.5]} camera={{position:[0,8,7],fov:48}} fallback={<p>WebGL unavailable; authoritative orientation and neural telemetry remain below.</p>}>
      <color attach="background" args={["#101e28"]}/>
      <ambientLight intensity={1.4}/><directionalLight position={[3,8,4]} intensity={3}/>
      <gridHelper args={[12,12,"#4e6e6d","#253b43"]}/>
      {/* World-fixed +Z reference. Not a target or heading-error signal. */}
      <group rotation={[0,result.world_reference.heading_eq*2*Math.PI,0]}>
        <mesh position={[0,.025,2.5]}><boxGeometry args={[.025,.025,5]}/><meshBasicMaterial color="#a4c3ba"/></mesh>
        <mesh position={[0,.06,3.6]} rotation={[-Math.PI/2,0,0]}><coneGeometry args={[.18,.55,3]}/><meshBasicMaterial color="#a4c3ba"/></mesh>
      </group>
      {/* Fixed position; one abstract cycle = 2π render radians, no amplification. */}
      <group rotation={[0,renderRotation,0]}>
        <ScenarioFlyVisual onStatusChange={assetStatus}/>
        <mesh position={[0,.04,1.4]}><boxGeometry args={[.06,.02,2.8]}/><meshBasicMaterial color="#d9c199"/></mesh>
      </group>
      {/* A body/view-frame stripe inset illustrating authoritative relative view. */}
      <group position={[0,.7,-3]}>
        {Array.from({length:15},(_,i)=><mesh key={i} position={[((i*.3+relativeView*4.5)%4.5+4.5)%4.5-2.25,0,0]}>
          <boxGeometry args={[.045,1,.015]}/><meshBasicMaterial color="#4b7478"/>
        </mesh>)}
      </group>
    </Canvas></PresentationBoundary>
    <div className="scene-title"><span className="eyebrow">WORLD / VIEW → NEURAL CIRCUIT → ORIENTATION → NEXT VIEW</span><p>A delayed model-space loop. Fixed position; orientation only.</p></div>
    <div className="course-reference-label">World-fixed reference · not a goal direction</div>
    <div className="course-orientation-label"><span>Model-space orientation</span><strong>{frame.yaw_orientation_eq.toFixed(9)} yaw_orientation_eq</strong><small>{frame.step===0 ? "External perturbation follows boundary zero" : frame.step===500 ? "Residual offset preserved · experiment complete" : "Counter-motion / delayed feedback evolution"}</small></div>
    <div className="course-world-note">Specimen = visual asset, not biomechanics. Direct cycle-to-angle presentation; no magnification. Stripes are not retinal imagery.</div>
  </div>;
}
