import { isCoursePlayback, isNeuralPlayback, type ScenarioPlayback } from "@/lib/scenarioPlayback";
import { scenarioNarrative } from "@/lib/scenarioPresentation";
import { EvidenceGrammar, signed } from "./ScientificInstrument";

/** Whole-run interpretation is separated from the selected authoritative boundary. */
export function CurrentResult({result,step}:{result:ScenarioPlayback;step:number}) {
  const frame=result.frames[step];
  let title:string, outcome:string, boundary:string, limitation:string, model:string;
  if(isCoursePlayback(result)) {
    const current=result.frames[step];
    title="Counter-motion. Residual orientation.";
    outcome=`An external perturbation initiates neural-mediated counter-rotation and small decaying reversals. Orientation settles at a nonzero residual offset: ${signed(result.summary.final_orientation_eq,9)} yaw_orientation_eq.`;
    boundary=`Model-space orientation ${signed(current.yaw_orientation_eq,9)}. ${step===0 ? "External perturbation follows boundary zero." : step===result.frames.length-1 ? "Final residual offset preserved." : "Feedback evolution; motion-related modes decay."}`;
    limitation="The model senses visual-motion changes, not absolute heading error. No translation; not a biological behavior prediction.";
    model="Exploratory orientation integrator + geometric observation. MARGINAL ORIENTATION MODE: no heading-error signal exists.";
  } else if(isNeuralPlayback(result)) {
    const current=result.frames[step];
    title="A neural response, not a body action.";
    outcome="The right-side descriptor produces side-specific HS source responses and a bilateral DNp15 readout. The left side remains neutral in this canonical condition.";
    boundary=`DNp15 R ${signed(current.dnp15_states[0])} / L ${signed(current.dnp15_states[1])}. ${current.bilateral_differential > 0 ? "The model currently produces a larger right DNp15 proxy state." : current.bilateral_differential < 0 ? "The model currently produces a larger left DNp15 proxy state." : "The bilateral diagnostic is currently neutral."}`;
    limitation="R−L is a model diagnostic only. No body mapping is defined. Continuous states; event semantics not defined.";
    model="Signed HS proxy dynamics and frozen mean-of-three transfer; uncalibrated DNp15 continuous states.";
  } else {
    const current=result.frames[step], story=scenarioNarrative(result,current);
    title=story.baseline ? "Expected neutral control state." : result.statuses.body_movement_occurred ? "Movement recorded in the model." : result.total_dnp01_spikes===0 ? "DNp01 remains subthreshold." : "DNp01 model events recorded.";
    const first=result.frames[0], last=result.frames[result.frames.length-1];
    outcome=result.scenario.id==="LOOMING_WORLD_EXPERIMENT" ? `Visual exposure changes from ${first.active_sensory_body_count} to ${last.active_sensory_body_count} bodies. DNp01 R changes from ${signed(first.dnp01_membrane_mv[0],3)} to ${signed(last.dnp01_membrane_mv[0],3)} mV_eq. ${story.summary}` : story.summary;
    boundary=`DNp01 R ${signed(current.dnp01_membrane_mv[0],3)} / L ${signed(current.dnp01_membrane_mv[1],3)} mV_eq. ${story.baseline ? "Stimulus disabled." : `${current.active_sensory_body_count} sensory bodies exposed.`}`;
    limitation=story.baseline ? "A control, not a broken simulation. Neutral sources do not imply a zero membrane coordinate." : "No biological escape prediction. Body output is the recorded model result, never a scripted visual response.";
    model="Exploratory sensory projection, transfer and membrane dynamics; uncalibrated model-space coordinates.";
  }
  return <aside className="current-result" aria-label="Current scientific result">
    <div className="result-heading"><span className="instrument-index">RESULT</span><span className="authority-status">Replay verified</span></div>
    <h2>{title}</h2><section className="canonical-outcome"><h3>Whole canonical run</h3><p>{outcome}</p></section>
    <section className="selected-outcome"><h3>{!isNeuralPlayback(result) && !isCoursePlayback(result) && result.termination?.status === "TERMINATED_GEOMETRY_DOMAIN" ? "STOPPED · GEOMETRY DOMAIN" : step===result.frames.length-1 ? "FINAL BOUNDARY · RUN COMPLETE" : "Selected boundary"} <span>{frame.time_ms.toFixed(1)} ms</span></h3><p>{boundary}</p></section>
    <p className="result-limitation">{limitation}</p>
    <EvidenceGrammar data={isCoursePlayback(result) ? "MaleCNS selected chemical routes + evidence-supported qualitative DNp15/course relationship; no physical gain." : isNeuralPlayback(result) ? "MaleCNS selected HS→DNp15 chemical routes; counts are structural only." : "MaleCNS LC4 / LPLC2 → DNp01 structural routing."} model={model}/>
  </aside>;
}
