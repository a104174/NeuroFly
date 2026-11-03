import { KIND_COPY, type DataKind } from "@/content/science-copy";
import { KindGlyph } from "./KindGlyph";
import { Tooltip } from "./Tooltip";
import styles from "./KindBadge.module.css";

type Common = {
  /** Required: a value without a kind cannot be rendered. */
  kind: DataKind;
  /** Adds the kind's explanation as a tooltip and makes the badge focusable. */
  explain?: boolean;
  className?: string;
};
/** Glyph and text together by default. Glyph only is allowed inside a titled group. */
export type KindBadgeProps =
  | (Common & { variant?: "full" })
  | (Common & { variant: "glyph"; inTitledGroup: true });

export function KindBadge(props: KindBadgeProps) {
  const { kind, explain = false, className } = props;
  const copy = KIND_COPY[kind];
  const glyphOnly = props.variant === "glyph";
  const badge = (
    <span
      className={`${styles.badge} ${glyphOnly ? styles.glyphOnly : ""} ${className ?? ""}`}
      data-kind={kind}
      {...(glyphOnly ? { role: "img", "aria-label": copy.label } : {})}
    >
      <KindGlyph kind={kind} />
      {glyphOnly ? null : <span>{copy.label}</span>}
    </span>
  );
  return explain ? <Tooltip content={copy.tooltip} variant="definition" focusable>{badge}</Tooltip> : badge;
}
