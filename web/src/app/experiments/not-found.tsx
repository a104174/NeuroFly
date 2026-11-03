"use client";

import { useParams } from "next/navigation";
import { PageShell } from "@/components/site/PageShell";
import { ButtonLink, StatePanel } from "@/components/ui";
import { SITE_LINKS } from "@/components/site/siteContent";

/** Shown for an unknown experiment ID, with the ID, and a way back to the list. */
export default function ExperimentNotFound() {
  const { artifactId } = useParams<{ artifactId?: string }>();
  return (
    <PageShell title="Experiment not found" current="/experiments">
      {artifactId ? (
        <StatePanel state="unknown-id" noun="experiment" id={artifactId} actions={<ButtonLink href="/experiments">All experiments</ButtonLink>} />
      ) : (
        <StatePanel state="not-found" links={SITE_LINKS.map((link) => <ButtonLink key={link.href} variant="quiet" href={link.href}>{link.label}</ButtonLink>)} />
      )}
    </PageShell>
  );
}
