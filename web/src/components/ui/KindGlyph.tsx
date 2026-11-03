import type { DataKind } from "@/content/science-copy";

/**
 * One glyph per data kind. The square and diamond differ by shape; the three circles
 * differ by half fill, dashed outline and slash, so no kind depends on colour.
 * Decorative by default; pass `label` for a standalone glyph.
 */
export function KindGlyph({ kind, size = 12, label }: { kind: DataKind; size?: number; label?: string }) {
  const accessibility = label ? { role: "img" as const, "aria-label": label } : { "aria-hidden": true as const };
  const common = { width: size, height: size, viewBox: "0 0 12 12", focusable: false, ...accessibility };
  switch (kind) {
    case "structural":
      return <svg {...common}><rect x="2" y="2" width="8" height="8" fill="currentColor" /></svg>;
    case "model-assumption":
      return <svg {...common}><path d="M6 1.5 10.5 6 6 10.5 1.5 6Z" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" /></svg>;
    case "model-state":
      return <svg {...common}><circle cx="6" cy="6" r="4.25" fill="none" stroke="currentColor" strokeWidth="1.5" /><path d="M6 1.75A4.25 4.25 0 0 0 6 10.25Z" fill="currentColor" /></svg>;
    case "not-evaluated":
      return <svg {...common}><circle cx="6" cy="6" r="4.25" fill="none" stroke="currentColor" strokeWidth="1.5" strokeDasharray="2 1.7" /></svg>;
    case "unavailable":
      return <svg {...common}><circle cx="6" cy="6" r="4.25" fill="none" stroke="currentColor" strokeWidth="1.5" /><path d="M3 9 9 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" /></svg>;
  }
}
