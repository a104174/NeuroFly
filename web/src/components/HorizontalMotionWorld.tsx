"use client";

import { Canvas, useThree } from "@react-three/fiber";
import { Component, useEffect, type ReactNode } from "react";
import { OrthographicCamera } from "three";
import { neuralScene, type NeuralPlaybackResult } from "@/lib/scenarioPlayback";

class SceneBoundary extends Component<{children:ReactNode},{failed:boolean}> {
  state={failed:false};
  static getDerivedStateFromError(){return {failed:true};}
  render(){return this.state.failed ? <p role="alert">3D presentation unavailable. Authoritative neural telemetry remains below.</p> : this.props.children;}
}

function PresentationCamera() {
  const {camera,size,invalidate}=useThree();
  useEffect(()=>{
    if (!(camera instanceof OrthographicCamera)) return;
    // Three.js owns this imperative camera. Fit panels, never scientific state.
    // eslint-disable-next-line react-hooks/immutability
    camera.zoom=Math.min(size.width/7.5,size.height/4.5);
    camera.updateProjectionMatrix(); invalidate();
  },[camera,size.width,size.height,invalidate]);
  return null;
}

/** Stateless presentation panels. No fly/body, scientific encoder or frame loop. */
export default function HorizontalMotionWorld({result,cursor}:{result:NeuralPlaybackResult;cursor:number}) {
  const {frame,phase}=neuralScene(result,cursor);
  return <div className="scenario-world neural-world" aria-label="Horizontal motion descriptor presentation">
    <SceneBoundary><Canvas orthographic frameloop="demand" dpr={[1,1.5]} camera={{position:[0,0,10],zoom:50}} fallback={<p>WebGL unavailable; input and neural telemetry remain below.</p>}>
      <PresentationCamera/>
      <color attach="background" args={["#101e28"]} />
      {(["L","R"] as const).map(side=><group key={side} position={[side === "R" ? 1.65 : -1.65,0,0]}>
        <mesh><planeGeometry args={[2.9,2.2]}/><meshBasicMaterial color="#233d48"/></mesh>
        {Array.from({length:13},(_,i)=><mesh key={i} position={[((i*.24+(side === "R" ? phase : 0))%3.12)-1.56,0,.01]}>
          <planeGeometry args={[.085,2.2]}/><meshBasicMaterial color={frame.input_descriptor[side] !== 0 ? "#b9d7c7" : "#526872"}/>
        </mesh>)}
      </group>)}
    </Canvas></SceneBoundary>
    <div className="scene-title"><span className="eyebrow">CONTROLLED MOTION INPUT / NEURAL-ONLY</span><p>Stripes illustrate horizontal_motion_eq. Not calibrated retinal imagery.</p></div>
    <div className="neural-panel-labels"><span>L input {frame.input_descriptor.L.toFixed(3)}</span><span>R input {frame.input_descriptor.R.toFixed(3)} · {frame.input_descriptor.R !== 0 ? "Descriptor presented" : "Pulse off / neural recovery"}</span></div>
    <div className="neural-world-note">No body mapping is defined. This view contains no simulated body.</div>
  </div>;
}
