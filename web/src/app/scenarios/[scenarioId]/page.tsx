import { notFound } from "next/navigation";
import { PageShell } from "@/components/site/PageShell";
import { ButtonLink, StatePanel } from "@/components/ui";
import { ScenarioCockpit } from "@/components/ScenarioCockpit";
import { requestJson } from "@/lib/neuroflyClient";
import { parseScenarioCatalog, SCENARIO_KINDS } from "@/lib/scenarioPlayback";
import { loadScenarioPlayback } from "@/app/scenarios/actions";
import { Suspense } from "react";
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
  catch (error) {
    return <PageShell title="The scenario could not load" current="/scenarios"><StatePanel state="api-down" actions={<ButtonLink href="/scenarios">Back to Scenarios</ButtonLink>} /><p>{error instanceof Error ? error.message : "Backend unavailable."}</p></PageShell>;
  }
  const scenario = definitions.find(s => s.id === scenarioId);
  if (!scenario) notFound();
  const query = await searchParams;
  const meta = experimentMetadata[scenario.id];
  return <PageShell eyebrow={meta.kind} title={scenario.title} current="/scenarios" lead={<p>{meta.purpose}</p>}>
    {query.replay === "canonical" ? <Suspense fallback={<ScientificPlaybackLoading/>}><RestoredCockpit scenario={scenario}/></Suspense> : <ScenarioCockpit scenario={scenario}/>}
  </PageShell>;
}
