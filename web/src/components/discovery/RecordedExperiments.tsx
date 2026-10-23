import Link from "next/link";
import type { ExperimentSummary } from "@/lib/neuroflyClient";
import { Arrow, ActionLink } from "../site/SitePrimitives";
import { DiscoveryState } from "./DiscoveryShell";

function runTitle(identifier: string) {
  const words = identifier.replace(/_v\d+$/, "").replaceAll("_", " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

/** No browser storage or model execution. Preserve API ordering and artifact identities. */
export function RecordedExperiments({ experiments, error }: { experiments: ExperimentSummary[] | null; error: string | null }) {
  return <>
    {error !== null ? <DiscoveryState kind="error" title="Recorded experiments are temporarily unavailable."><p>The current experiment archive could not be verified, so no results are displayed.</p><ActionLink href="/visual-lab/arena">Enter the Lab</ActionLink><details className="discovery-context"><summary>Technical details</summary><p className="discovery-error-detail">{error}</p></details></DiscoveryState> : !experiments?.length ? <DiscoveryState kind="empty" title="No recorded experiments yet."><p>No completed experiment artifacts are available through the configured read-only API yet.</p><p>You can explore the Lab while this collection is empty. Lab activity is not automatically saved here.</p><ActionLink href="/visual-lab/arena">Enter the Lab</ActionLink></DiscoveryState> : <section className="recorded-collection" aria-labelledby="recorded-title"><div className="discovery-section-heading"><h2 id="recorded-title">Ready for a closer look.</h2><p>{experiments.length} {experiments.length === 1 ? "recorded run" : "recorded runs"}</p></div><ol className="recorded-list">{experiments.map(experiment => <li key={experiment.artifact_id}>
      <div className="recorded-identity"><span className="discovery-format">Completed model run</span><h3>{runTitle(experiment.candidate.identifier)}</h3><p>{experiment.pathway_condition.replaceAll("_", " ")} pathway · {experiment.duration_ms} ms</p><p className="recorded-validation">Empirical validation: {experiment.validation_status.replaceAll("_", " ").toLowerCase()}</p></div>
      <div className="recorded-actions"><Link prefetch={false} className="discovery-text-link" href={`/experiments/${experiment.artifact_id}`}>Inspect run <Arrow /></Link><Link prefetch={false} className="recorded-secondary" href={`/experiments/${experiment.artifact_id}/cockpit`}>Scientific cockpit ↗</Link></div>
      <details className="discovery-context"><summary>Run identity</summary><dl><div><dt>Artifact ID</dt><dd>{experiment.artifact_id}</dd></div><div><dt>Candidate</dt><dd>{experiment.candidate.identifier} · version {experiment.candidate.version}</dd></div><div><dt>Dataset</dt><dd>{experiment.dataset}</dd></div><div><dt>Integration interval</dt><dd>{experiment.dt_ms} ms</dd></div></dl></details>
    </li>)}</ol></section>}
    <section className="discovery-research"><div><p className="nf-eyebrow">Different ways to revisit</p><h2>Know what you’re revisiting.</h2><p>This collection contains completed scientific model runs. Sessions saved in the research tools are stored separately in this browser.</p></div><Link prefetch={false} className="discovery-text-link" href="/visual-lab/arena/research">Find research tools <Arrow /></Link></section>
  </>;
}
