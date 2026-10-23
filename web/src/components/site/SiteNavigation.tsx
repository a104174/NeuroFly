"use client";

import Link from "next/link";
import { useRef } from "react";
import { LAB_HREF, SITE_LINKS } from "./siteContent";

/** Native disclosure remains usable without JS; JS adds Escape and link dismissal. */
export function MobileNavigation() {
  const menu = useRef<HTMLDetailsElement>(null);
  const close = () => { if (menu.current) menu.current.open = false; };
  return <details className="nf-mobile-menu" ref={menu} onKeyDown={event => {
    if (event.key === "Escape" && menu.current?.open) {
      menu.current.open = false;
      menu.current.querySelector("summary")?.focus();
    }
  }}>
    <summary><span>Menu</span><span className="nf-menu-glyph" aria-hidden="true"><span /><span /></span></summary>
    <nav aria-label="Mobile primary navigation">
      {SITE_LINKS.map(link => <Link prefetch={false} key={link.href} href={link.href} onClick={close} aria-current={link.href === "/" ? "page" : undefined}>{link.label}</Link>)}
      <Link prefetch={false} className="nf-mobile-cta" href={LAB_HREF} onClick={close}>Enter the Lab <span aria-hidden="true">↗</span></Link>
    </nav>
  </details>;
}
