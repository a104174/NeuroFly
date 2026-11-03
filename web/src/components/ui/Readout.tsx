import { isBiologicalUnit, READOUT_COPY, KIND_COPY, UNIT_COPY, type DataKind } from "@/content/science-copy";
import { isModelEquivalentUnit, type ModelUnit } from "@/lib/modelUnits";
import { KindGlyph } from "./KindGlyph";
import { Tooltip } from "./Tooltip";
import styles from "./Readout.module.css";

type Base = {
  label: string;
  size?: "default" | "large";
  /** Reserve this many characters so digits do not shift as values change. */
  minChars?: number;
  className?: string;
};
type ValueFor<K extends DataKind, U> = Base & {
  kind: K;
  state?: "value";
  value: number | string;
  /** Fixed decimals for numbers. */
  digits?: number;
  unit?: U;
};

/**
 * `kind` is required in every variant, and model state may only carry a model unit, so a
 * readout cannot be written without saying what kind of number it is.
 */
export type ReadoutProps =
  | (ValueFor<"model-state", ModelUnit> & { unit: ModelUnit })
  | ValueFor<Exclude<DataKind, "model-state" | "unavailable">, string>
  | (Base & { kind: DataKind; state: "not-recorded" })
  | (Base & { kind: DataKind; state: "loading" })
  | (Base & { kind: DataKind; state: "unavailable"; reason: string });

/** In development a biological unit on model output is a bug; in production it is withheld. */
function safeUnit(unit: string | undefined): string | undefined {
  if (unit === undefined || !isBiologicalUnit(unit)) return unit;
  if (process.env.NODE_ENV !== "production") {
    throw new Error(`"${unit}" is a biological unit. Model output uses model-equivalent units such as mV_eq.`);
  }
  console.error(`Readout unit "${unit}" withheld: biological units are not allowed on model output.`);
  return undefined;
}

export function Readout(props: ReadoutProps) {
  const { label, size = "default", minChars, className } = props;
  const state = props.state ?? "value";
  const shownKind: DataKind = state === "unavailable" ? "unavailable" : props.kind;
  const kindLabel = KIND_COPY[shownKind].label;

  let body: React.ReactNode;
  if (state === "value" && "value" in props) {
    const text = typeof props.value === "number" && props.digits !== undefined ? props.value.toFixed(props.digits) : String(props.value);
    const unit = safeUnit(props.unit);
    body = (
      <>
        <span className={styles.number}>{text}</span>
        {unit === undefined ? null : unit === "dimensionless" ? (
          <span className={styles.unit}>{UNIT_COPY.dimensionless}</span>
        ) : isModelEquivalentUnit(unit) ? (
          <Tooltip content={`${unit}: ${UNIT_COPY.modelEquivalentExplanation}`} focusable>
            <span className={styles.unit}>{unit}<span className={styles.srOnly}>, {UNIT_COPY.modelEquivalentNote}</span></span>
          </Tooltip>
        ) : (
          <span className={styles.unit}>{unit}</span>
        )}
      </>
    );
  } else if (state === "loading") {
    body = <span className={styles.skeleton} role="status" aria-label={`${READOUT_COPY.loading} ${label}`} />;
  } else if (state === "unavailable" && "reason" in props) {
    body = (<><span className={styles.number} aria-hidden="true">—</span><span className={styles.note}>{READOUT_COPY.notAvailable}. {props.reason}</span></>);
  } else {
    // A missing value is never drawn as zero.
    body = (<><span className={styles.number} aria-hidden="true">—</span><span className={styles.note}>{READOUT_COPY.notRecorded}</span></>);
  }

  return (
    <div
      className={`${styles.readout} ${size === "large" ? styles.large : ""} ${className ?? ""}`}
      data-kind={shownKind}
      data-state={state}
      style={minChars ? ({ "--min-chars": minChars } as React.CSSProperties) : undefined}
    >
      <span className={styles.label}>
        <span className={styles.glyph}><KindGlyph kind={shownKind} label={kindLabel} size={11} /></span>
        <span>{label}</span>
      </span>
      <span className={styles.value}>{body}</span>
    </div>
  );
}
