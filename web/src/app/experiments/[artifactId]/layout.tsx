import { notFound } from "next/navigation";
import type { ReactNode } from "react";
import { getExperiment, NeuroflyApiError } from "@/lib/neuroflyClient";

/**
 * Decides "does this experiment exist?" before any page streams, so an unknown or malformed ID
 * returns a real 404 instead of a 200 with an error screen. The pages below call the same
 * endpoint, and Next memoises identical GETs within a request, so this costs no extra call.
 * Other failures (an unreachable API, an integrity failure) are left to the page to explain.
 */
export default async function ExperimentLayout({ children, params }: { children: ReactNode; params: Promise<{ artifactId: string }> }) {
  const { artifactId } = await params;
  try {
    await getExperiment(artifactId);
  } catch (error) {
    if (error instanceof NeuroflyApiError && (error.code === "artifact_not_found" || error.code === "invalid_artifact_id")) notFound();
  }
  return children;
}
