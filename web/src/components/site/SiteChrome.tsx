import Link from "next/link";
import { MobileNavigation } from "./SiteNavigation";
import { LAB_HREF, SITE_LINKS, SCIENCE_HREF } from "./siteContent";
import { Arrow } from "./SitePrimitives";
import { BrandLogo } from "./BrandLogo";

export function SiteHeader({ activeHref = "/" }: { activeHref?: string } = {}) {
  return <header className="nf-header"><div className="nf-container nf-header-inner">
    <Link prefetch={false} href="/" className="nf-wordmark" aria-label="NeuroFly home"><BrandLogo /><span>Neuro<span>Fly</span></span></Link>
    <nav className="nf-desktop-nav" aria-label="Primary navigation">{SITE_LINKS.map(link => <Link prefetch={false} key={link.href} href={link.href} aria-current={link.href === activeHref ? "page" : undefined}>{link.label}</Link>)}</nav>
    <Link prefetch={false} href={LAB_HREF} className="nf-header-cta">Enter the Lab <Arrow /></Link>
    <MobileNavigation activeHref={activeHref} />
  </div></header>;
}

export function SiteFooter() {
  return <footer className="nf-footer"><div className="nf-container">
    <div className="nf-footer-top"><div><Link prefetch={false} className="nf-wordmark" href="/" aria-label="NeuroFly home"><BrandLogo /><span>Neuro<span>Fly</span></span></Link><p>Selected circuits. Explicit assumptions.<br />Observable behaviour.</p></div><nav aria-label="Footer navigation">{SITE_LINKS.map(link => <Link prefetch={false} key={link.href} href={link.href}>{link.label}</Link>)}<Link prefetch={false} href="/experiments">Recorded experiments</Link><a href={SCIENCE_HREF}>Documentation <span aria-hidden="true">↗</span></a></nav></div>
    <div className="nf-footer-bottom"><p>Explore a connectome-informed digital organism.</p><p>Visual assets: fly by <a href="https://sketchfab.com/3d-models/wildtype-male-drosophila-melanogaster-0affd20207ca4c889bd7e1e513e04dfa">mlykouretzos</a>; lab table by <a href="https://sketchfab.com/3d-models/lab-table-a6585466b3bb4417bd0338c74328b209">zeeshanfareed</a>. <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> · Rendered and captured for NeuroFly.</p></div>
  </div></footer>;
}
