import { notFound } from "next/navigation";
import type { ReactNode } from "react";
import { getMorphologyArtifact, NeuroflyApiError } from "@/lib/neuroflyClient";

/** Decides "does this neuron sample exist?" before the page streams, so an unknown ID is a real 404. */
export default async function MorphologyLayout({ children, params }: { children: ReactNode; params: Promise<{ artifactId: string }> }) {
  const { artifactId } = await params;
  try {
    await getMorphologyArtifact(artifactId);
  } catch (error) {
    if (error instanceof NeuroflyApiError && error.status === 404) notFound();
  }
  return children;
}
