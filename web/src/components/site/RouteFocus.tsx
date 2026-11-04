"use client";

import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";

const SETTLE_MS = 3000;

/**
 * After a client-side route change, move focus to the page's h1 so keyboard and screen-reader
 * users start at the new content (brief section 9). The route's loading state is replaced by the
 * real page a moment later, which would drop focus, so focus is re-applied while the page settles
 * and left alone as soon as the user acts. It does nothing on first load, and a change of query
 * string alone (a filter) does not move focus.
 */
export function RouteFocus() {
  const pathname = usePathname();
  const first = useRef(true);
  useEffect(() => {
    if (first.current) { first.current = false; return; }
    let focused: HTMLElement | null = null;
    const focusHeading = () => {
      const heading = document.querySelector<HTMLElement>("main h1") ?? document.querySelector<HTMLElement>("h1");
      if (!heading) return;
      if (!heading.hasAttribute("tabindex")) heading.setAttribute("tabindex", "-1");
      heading.focus({ preventScroll: true });
      if (document.activeElement === heading) focused = heading;
    };
    const lost = () => !focused || !focused.isConnected || document.activeElement === document.body;
    focusHeading();
    const observer = new MutationObserver(() => { if (lost()) focusHeading(); });
    observer.observe(document.body, { childList: true, subtree: true });
    const stop = () => {
      observer.disconnect();
      clearTimeout(timer);
      window.removeEventListener("keydown", stop);
      window.removeEventListener("pointerdown", stop);
    };
    const timer = setTimeout(stop, SETTLE_MS);
    window.addEventListener("keydown", stop);
    window.addEventListener("pointerdown", stop);
    return stop;
  }, [pathname]);
  return null;
}
