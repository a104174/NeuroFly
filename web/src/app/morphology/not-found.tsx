"use client";

import { useParams } from "next/navigation";
import { PageShell } from "@/components/site/PageShell";
import { ButtonLink, StatePanel } from "@/components/ui";
import { SITE_LINKS } from "@/components/site/siteContent";

/** Shown for an unknown neuron-sample ID, with the ID, and a way back to the list. */
export default function MorphologyNotFound() {
  const { artifactId } = useParams<{ artifactId?: string }>();
  return (
    <PageShell title="Neuron sample not found" current="/morphology">
      {artifactId ? (
        <StatePanel state="unknown-id" noun="neuron sample" id={artifactId} actions={<ButtonLink href="/morphology">All neurons</ButtonLink>} />
      ) : (
        <StatePanel state="not-found" links={SITE_LINKS.map((link) => <ButtonLink key={link.href} variant="quiet" href={link.href}>{link.label}</ButtonLink>)} />
      )}
    </PageShell>
  );
}
