/* eslint-disable @next/next/no-img-element -- Pre-encoded WebP assets; the hero poster is the LCP element and needs fetchPriority. */
import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter, SiteHeader } from "@/components/site/SiteChrome";
import { EXPERIMENTS_HREF, EXPERIMENTS_LABEL, LAB_HREF, STATUS_HREF } from "@/components/site/siteContent";
import { KindBadge, KindGlyph } from "@/components/ui";
import { HOME_COPY, KIND_COPY } from "@/content/science-copy";
import { discoveryCopy, experimentMetadata } from "@/lib/scenarioPresentation";
import type { ScenarioKind } from "@/lib/scenarioPlayback";
import styles from "./page.module.css";

/** The one scenario that opens ready to play with no setup. */
const FIRST_SCENARIO: ScenarioKind = "LOOMING_CIRCUIT_VALIDATION";
const FIRST_SCENARIO_HREF = `/scenarios/${FIRST_SCENARIO}?replay=canonical`;
/** Up to four cards: three canonical scenarios and the Lab. */
const GALLERY: readonly ScenarioKind[] = ["LOOMING_CIRCUIT_VALIDATION", "HORIZONTAL_MOTION_NEURAL_VALIDATION", "EXPLORATORY_COURSE_CONTROL"];

export const metadata: Metadata = {
  title: "NeuroFly · Selected fruit fly circuits, modelled from the connectome",
  description: HOME_COPY.statement,
  openGraph: { title: HOME_COPY.headline, description: HOME_COPY.statement, siteName: "NeuroFly", type: "website", locale: "en_GB" },
};

export default function HomePage() {
  return (
    <div data-themed-page className={styles.page}>
      {/* Reveals the server-rendered page when JS cannot finish the root loading boundary. */}
      <noscript><style>{`body > [hidden]:has(> [data-themed-page]) { display: block !important; }
        body:has(> [hidden] > [data-themed-page]) > .app-shell { display: none !important; }`}</style></noscript>
      <SiteHeader tone="auto" />
      <main id="main-content" tabIndex={-1}>
        <section className={styles.hero} aria-labelledby="home-title">
          <div className={styles.heroCopy}>
            <p className={styles.eyebrow}>{HOME_COPY.eyebrow}</p>
            <h1 id="home-title">{HOME_COPY.headline}</h1>
            <p className={styles.statement}>{HOME_COPY.statement}</p>
            <div className={styles.actions}>
              <Link prefetch={false} className={styles.primary} href={FIRST_SCENARIO_HREF}>{HOME_COPY.primaryAction}</Link>
              <Link prefetch={false} className={styles.quiet} href={STATUS_HREF}>{HOME_COPY.secondaryAction}</Link>
            </div>
          </div>
          <figure className={styles.stage} data-theme-scope="dark">
            <img
              src="/assets/site/fly-specimen.webp"
              srcSet="/assets/site/fly-specimen-small.webp 768w, /assets/site/fly-specimen.webp 1500w"
              sizes="(max-width: 1023px) 92vw, 560px"
              width={1500}
              height={1400}
              fetchPriority="high"
              loading="eager"
              decoding="sync"
              alt="Three-quarter render of NeuroFly's 3D male fruit fly model, showing its eyes, translucent wings and six legs. It is an artistic model, not a reconstruction of the connectome."
            />
            <figcaption>{HOME_COPY.posterCaption}</figcaption>
          </figure>
        </section>

        <section className={styles.strip} aria-label="Scope and status">
          <ul>
            {HOME_COPY.strip.map((fact) => (
              <li key={fact.text} data-kind={fact.kind}><KindGlyph kind={fact.kind} size={14} label={KIND_COPY[fact.kind].label} /><span>{fact.text}</span></li>
            ))}
          </ul>
        </section>

        <section className={styles.section} aria-labelledby="layers-title">
          <h2 id="layers-title">Three layers, kept apart</h2>
          <p className={styles.sectionLead}>Every number on this site says which layer it comes from.</p>
          <ol className={styles.layers}>
            {HOME_COPY.layers.map((layer) => (
              <li key={layer.title}>
                <KindBadge kind={layer.kind} />
                <h3>{layer.title}</h3>
                <p>{layer.text}</p>
              </li>
            ))}
          </ol>
        </section>

        <section className={styles.section} aria-labelledby="scenarios-title">
          <h2 id="scenarios-title">Scenarios</h2>
          <p className={styles.sectionLead}>A scenario is a defined situation. These are recorded in advance, and you can play them back.</p>
          <ul className={styles.gallery}>
            {GALLERY.map((id) => {
              const copy = discoveryCopy[id], meta = experimentMetadata[id];
              return (
                <li key={id} className={styles.card}>
                  <p className={styles.cardKind}>{meta.kind}</p>
                  <h3><Link prefetch={false} href={`/scenarios/${id}`}>{copy.title}</Link></h3>
                  <p>{copy.description}</p>
                  <dl className={styles.meta}>
                    <div><dt>Stimulus</dt><dd>{meta.input}</dd></div>
                    <div><dt>Scientific duration</dt><dd>{meta.duration}</dd></div>
                  </dl>
                </li>
              );
            })}
            <li className={styles.card}>
              <p className={styles.cardKind}>Lab</p>
              <h3><Link prefetch={false} href={LAB_HREF}>{HOME_COPY.lab.title}</Link></h3>
              <p>{HOME_COPY.lab.text}</p>
              <figure className={styles.labShot} data-theme-scope="dark">
                <img src="/assets/site/neurofly-lab-preview.webp" width={1294} height={718} loading="lazy" decoding="async" alt="Screenshot of the NeuroFly 3D laboratory: a fruit fly model standing inside the transparent enclosure on a laboratory bench." />
                <figcaption>Actual Lab viewport · static capture</figcaption>
              </figure>
              <p className={styles.cardNote}>{HOME_COPY.lab.note}</p>
            </li>
          </ul>
          <p className={styles.after}>All results here are <KindBadge kind="model-state" /> and <KindBadge kind="not-evaluated" />. <Link prefetch={false} href="/scenarios">See every scenario</Link></p>
        </section>

        <section className={styles.section} aria-labelledby="paths-title">
          <h2 id="paths-title">Choose your path</h2>
          <div className={styles.paths}>
            <div className={styles.path}>
              <h3>I’m new</h3>
              <p>Watch one recorded run, with no setup and no jargon before the first frame.</p>
              <Link prefetch={false} className={styles.primary} href={FIRST_SCENARIO_HREF}>Watch the looming scenario</Link>
            </div>
            <div className={styles.path}>
              <h3>I’m a researcher</h3>
              <p>Start from what is and is not established, then follow each reason to its report.</p>
              <div className={styles.actions}>
                <Link prefetch={false} className={styles.quiet} href={STATUS_HREF}>Status and limits</Link>
                <Link prefetch={false} className={styles.quiet} href={EXPERIMENTS_HREF}>{EXPERIMENTS_LABEL}</Link>
              </div>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter tone="auto" />
    </div>
  );
}
