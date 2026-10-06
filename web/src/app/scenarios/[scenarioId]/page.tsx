import { notFound } from "next/navigation";
import { AppHeader } from "@/components/AppHeader";
import { ScenarioCockpit } from "@/components/ScenarioCockpit";
import { StateMessage } from "@/components/StateMessage";
import { requestJson } from "@/lib/neuroflyClient";
import { parseScenarioCatalog, SCENARIO_KINDS } from "@/lib/scenarioPlayback";
import { loadScenarioPlayback } from "@/app/scenarios/actions";
import { Suspense } from "react";
import Link from "next/link";
import { ScientificPlaybackLoading } from "@/components/ScientificInstrument";
import type { ScenarioDefinition } from "@/lib/scenarioPlayback";
import { experimentMetadata } from "@/lib/scenarioPresentation";

async function RestoredCockpit({scenario}:{scenario:ScenarioDefinition}) {
  const restored=await loadScenarioPlayback(scenario.id);
  return <ScenarioCockpit scenario={scenario} initialResult={"result" in restored ? restored.result : null} initialError={"error" in restored ? restored.error : null}/>;
}

export const dynamic = "force-dynamic";
export default async function ScenarioPage({ params, searchParams }: { params: Promise<{ scenarioId: string }>; searchParams: Promise<{ replay?: string }> }) {
  const { scenarioId } = await params;
  if (!SCENARIO_KINDS.some(id => id === scenarioId)) notFound();
  let definitions;
  try { definitions = await requestJson("/api/v1/scenarios", parseScenarioCatalog); }
  catch (error) { return <div className="app-shell"><AppHeader /><main className="main-content"><StateMessage eyebrow="SCENARIO UNAVAILABLE" title="The preset could not load." detail={error instanceof Error ? error.message : "Backend unavailable."} tone="error" /></main></div>; }
  const scenario = definitions.find(s => s.id === scenarioId);
  if (!scenario) notFound();
  const query = await searchParams;
  return <div className="app-shell"><AppHeader />{query.replay === "canonical" ? <Suspense fallback={<main className="scenario-route"><Link className="back-link" href="/scenarios">← All experiments</Link><header className="scenario-heading"><div><p className="eyebrow">{experimentMetadata[scenario.id].kind}</p><h1>{scenario.title}</h1><p>{experimentMetadata[scenario.id].purpose}</p></div></header><ScientificPlaybackLoading/></main>}><RestoredCockpit scenario={scenario}/></Suspense> : <ScenarioCockpit scenario={scenario}/>}</div>;
}
