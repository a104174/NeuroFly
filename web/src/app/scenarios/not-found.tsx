"use client";

import { useParams } from "next/navigation";
import { PageShell } from "@/components/site/PageShell";
import { ButtonLink, StatePanel } from "@/components/ui";
import { SITE_LINKS } from "@/components/site/siteContent";

/** Shown for an unknown scenario ID, with the ID, and a way back to the list. */
export default function ScenarioNotFound() {
  const { scenarioId } = useParams<{ scenarioId?: string }>();
  return (
    <PageShell title="Scenario not found" current="/scenarios">
      {scenarioId ? (
        <StatePanel state="unknown-id" noun="scenario" id={scenarioId} actions={<ButtonLink href="/scenarios">All scenarios</ButtonLink>} />
      ) : (
        <StatePanel state="not-found" links={SITE_LINKS.map((link) => <ButtonLink key={link.href} variant="quiet" href={link.href}>{link.label}</ButtonLink>)} />
      )}
    </PageShell>
  );
}
