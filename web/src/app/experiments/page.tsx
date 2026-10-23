import type { Metadata } from "next";
import { DiscoveryShell } from "@/components/discovery/DiscoveryShell";
import { RecordedExperiments } from "@/components/discovery/RecordedExperiments";
import { listExperiments, NeuroflyApiError, type ExperimentSummary } from "@/lib/neuroflyClient";

export const metadata: Metadata = { title: "Recorded experiments · NeuroFly", description: "Inspect completed NeuroFly model runs, their provenance and recorded neural timelines through the read-only scientific API." };
export const dynamic = "force-dynamic";
export default async function ExperimentsPage() {
  let experiments: ExperimentSummary[] | null = null;
  let error: string | null = null;
  try { experiments = await listExperiments(); }
  catch (cause) { error = cause instanceof NeuroflyApiError ? cause.message : "The experiment API could not be reached."; }
  return <DiscoveryShell active="experiments">
    <header className="discovery-hero discovery-hero--records"><p className="nf-eyebrow">NeuroFly / Recorded experiments</p><h1>Return to<br /><span>the evidence.</span></h1><p>Completed model runs, with their provenance and neural timelines. Inspect what was recorded, at your own pace.</p></header>
    <RecordedExperiments experiments={experiments} error={error} />
  </DiscoveryShell>;
}
