import { AppHeader } from "@/components/AppHeader";
import { StateMessage } from "@/components/StateMessage";
import { requestJson } from "@/lib/neuroflyClient";
import { parseScenarioCatalog } from "@/lib/scenarioPlayback";
import { ScenarioCard } from "@/components/ScenarioCard";

export const dynamic = "force-dynamic";
export default async function ScenariosPage() {
  let scenarios;
  try { scenarios = await requestJson("/api/v1/scenarios", parseScenarioCatalog); }
  catch (error) { return <div className="app-shell"><AppHeader /><main className="main-content">
    <StateMessage eyebrow="SCENARIO API UNAVAILABLE" title="Scenarios could not load." detail={error instanceof Error ? error.message : "Please check the backend."} tone="error" />
  </main></div>; }
  return <div className="app-shell"><AppHeader /><main className="scenario-route">
    <p className="eyebrow">NEUROFLY / SCIENTIFIC SCENARIOS</p>
    <div className="library-heading"><div><h1>Experiments, not predictions.</h1><p className="scenario-intro">Five bounded windows into connectome-based models.<br/>Explicit inputs. Frozen scientific results. Deterministic replay.</p></div><span className="library-count">05 <small>CANONICAL EXPERIMENTS</small></span></div>
    <div className="scenario-catalog">{scenarios.map((scenario,index)=><ScenarioCard key={scenario.id} scenario={scenario} index={index}/>)}</div>
    <p className="subtle-note">Five executable presets: control, circuit micro-window, exploratory world experiment, neural-only horizontal motion and exploratory course control. Broader strategic worlds remain future work.</p>
  </main></div>;
}
