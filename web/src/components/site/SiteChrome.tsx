import Link from "next/link";
import { MALECNS_RELEASE } from "@/content/science-copy";
import { BrandLogo } from "./BrandLogo";
import { SiteNavigation } from "./SiteNavigation";
import { StatusPill } from "./StatusPill";
import { ThemeSwitch } from "./ThemeSwitch";
import { AUTHOR_HREF, AUTHOR_NAME, CC_BY_HREF, DATA_CREDIT_HREF, EXPERIMENTS_HREF, EXPERIMENTS_LABEL, LAB_HREF, MALECNS_HREF, MALECNS_RELEASE_HREF, SCIENCE_HREF, SCIENCE_PAGE_HREF, SITE_LINKS, STATUS_HREF } from "./siteContent";
import styles from "./SiteChrome.module.css";

/**
 * `tone="dark"` pins the chrome to dark while the page around it is still the legacy dark
 * design. A page that has migrated to the tokens passes `tone="auto"`, which follows the theme
 * and shows the theme switch. The default becomes "auto" when the last legacy page migrates.
 */
type Tone = "dark" | "auto";

export type SiteHeaderProps = {
  /** default: full navigation. tool: 48 px bar for the Cockpit and Lab. over-stage: glass over a 3D stage. */
  variant?: "default" | "tool" | "over-stage";
  tone?: Tone;
  /** Overrides the current path, for tests and for pages that sit under another section. */
  current?: string;
  /** Tool variant: where the back link goes, what it says, and the page title. */
  backHref?: string;
  backLabel?: string;
  title?: string;
};

function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <Link prefetch={false} href="/" className={styles.brand} aria-label="NeuroFly home">
      <BrandLogo />
      {compact ? null : <span className={styles.wordmark}>Neuro<span>Fly</span></span>}
    </Link>
  );
}

/** The skip link is the first focusable element on every page. Each page's <main> has id="main-content". */
export function SiteHeader({ variant = "default", tone = "auto", current, backHref, backLabel, title }: SiteHeaderProps) {
  const tool = variant === "tool";
  return (
    <header className={styles.header} data-variant={variant} data-theme-scope={tone === "dark" ? "dark" : undefined}>
      <a className={styles.skip} href="#main-content">Skip to content</a>
      <div className={styles.inner}>
        <Brand compact={tool} />
        {tool ? (
          <>
            {backHref ? <Link prefetch={false} href={backHref} className={styles.back}><span aria-hidden="true">←</span> {backLabel ?? "Back"}</Link> : null}
            {title ? <p className={styles.title}>{title}</p> : null}
            <div className={styles.actions}><StatusPill /></div>
          </>
        ) : (
          <>
            <SiteNavigation current={current} themeSwitch={tone === "auto"}>
              <StatusPill />
              {tone === "auto" ? <ThemeSwitch className={styles.desktopOnly} /> : null}
            </SiteNavigation>
          </>
        )}
      </div>
    </header>
  );
}

export function SiteFooter({ tone = "auto" }: { tone?: Tone }) {
  return (
    <footer className={styles.footer} data-theme-scope={tone === "dark" ? "dark" : undefined}>
      <div className={styles.footerInner}>
        <div className={styles.footerTop}>
          <div>
            <Brand />
            <p className={styles.tagline}>Selected circuits. Explicit assumptions.<br />Observable behaviour.</p>
          </div>
          <nav aria-label="Footer navigation" className={styles.footerNav}>
            {SITE_LINKS.map((link) => <Link prefetch={false} key={link.href} href={link.href}>{link.label}</Link>)}
            <Link prefetch={false} href={STATUS_HREF}>Status and limits</Link>
            <Link prefetch={false} href={EXPERIMENTS_HREF}>{EXPERIMENTS_LABEL}</Link>
            <a href={SCIENCE_HREF}>Documentation <span aria-hidden="true">↗</span></a>
            <a href={MALECNS_HREF}>MaleCNS data <span aria-hidden="true">↗</span></a>
          </nav>
        </div>
        <div className={styles.footerBottom}>
          <p>Wiring and neuron shapes: <a href={MALECNS_RELEASE_HREF}>{MALECNS_RELEASE}</a>, licensed <a href={CC_BY_HREF}>CC BY 4.0</a>. NeuroFly&rsquo;s files are derived from it (<a href={DATA_CREDIT_HREF}>how</a>). Model output is not biological data.</p>
          <p>Created by <a href={AUTHOR_HREF}>{AUTHOR_NAME}</a>.</p>
          <p>Visual assets: fly by <a href="https://sketchfab.com/3d-models/wildtype-male-drosophila-melanogaster-0affd20207ca4c889bd7e1e513e04dfa">mlykouretzos</a>; lab table by <a href="https://sketchfab.com/3d-models/lab-table-a6585466b3bb4417bd0338c74328b209">zeeshanfareed</a>. <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> · Rendered and captured for NeuroFly.</p>
        </div>
      </div>
    </footer>
  );
}

export { LAB_HREF, SCIENCE_PAGE_HREF };
