import type { Metadata } from "next";
import Link from "next/link";
import { PageShell } from "@/components/site/PageShell";
import { LAB_HREF } from "@/components/site/siteContent";
import { ButtonLink, Card, SegmentedLinks, StatePanel } from "@/components/ui";
import { STIMULUS_FILTERS, filterScenarios, parseStimulus, scenariosHref } from "@/lib/listing";
import { listScenarios } from "@/lib/scenarioCatalog";
import { discoveryCopy, experimentMetadata } from "@/lib/scenarioPresentation";
import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "Scenarios · NeuroFly",
  description: "The five canonical NeuroFly scenarios: defined situations, recorded in advance and played back from stored data.",
};
// The five scenario definitions stay API-owned; this page only presents them and never starts a model.
export const dynamic = "force-dynamic";

export default async function ScenariosPage({ searchParams }: { searchParams?: Promise<Record<string, string | string[] | undefined>> } = {}) {
  const stimulus = parseStimulus((await searchParams)?.stimulus);
  let scenarios;
  let error: string | null = null;
  try { scenarios = await listScenarios(); }
  catch (cause) { error = cause instanceof Error ? cause.message : "Please check the backend."; }
  const shown = scenarios ? filterScenarios(scenarios, stimulus) : [];

  return (
    <PageShell
      title="Scenarios"
      lead={<p>A scenario is a defined situation: which stimulus, which circuit, which settings. Each one here was recorded in advance, and you play it back. <Link prefetch={false} href="/science/glossary#scenario">Read the glossary</Link>.</p>}
    >
      {scenarios ? (
        <>
          <div className={styles.toolbar}>
            <SegmentedLinks
              label="Stimulus type"
              items={[{ id: "all", label: "All", href: scenariosHref(null), current: stimulus === null }, ...STIMULUS_FILTERS.map((f) => ({ id: f.key, label: f.label, href: scenariosHref(f.key), current: stimulus === f.key }))]}
            />
            <p className={styles.count} role="status" aria-live="polite">Showing {shown.length} of {scenarios.length} scenarios</p>
          </div>
          {shown.length ? (
            <ul className={styles.grid}>
              {shown.map((scenario) => {
                const copy = discoveryCopy[scenario.id], meta = experimentMetadata[scenario.id];
                return (
                  <li key={scenario.id} data-scenario-id={scenario.id}>
                    <Card
                      eyebrow={meta.kind}
                      titleLevel={2}
                      title={copy.title}
                      href={`/scenarios/${scenario.id}`}
                      meta={[{ label: "Stimulus", value: meta.input }, { label: "Scientific duration", value: meta.duration }]}
                    >
                      <p>{copy.description}</p>
                      <details>
                        <summary>What this does not show</summary>
                        <p>{meta.limit}</p>
                        <p>{scenario.scientific_caveat}</p>
                        <p>Scenario name in the API: {scenario.title}</p>
                      </details>
                    </Card>
                  </li>
                );
              })}
            </ul>
          ) : (
            <StatePanel state="empty" message="No scenarios match this stimulus type." actions={<ButtonLink variant="quiet" href={scenariosHref(null)}>Clear filter</ButtonLink>} />
          )}
          <p className={styles.note}>Every result here is model state and has not been evaluated against real fly data. A “circuit check” confirms that the model runs as specified; it is not biological validation. The one published run is listed under <Link prefetch={false} href="/experiments">Engineering test, not a scientific experiment</Link>.</p>
        </>
      ) : (
        <>
          <StatePanel state="api-down" actions={<><ButtonLink href="/scenarios">Retry</ButtonLink><ButtonLink variant="quiet" href={LAB_HREF}>Enter the Lab</ButtonLink></>} />
          <details className={styles.technical}>
            <summary>Technical details</summary>
            <p>{error}</p>
          </details>
          <p className={styles.note}>The scenario catalogue is unavailable, so no scenarios are shown and none are substituted.</p>
        </>
      )}
      <section className={styles.lab} aria-labelledby="lab-title">
        <div>
          <h2 id="lab-title">Prefer to explore freely?</h2>
          <p>Explore runs in your browser: walking and flight modes with engineering movement and no muscle or wing physics.</p>
        </div>
        <ButtonLink variant="quiet" href={LAB_HREF}>Enter the Lab</ButtonLink>
      </section>
    </PageShell>
  );
}
