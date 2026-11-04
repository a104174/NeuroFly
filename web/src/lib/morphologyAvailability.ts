import { NeuroflyApiError } from "@/lib/neuroflyClient";

/** The API code that means "no morphology artifact root is configured on this deployment". */
export const MORPHOLOGY_NOT_CONFIGURED_CODE = "morphology_store_unavailable";

/**
 * True when the API says it has no neuron shape data at all (a configuration of the deployment),
 * as opposed to an outage, a bad ID or a failed integrity check.
 */
export function isMorphologyNotOnDeployment(error: unknown): boolean {
  return error instanceof NeuroflyApiError && error.code === MORPHOLOGY_NOT_CONFIGURED_CODE;
}
