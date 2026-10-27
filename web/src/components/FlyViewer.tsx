"use client";

import Link from "next/link";
import type { WingPose } from "@/lib/articulatedWings";
import { ARENA, ARENA_RESET_VIEW } from "@/lib/experimentalArena";
import dynamic from "next/dynamic";
import { useCallback, useMemo, useState, type ReactNode } from "react";
import type { ArenaOverlayProps } from "./ArenaComparison";
import type { ViewerStats } from "./FlyViewerCanvas";
import { FLY_VIEWER_ASSET, type FlyViewerView } from "@/lib/flyViewer";

import {presentationGaitHistory,gaitAt,type GaitMotion,type GaitState} from "@/lib/articulatedGait";

import {projectMotorGait,type MotorReference,type BridgeCondition} from "@/lib/motorGaitBridge";
import type { ViewerCameraView } from "./lab/explorePresentation";
import type { FlightTrajectoryDisplay } from "@/lib/flightTrajectory";

const FlyViewerCanvas = dynamic(() => import("./FlyViewerCanvas"), { ssr: false, loading: () => <p className="fly-viewer-message">Preparing the studio…</p> });
const views: { id: FlyViewerView; label: string }[] = [{ id: "three-quarter", label: "Overview" }, { id: "lateral", label: "Side" }, { id: "head", label: "Front" }, { id: "dorsal", label: "Top" }];
export function FlyViewer({ experience = false, initialGait = false, initialView = experience ? "explore" : "three-quarter", arena = false, replayPose, locomotion = false, locomotionVersion = "v0", stimulusPlane, stimulusX, stimulusIds, trajectory, liveTrajectory, comparison, playbackControls, scientificTimeline, gaitMotion, liveGaitState, motorBridge, presentationLabel, flightPresentation, flightTrajectory, flightDisclosure }: { experience?:boolean; initialGait?:boolean; initialView?:ViewerCameraView; flightDisclosure?:string; flightPresentation?:WingPose; flightTrajectory?:FlightTrajectoryDisplay; motorBridge?:{reference:MotorReference;condition:BridgeCondition}; presentationLabel?:string; gaitMotion?:GaitMotion; liveGaitState?:GaitState; arena?: boolean; locomotion?: boolean; locomotionVersion?: "v0" | "v1" | "v2" | "v3" | "v3.1" | "v4" | "v5" | "v5.1"; stimulusPlane?: number; stimulusX?: number[]; stimulusIds?: string[]; trajectory?: [number, number, number][]; liveTrajectory?: [number, number, number][]; comparison?: ArenaOverlayProps; playbackControls?: ReactNode; scientificTimeline?: ReactNode; replayPose?: import("@/lib/arenaCourseReplay").ArenaCoursePose }) {
  const [gait,setGait]=useState(initialGait);
  const gaitFrames=gaitMotion?.frames,endPosition=gaitMotion?.end.position,endTime=gaitMotion?.end.time,endHeading=gaitMotion?.end.heading;
  const gaitData=useMemo(()=>{try{return {states:gait&&gaitFrames&&endPosition&&endTime!==undefined&&endHeading!==undefined?presentationGaitHistory({frames:gaitFrames,end:{time:endTime,position:endPosition,heading:endHeading},time:endTime}):[],error:null};}catch(e){return {states:[],error:String(e)};}},[gait,gaitFrames,endPosition,endTime,endHeading]);
  const gaitStates=gaitData.states;
  const [gaitProblem,setGaitProblem]=useState<string|null>(null);
  const onGaitFailure=useCallback((message:string|null)=>setGaitProblem(message),[]);
  const baseGaitState=gait ? liveGaitState ?? (gaitStates.length&&gaitMotion?gaitAt(gaitStates,gaitMotion.time):undefined) : undefined;
  const gaitState=baseGaitState&&motorBridge?projectMotorGait(baseGaitState,motorBridge.reference,motorBridge.condition):baseGaitState;
  const [tableReady, setTableReady] = useState(false);
  const onTableReady = useCallback(() => setTableReady(true), []);
  const [view, setView] = useState<ViewerCameraView>(initialView);
  const [reset, setReset] = useState(0);
  const [status, setStatus] = useState<{ state: "loading" | "ready" | "error"; detail?: string }>({ state: "loading" });
  const [diagnostics, setDiagnostics] = useState(false);
  const [showLandmarks, setShowLandmarks] = useState(false);
  const [stats, setStats] = useState<ViewerStats | null>(null);
  const onStatus = useCallback((value: { state: "loading" | "ready" | "error"; detail?: string }) => setStatus(previous => previous.state === "error" ? previous : value), []);
  const onFailure = useCallback((detail: string) => setStatus({ state: "error", detail }), []);
  const provenance = FLY_VIEWER_ASSET.provenance;
  return <>
    <section className={`fly-viewer-stage${arena ? " arena-viewer-stage" : ""}${locomotion ? " locomotion-viewer-stage" : ""}`} aria-label={arena ? "Controlled chamber visual prototype" : "Interactive male Drosophila visual asset"}>
      <FlyViewerCanvas explore={experience} showLandmarks={!experience || showLandmarks} flightPresentation={flightPresentation} flightTrajectory={flightTrajectory} onGaitFailure={onGaitFailure} gaitState={gaitState} arena={arena} replayPose={arena ? replayPose : undefined} locomotion={locomotion} stimulusPlane={stimulusPlane} stimulusX={stimulusX} stimulusIds={stimulusIds} trajectory={trajectory} liveTrajectory={liveTrajectory} comparison={comparison} onTableReady={onTableReady} view={view} reset={reset} diagnostics={diagnostics} onStatus={onStatus} onStats={setStats} onFailure={onFailure} />
      <div className="fly-viewer-caption"><span>{experience?"A closer look at behaviour":"V2-F / MALE DROSOPHILA"}</span><small>{experience?"Drag to orbit · Pinch or scroll to zoom":presentationLabel??(arena ? locomotion ? locomotionVersion === "v5.1" ? "Visual stimulus P/Q / Reconstructed browser model" : locomotionVersion === "v5" ? comparison ? "Independent stimuli v5 / Recomputed counterfactual replay" : "Independent stimuli v5 / Live browser model" : locomotionVersion === "v4" ? comparison ? "Moving stimulus v4 / Recomputed counterfactual replay" : "Moving stimulus v4 / Live browser model" : locomotionVersion === "v3.1" ? "Neural ON/OFF / Recomputed counterfactual replay" : locomotionVersion === "v3" ? "Continuous v3 / Live neural + engineering navigation" : locomotionVersion === "v2" ? "Interactive v2 / Live browser model" : `Experimental Locomotion ${locomotionVersion} / Precomputed replay` : replayPose ? "A+C v0.2 / Course orientation replay" : "A+C v0.1 / Controlled chamber" : "Static visual specimen")}</small></div>
      {comparison ? <div className="comparison-stage-legend" aria-label="Comparison condition legend">{comparison.states.map(s=><span key={s.key} style={{color:s.color}}>{s.symbol} {s.key}{comparison.focus === s.key ? " · focus" : ""}</span>)}</div> : null}
      {playbackControls ? <div className="fly-viewer-playback">{playbackControls}</div> : null}
      {(status.state !== "ready" || (arena && !tableReady)) ? <div className="fly-viewer-message" role={status.state === "error" ? "alert" : "status"}>
        <strong>{status.state === "error" ? "The specimen could not be displayed." : arena ? "Preparing the chamber and specimen…" : "Loading the specimen…"}</strong>
        {status.detail ? <p>{status.detail}</p> : null}
        {status.state === "error" ? <button onClick={() => window.location.reload()}>Reload viewer</button> : null}
      </div> : null}
      {!experience?<div className="fly-viewer-toolbar" aria-label="Camera controls">
        <div className="fly-viewer-views">{(arena ? [...views, { id: "inspect" as const, label: "Inspect Fly" }] : views).map(item => <button key={item.id} aria-pressed={view === item.id} onClick={() => { setView(item.id); setReset(n => n + 1); }}>{item.label}</button>)}</div>
        <button onClick={() => { setView(ARENA_RESET_VIEW); setReset(n => n + 1); }} title="Return to the default overview">Reset view</button>
      </div>:null}
      {diagnostics && stats ? <output data-wings={JSON.stringify(stats.wings)} data-gait={JSON.stringify(stats.gait)} data-flight-trajectory-geometry={JSON.stringify(stats.flightTrajectoryGeometry)} data-render-stimulus={JSON.stringify(stats.stimulusPositions)} data-comparison-marker-positions={JSON.stringify(stats.comparisonMarkers)} data-render-body-yaw={stats.bodyYaw} data-render-body-position={JSON.stringify(stats.bodyPosition)} data-camera-position={JSON.stringify(stats.cameraPosition)} data-camera-target={JSON.stringify(stats.cameraTarget)} className="fly-viewer-stats" aria-label="Measured renderer statistics">{stats.fps.toFixed(0)} FPS (approx.) · {stats.calls} calls · {stats.triangles.toLocaleString()} rendered triangles<br />{stats.geometries} geometries · {stats.textures} textures · renderer counters, not GPU memory</output> : null}
    </section>
    {experience&&(gaitProblem||gaitData.error)?<p className="lab-error" role="alert">Leg animation unavailable: {gaitProblem??gaitData.error}. Original body presentation retained.</p>:null}
    {experience?<div className="lab-camera-bar"><label htmlFor="lab-camera">Camera <select id="lab-camera" value={view} onChange={e=>{setView(e.target.value as ViewerCameraView);setReset(n=>n+1);}}>{[{id:"explore",label:"Explore"},...views,{id:"inspect",label:"Inspect"}].map(item=><option key={item.id} value={item.id}>{item.label}</option>)}</select></label><button onClick={()=>{setView("explore");setReset(n=>n+1);}}>Reset view</button><span>Orbit, zoom, discover.</span></div>:null}
    {experience?<details className="lab-display-details"><summary>Display & credits</summary><div>{renderNotes()}</div></details>:renderNotes()}
  </>;
  function renderNotes(){return <>
    {experience?<div className="fly-viewer-notes"><label><input type="checkbox" checked={showLandmarks} onChange={e=>setShowLandmarks(e.target.checked)}/> Model landmarks (annotations)</label><p>Markers show the observer’s geometric reference points. Visibility does not change sensory inputs.</p></div>:null}
    {arena&&!flightPresentation?<div className="fly-viewer-notes"><label><input type="checkbox" checked={gait} disabled={!gaitMotion && !liveGaitState} onChange={e=>setGait(e.target.checked)}/> {experience?"Leg animation":"Articulated Gait v6"}</label><span> Engineering kinematic gait — not connectome-derived leg control{!gaitMotion && !liveGaitState?" · Sem histórico de movimento: apresentação original.":""}</span></div>:null}
    {!experience&&(gaitProblem||gaitData.error)?<p role="alert">Articulated gait unavailable: {gaitProblem??gaitData.error}. Original V2-F presentation retained.</p>:null}
    {scientificTimeline}
    <div className="fly-viewer-notes"><p>Drag to orbit · Scroll or pinch to zoom · Camera pivots around the visual thoracic anchor.{arena ? experience ? " Inspect moves the camera only. Reset returns to Explore." : " Inspect Fly moves the camera only. Reset returns to Overview." : ""}</p><label><input type="checkbox" checked={diagnostics} onChange={event => setDiagnostics(event.target.checked)} /> Render diagnostics</label></div>
    <p className="fly-viewer-notes"><Link href={arena ? "/visual-lab/fly" : "/visual-lab/arena"}>{arena ? "Inspect the specimen in the studio →" : "Explore the experimental chamber prototype →"}</Link></p>
    <footer className="fly-viewer-credits"><p><a href={provenance.source_url} target="_blank" rel="noreferrer">Wildtype Male Drosophila Melanogaster</a> by {provenance.author} · <a href={provenance.license_url} target="_blank" rel="noreferrer">CC BY 4.0</a> · Modified for NeuroFly.</p><p>A third-party visual representation, not MaleCNS-derived external anatomy. {flightDisclosure ?? (flightPresentation?.source === 'ENGINEERING_3D_FLIGHT_V8' ? "Engineering 3D kinematic flight integrated from declared inputs; wing and leg presentation only. No neural flight control, forces or aerodynamic validation." : flightPresentation ? "Engineering-only visual flight preview: original wing surfaces articulated with declared hinges. No neural wing control, aerodynamics or scientific airborne trajectory." : presentationLabel ? "Bounded precomputed Python motor-model response and body replay; engineering gait projection only. No live DNg100 computation or validated neuromuscular actuation." : locomotion ? (locomotionVersion === "v5.1" || locomotionVersion === "v3.1" || ((locomotionVersion === "v4" || locomotionVersion === "v5") && comparison)) ? "Counterfactual model trajectories recomputed locally from recorded events. Engineering propulsion and boundary recovery; computational steering intervention, not physiological ablation." : (locomotionVersion === "v2" || locomotionVersion === "v3" || locomotionVersion === "v4" || locomotionVersion === "v5") ? "Live local browser computation with engineering propulsion and HS/DNp15 proxy-model steering. No biological gait, muscle calibration or fully connectome-driven locomotion." : "Precomputed replay with engineering propulsion; v1 steering is a proxy-model contribution, not fully connectome-driven locomotion. No biological gait or muscle model." : arena && replayPose ? "Recorded abstract model orientation only; no biological locomotion or chamber interaction." : "No simulation or experimental replay runs here.")}</p>{arena ? <p>Environment: original NeuroFly acrylic enclosure and backdrop. <a href={ARENA.tableSource} target="_blank" rel="noreferrer">Lab Table</a> by zeeshanfareed · <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noreferrer">CC BY 4.0</a> · Uniformly fitted; decorative tabletop bottles omitted and material response adjusted for NeuroFly. Display scale is illustrative, not a biological measurement.</p> : null}</footer>
  </>;}
}
