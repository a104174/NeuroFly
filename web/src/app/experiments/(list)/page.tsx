import type { Metadata } from "next";
import Link from "next/link";
import { NoticeBanner } from "@/components/NoticeBanner";
import { PageShell } from "@/components/site/PageShell";
import { EXPERIMENTS_LABEL } from "@/components/site/siteContent";
import { ButtonLink, DataTable, KindBadge, KindGlyph, StatePanel, type Column } from "@/components/ui";
import { DEFAULT_EXPERIMENT_QUERY, experimentsHref, modelVersion, parseExperimentQuery, searchExperiments, sortExperiments } from "@/lib/listing";
import { listExperiments, NeuroflyApiError, type ExperimentSummary } from "@/lib/neuroflyClient";
import { experimentName, isEngineeringTest } from "@/lib/recordedExperimentPresentation";
import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "Experiments · NeuroFly",
  description: "Completed NeuroFly model runs published with their status and provenance, from the read-only scientific API.",
};
export const dynamic = "force-dynamic";

const NOT_RECORDED = <span className={styles.missing}>— <span>Not recorded</span></span>;

export default async function ExperimentsPage({ searchParams }: { searchParams?: Promise<Record<string, string | string[] | undefined>> } = {}) {
  const query = parseExperimentQuery((await searchParams) ?? {});
  let experiments: ExperimentSummary[] | null = null;
  let error: string | null = null;
  let integrity = false;
  try { experiments = await listExperiments(); }
  catch (cause) {
    error = cause instanceof NeuroflyApiError ? cause.message : "The experiment API could not be reached.";
    integrity = cause instanceof NeuroflyApiError && (cause.status === 409 || cause.code === "artifact_integrity_failure");
  }

  const shown = experiments ? sortExperiments(searchExperiments(experiments, query.q), query.sort, query.dir) : [];
  // Scenario and date are not in the API's experiment summary. They are shown as "Not recorded"
  // until the backend provides them (listed as a backend request in docs/redesign-progress.md).
  const columns: Column<ExperimentSummary>[] = [
    { id: "name", label: "Name", sortable: true, render: (e) => (
      <span className={styles.name}>
        <Link prefetch={false} href={`/experiments/${e.artifact_id}`}>{experimentName(e.candidate.identifier)}</Link>
        {isEngineeringTest(e.experiment_config_id) ? <span className={styles.tag}><KindGlyph kind="unavailable" size={11} /> {EXPERIMENTS_LABEL}</span> : null}
        <span className={styles.id}>{e.artifact_id}</span>
      </span>
    ) },
    { id: "scenario", label: "Scenario", render: () => NOT_RECORDED },
    { id: "status", label: "Status", render: () => <KindBadge kind="not-evaluated" /> },
    { id: "model", label: "Model version", sortable: true, render: (e) => <span className={styles.mono}>{modelVersion(e)}</span> },
    { id: "date", label: "Date", render: () => NOT_RECORDED },
    { id: "action", label: "Cockpit", render: (e) => (
      <Link prefetch={false} href={`/experiments/${e.artifact_id}/cockpit`} aria-label={`Open Cockpit for ${experimentName(e.candidate.identifier)}`}>Open Cockpit</Link>
    ) },
  ];
  const filtered = query.q !== DEFAULT_EXPERIMENT_QUERY.q;

  return (
    <PageShell
      title="Experiments"
      current="/experiments"
      lead={<p>An experiment is a completed run published here with its status and provenance. Publishing a run does not mean it has been evaluated. <Link prefetch={false} href="/science/glossary#experiment">Read the glossary</Link>.</p>}
    >
      <div className={styles.note}>
        <NoticeBanner restoreLabel="Show the note about evaluation">No experiment has been evaluated against biological data yet.</NoticeBanner>
      </div>
      {experiments ? (
        experiments.length === 0 ? (
          <StatePanel state="empty" message="No experiments are published yet." />
        ) : (
          <>
            <div className={styles.tools}>
              <form method="get" action="/experiments" role="search" className={styles.search}>
                <label>Search experiments<input type="search" name="q" defaultValue={query.q} autoComplete="off" /></label>
                {query.sort !== DEFAULT_EXPERIMENT_QUERY.sort ? <input type="hidden" name="sort" value={query.sort} /> : null}
                {query.dir !== DEFAULT_EXPERIMENT_QUERY.dir ? <input type="hidden" name="dir" value={query.dir} /> : null}
                <button type="submit">Search</button>
              </form>
              <p className={styles.count} role="status" aria-live="polite">Showing {shown.length} of {experiments.length} experiments</p>
            </div>
            {shown.length ? (
              <DataTable
                caption="Published experiments. Select a column heading to sort."
                columns={columns}
                rows={shown}
                rowKey={(e) => e.artifact_id}
                rowHeader="name"
                sort={{ id: query.sort, direction: query.dir }}
                sortHref={(id, direction) => experimentsHref({ ...query, sort: id as "name" | "model", dir: direction })}
              />
            ) : (
              <StatePanel state="empty" message="No experiments match these filters." actions={filtered ? <ButtonLink variant="quiet" href="/experiments">Clear filters</ButtonLink> : undefined} />
            )}
          </>
        )
      ) : (
        <>
          <StatePanel state={integrity ? "integrity-failure" : "api-down"} actions={<ButtonLink href="/experiments">Retry</ButtonLink>} />
          <details className={styles.technical}>
            <summary>Technical details</summary>
            <p>{error}</p>
          </details>
          <p className={styles.after}>The recorded experiments could not be read, so no results are shown and none are substituted.</p>
        </>
      )}
      <p className={styles.after}>Looking for something to explore first? Start with the <Link prefetch={false} href="/scenarios">scenarios</Link>, or read <Link prefetch={false} href="/science/status">what is and is not established</Link>.</p>
    </PageShell>
  );
}
