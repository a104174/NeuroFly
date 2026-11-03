"use client";

import { useCallback, useEffect, useId, useLayoutEffect, useRef, useState, type ReactNode } from "react";
import styles from "./Tooltip.module.css";

/**
 * Plain or definition tooltip (brief section 6): opens after 400 ms on hover and at once
 * on focus, closes on Escape, stays open while the pointer is over it (WCAG 1.4.13), and
 * opens on tap for touch. It is never the only place essential information appears.
 * Pass `focusable` when the trigger is not itself focusable so keyboard users can open it.
 * A focusable trigger can be under 24 px (a 22 px badge); it meets WCAG 2.5.8 through the spacing
 * exception, so keep other targets more than 24 px away from it.
 */
export function Tooltip({
  content,
  children,
  variant = "plain",
  focusable = false,
  className,
}: {
  content: ReactNode;
  children: ReactNode;
  variant?: "plain" | "definition";
  focusable?: boolean;
  className?: string;
}) {
  const id = useId();
  const [open, setOpen] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const lastPointer = useRef<string>("mouse");
  const tip = useRef<HTMLSpanElement>(null);

  const clear = () => { if (timer.current !== undefined) { clearTimeout(timer.current); timer.current = undefined; } };
  const show = useCallback((delay: number) => {
    clear();
    if (delay === 0) setOpen(true);
    else timer.current = setTimeout(() => setOpen(true), delay);
  }, []);
  const hide = useCallback(() => { clear(); setOpen(false); }, []);
  useEffect(() => clear, []);

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => { if (event.key === "Escape") hide(); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, hide]);

  // Keep the tooltip inside the viewport: flip below when there is no room above, then shift sideways.
  useLayoutEffect(() => {
    const element = tip.current;
    if (!open || !element) return;
    element.dataset.placement = "top";
    element.style.setProperty("--shift", "0px");
    let box = element.getBoundingClientRect();
    if (box.top < 8) { element.dataset.placement = "bottom"; box = element.getBoundingClientRect(); }
    const margin = 8;
    const shift = box.left < margin ? margin - box.left : box.right > window.innerWidth - margin ? window.innerWidth - margin - box.right : 0;
    element.style.setProperty("--shift", `${shift}px`);
  }, [open]);

  return (
    <span
      className={`${styles.root} ${className ?? ""}`}
      onMouseEnter={() => { lastPointer.current = "mouse"; show(400); }}
      onMouseLeave={hide}
      onFocus={() => show(0)}
      onBlur={hide}
      onPointerDown={(event) => { lastPointer.current = event.pointerType; }}
      onClick={() => { if (lastPointer.current === "touch") { if (open) hide(); else show(0); } }}
    >
      <span className={styles.trigger} tabIndex={focusable ? 0 : undefined} aria-describedby={id}>
        {children}
      </span>
      <span ref={tip} id={id} role="tooltip" hidden={!open} className={`${styles.tip} ${variant === "definition" ? styles.definition : ""}`}>
        {content}
      </span>
    </span>
  );
}
