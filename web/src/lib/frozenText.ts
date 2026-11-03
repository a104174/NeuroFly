/**
 * English display text for the few Portuguese strings that still live in frozen modules
 * (`scripts/frozen-contribution.ts` pins their bytes, so they cannot be edited in place).
 * Components pass every such string through `displayText` before showing it.
 */
const ENGLISH: Readonly<Record<string, string>> = {
  "Steering neural ativo": "Neural steering on",
  "Saída para steering desligada": "Steering output off",
  "Dados de locomoção incompatíveis ou corrompidos. Nenhum movimento foi criado.": "Locomotion data are incompatible or corrupted. No movement was created.",
  "Replay neural incompatível ou corrompido. Nenhum steering de substituição foi criado.": "Neural replay is incompatible or corrupted. No substitute steering was created.",
};

export function displayText(text: string): string {
  if (ENGLISH[text]) return ENGLISH[text];
  const http = text.match(/^(Locomoção|Replay neural) indisponível \(HTTP (\d+)\)\.$/);
  if (http) return `${http[1] === "Locomoção" ? "Locomotion" : "Neural replay"} unavailable (HTTP ${http[2]}).`;
  return text;
}
