"use client";

import { useEffect, useId, useRef, useState } from "react";
import { KIND_COPY, PROVENANCE_COPY, statusLabel, type DataKind } from "@/content/science-copy";
import { KindBadge } from "./KindBadge";
import { KindGlyph } from "./KindGlyph";
import styles from "./ProvenanceLabel.module.css";

export interface ProvenanceLabelProps {
  /** Required: provenance always states the kind. */
  kind: DataKind;
  /** For example "MaleCNS v1.0". */
  source: string;
  /** Model values only. */
  modelVersion?: string;
  /** Machine status code from the API, such as NOT_EVALUATED. Experiments only. */
  status?: string;
  artifactId?: string;
  /** Detail and Raw layers only. Opens JSON in a new tab. */
  apiHref?: string;
  /** inline: one line with a details popover. card: fields shown. raw: fields plus machine codes. */
  variant?: "inline" | "card" | "raw";
  className?: string;
}

function Fields({ props, raw }: { props: ProvenanceLabelProps; raw: boolean }) {
  const [copied, setCopied] = useState<"idle" | "copied" | "failed">("idle");
  const copy = async () => {
    try { await navigator.clipboard.writeText(props.artifactId ?? ""); setCopied("copied"); } catch { setCopied("failed"); }
  };
  const F = PROVENANCE_COPY.fields;
  return (
    <dl className={styles.fields}>
      <div><dt>{F.kind}</dt><dd><KindBadge kind={props.kind} /></dd></div>
      <div><dt>{F.source}</dt><dd>{props.source}</dd></div>
      {props.modelVersion ? <div><dt>{F.modelVersion}</dt><dd>{props.modelVersion}</dd></div> : null}
      {props.status ? <div><dt>{F.status}</dt><dd>{statusLabel(props.status)}{raw ? <code className={styles.code}>{props.status}</code> : null}</dd></div> : null}
      {props.artifactId ? (
        <div>
          <dt>{F.artifactId}</dt>
          <dd className={styles.idRow}>
            <code className={styles.code}>{props.artifactId}</code>
            <button type="button" className={styles.button} onClick={copy}>{PROVENANCE_COPY.copy}</button>
            <span role="status" className={styles.copyState}>{copied === "copied" ? PROVENANCE_COPY.copied : copied === "failed" ? PROVENANCE_COPY.copyFailed : ""}</span>
          </dd>
        </div>
      ) : null}
      {props.apiHref ? <div><dt>{F.api}</dt><dd><a className={styles.link} href={props.apiHref} target="_blank" rel="noreferrer">{PROVENANCE_COPY.openJson}<span className={styles.srOnly}> (opens in a new tab)</span></a></dd></div> : null}
    </dl>
  );
}

export function ProvenanceLabel(props: ProvenanceLabelProps) {
  const { variant = "inline", className } = props;
  const [open, setOpen] = useState(false);
  const root = useRef<HTMLSpanElement>(null);
  const button = useRef<HTMLButtonElement>(null);
  const panelId = useId();

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => { if (event.key === "Escape") { setOpen(false); button.current?.focus(); } };
    const onPointer = (event: PointerEvent) => { if (root.current && !root.current.contains(event.target as Node)) setOpen(false); };
    document.addEventListener("keydown", onKey);
    document.addEventListener("pointerdown", onPointer);
    return () => { document.removeEventListener("keydown", onKey); document.removeEventListener("pointerdown", onPointer); };
  }, [open]);

  if (variant !== "inline") {
    return <section className={`${styles.card} ${className ?? ""}`} aria-label={`Provenance: ${KIND_COPY[props.kind].label}`}><Fields props={props} raw={variant === "raw"} /></section>;
  }

  const summary = [props.source, props.modelVersion].filter(Boolean).join(" · ");
  return (
    <span ref={root} className={`${styles.inline} ${className ?? ""}`}>
      <span className={styles.line} data-kind={props.kind}>
        <KindGlyph kind={props.kind} label={KIND_COPY[props.kind].label} size={11} />
        <span>{summary}</span>
        <button ref={button} type="button" className={styles.button} aria-expanded={open} aria-controls={panelId} aria-label={PROVENANCE_COPY.detailsLabel(summary)} onClick={() => setOpen((v) => !v)}>
          {PROVENANCE_COPY.details}
        </button>
      </span>
      <span id={panelId} role="group" aria-label={PROVENANCE_COPY.detailsLabel(summary)} hidden={!open} className={styles.popover}>
        <Fields props={props} raw={false} />
      </span>
    </span>
  );
}
