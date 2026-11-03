"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, type ReactNode } from "react";
import { ThemeSwitch } from "./ThemeSwitch";
import { SITE_LINKS, isCurrent } from "./siteContent";
import styles from "./SiteChrome.module.css";

const FOCUSABLE = 'a[href], button:not([disabled]), summary, [tabindex]:not([tabindex="-1"])';

/**
 * Primary links for wide screens, and a full-height sheet below 1024 px. The sheet is a native
 * <details>, so it opens without JavaScript; JavaScript adds Escape, a focus trap, scroll
 * lock and closing on navigation.
 */
export function SiteNavigation({ current, themeSwitch = false, children }: { current?: string; themeSwitch?: boolean; /** Status pill and desktop theme switch. Rendered before the menu button so visual and focus order match. */ children?: ReactNode }) {
  const pathname = usePathname();
  const here = current ?? pathname;
  const menu = useRef<HTMLDetailsElement>(null);

  useEffect(() => { if (menu.current) menu.current.open = false; }, [pathname]);

  useEffect(() => {
    const details = menu.current;
    const header = details?.closest("header");
    if (!details || !header) return;
    let open = details.open;
    const lock = (on: boolean) => { document.documentElement.style.overflow = on ? "hidden" : ""; };
    const onToggle = () => { open = details.open; lock(open); };
    const onKey = (event: KeyboardEvent) => {
      if (!open) return;
      if (event.key === "Escape") { details.open = false; details.querySelector("summary")?.focus(); return; }
      if (event.key !== "Tab") return;
      const items = [...header.querySelectorAll<HTMLElement>(FOCUSABLE)].filter((el) => el.getClientRects().length > 0 && !el.closest("[hidden]"));
      if (!items.length) return;
      const first = items[0], last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    const wide = window.matchMedia("(min-width: 1024px)");
    const onWide = () => { if (wide.matches) details.open = false; };
    details.addEventListener("toggle", onToggle);
    header.addEventListener("keydown", onKey);
    wide.addEventListener("change", onWide);
    return () => {
      details.removeEventListener("toggle", onToggle);
      header.removeEventListener("keydown", onKey);
      wide.removeEventListener("change", onWide);
      lock(false);
    };
  }, []);

  const links = (closeOnClick: boolean) => SITE_LINKS.map((link) => (
    <Link key={link.href} prefetch={false} href={link.href} className={styles.link} onClick={closeOnClick ? () => { if (menu.current) menu.current.open = false; } : undefined} aria-current={isCurrent(link.match, here) ? "page" : undefined}>
      {link.label}
    </Link>
  ));

  return (
    <>
      <nav aria-label="Primary navigation" className={styles.desktopNav}>{links(false)}</nav>
      <div className={styles.actions}>
      {children}
      <details ref={menu} className={styles.menu}>
        <summary className={styles.menuButton}><span>Menu</span><span className={styles.menuGlyph} aria-hidden="true"><span /><span /></span></summary>
        <div className={styles.sheet}>
          <nav aria-label="Mobile primary navigation">{links(true)}</nav>
          {themeSwitch ? <div className={styles.sheetTheme}><span>Theme</span><ThemeSwitch /></div> : null}
        </div>
      </details>
      </div>
    </>
  );
}
