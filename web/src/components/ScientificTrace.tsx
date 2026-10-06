"use client";

import { memo, useMemo } from "react";
import type { CoursePlaybackResult } from "@/lib/courseControlPlayback";
import { signed } from "./ScientificInstrument";

/** Chart coordinates are a labelled display scale, never specimen amplification.
 * Every sample comes from the backend; no integration or derived model state. */
export const ScientificTrace = memo(function ScientificTrace({result,step}:{result:CoursePlaybackResult;step:number}) {
  const plot=useMemo(()=>{
    const values=result.frames.map(f=>f.yaw_orientation_eq);
    const lo=Math.min(0,...values),hi=Math.max(...values),range=hi-lo || 1;
    const x=(time:number)=>36+time/result.duration_ms*480;
    const y=(value:number)=>108-(value-lo)/range*78;
    return {x,y,lo,hi,points:result.frames.map(f=>`${x(f.time_ms).toFixed(2)},${y(f.yaw_orientation_eq).toFixed(2)}`).join(" ")};
  },[result]);
  const selected=result.frames[step];
  return <figure className="scientific-trace" aria-label="Authoritative model-space orientation trace">
    <figcaption><span>Orientation trace <code>yaw_orientation_eq</code></span><small>Backend boundaries · chart scale only</small></figcaption>
    <svg viewBox="0 0 552 148" role="img" aria-label={`Orientation over ${result.duration_ms} ms; selected ${selected.time_ms.toFixed(1)} ms, ${signed(selected.yaw_orientation_eq,9)}; final residual ${signed(result.summary.final_orientation_eq,9)}. Specimen rotation is not amplified.`}>
      <line className="trace-zero" x1="36" x2="516" y1={plot.y(0)} y2={plot.y(0)}/>
      <text x="4" y={plot.y(0)+4}>0</text><text x="36" y="16">{signed(plot.hi,6)}</text>
      <polyline className="trace-line" points={plot.points}/>
      <line className="trace-selection" x1={plot.x(selected.time_ms)} x2={plot.x(selected.time_ms)} y1="25" y2="112"/>
      <circle className="trace-point" cx={plot.x(selected.time_ms)} cy={plot.y(selected.yaw_orientation_eq)} r="4"/>
      <text x="36" y="138">0 ms · perturbation</text><text x="516" y="138" textAnchor="end">{result.duration_ms} ms · residual offset</text>
    </svg><p>Final residual <strong>{signed(result.summary.final_orientation_eq,9)}</strong> · zero is an orientation reference, not a sensed target heading.</p>
  </figure>;
});
