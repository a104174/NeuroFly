import type { Metadata } from "next";
import { ArticleSection, ArticleShell } from "@/components/science/ArticleShell";
import { KindBadge } from "@/components/ui";
import { CAPABILITIES, CAPABILITY_GROUPS, REPOSITORY_BLOB, type CapabilityGroup } from "@/content/science-copy";
import styles from "@/components/science/Article.module.css";

export const metadata: Metadata = {
  title: "Status and limits · NeuroFly",
  description: "What works today, what is only a model and what is not available yet, with the reason for each.",
};

const GROUPS: readonly CapabilityGroup[] = ["available", "model-only", "not-available"];

export default function StatusPage() {
  return (
    <ArticleShell
      eyebrow="Science"
      title="Status and limits"
      contents={GROUPS.map((group) => ({ id: group, label: CAPABILITY_GROUPS[group].title }))}
      lead={<p>NeuroFly is a research model. This page lists what it can and cannot do, and why. Anything switched off is deliberate, not a fault, and each reason comes from a project report that you can open.</p>}
    >
      {GROUPS.map((group) => (
        <ArticleSection key={group} id={group} title={CAPABILITY_GROUPS[group].title}>
          <p>{CAPABILITY_GROUPS[group].intro}</p>
          <div className={styles.tableWrap} role="region" aria-label={`${CAPABILITY_GROUPS[group].title}: capability table`} tabIndex={0}>
            <table className={styles.table} data-claim="capabilities">
              <caption>{CAPABILITY_GROUPS[group].title}: capability, kind, reason and source</caption>
              <thead><tr><th scope="col">Capability</th><th scope="col">Kind</th><th scope="col">Reason</th><th scope="col">Source</th></tr></thead>
              <tbody>
                {CAPABILITIES.filter((capability) => capability.group === group).map((capability) => (
                  <tr key={capability.id} id={capability.id}>
                    <th scope="row">{capability.name}</th>
                    <td><KindBadge kind={capability.kind} /></td>
                    <td>{capability.reason}</td>
                    <td className={styles.source}><a href={`${REPOSITORY_BLOB}${capability.source.path}`}>{capability.source.label} <span aria-hidden="true">↗</span></a></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </ArticleSection>
      ))}
    </ArticleShell>
  );
}
