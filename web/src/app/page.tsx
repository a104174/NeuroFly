import type { Metadata } from "next";
import Link from "next/link";
import { SiteHeader, SiteFooter } from "@/components/site/SiteChrome";
import { ActionLink, Arrow, FeatureIcon, SectionHeading } from "@/components/site/SitePrimitives";
import { SpecimenVisual } from "@/components/site/SpecimenVisual";
import { LabPreview } from "@/components/site/LabPreview";
import { LAB_HREF, SCIENCE_PAGE_HREF } from "@/components/site/siteContent";

export const metadata: Metadata = {
  title: "NeuroFly — A digital fly. A new way to explore behaviour.",
  description: "Explore a connectome-informed digital fly in an interactive 3D laboratory. Observe model neural steering, compare simulation runs and replay experiments.",
  openGraph: {
    title: "NeuroFly — A digital fly. A new way to explore behaviour.",
    description: "An interactive laboratory for exploring selected neural circuits and simulated movement. Selected connectivity. Explicit assumptions. Reproducible experiments.",
    siteName: "NeuroFly", type: "website", locale: "en_GB",
  },
};

export default function HomePage() {
  return (
    <div className="nf-site">
      {/* Reveal server-rendered home content when JS cannot complete the inherited streaming boundary. */}
      <noscript><style>{`body > [hidden]:has(> .nf-site) { display: block !important; }
        body:has(> [hidden] > .nf-site) > .app-shell { display: none !important; }`}</style></noscript>
      <a className="nf-skip-link" href="#main-content">Skip to content</a>
      <SiteHeader />
      <main id="main-content" tabIndex={-1}>
        <section className="nf-hero nf-container" aria-labelledby="hero-title">
          <div className="nf-hero-copy">
            <p className="nf-eyebrow"><span className="nf-small-dot" aria-hidden="true" /> Where biology meets simulation</p>
            <h1 id="hero-title"><span>A digital fly.</span><span>A new way to</span><span className="nf-accent">explore behaviour.</span></h1>
            <p className="nf-hero-description">Step into a laboratory where selected neural circuits meet a digital organism. Change the conditions. Observe the movement. Explore the connection.</p>
            <div className="nf-actions"><ActionLink href={LAB_HREF}>Enter the Lab</ActionLink><ActionLink href={SCIENCE_PAGE_HREF} variant="quiet">Explore the Science</ActionLink></div>
            <p className="nf-hero-note">Interactive environments. Traceable experiments.</p>
          </div>
          <SpecimenVisual variant="hero" />
          <div className="nf-proof-strip" aria-label="Platform foundations">
            <div><span>Informed by biology</span><strong>Selected MaleCNS connections</strong></div>
            <div><span>Made to explore</span><strong>An interactive 3D laboratory</strong></div>
            <div><span>Built to be examined</span><strong>Replay, compare, understand</strong></div>
          </div>
        </section>

        <section id="about" className="nf-section nf-container" aria-labelledby="about-title">
          <div className="nf-intro-grid">
            <SectionHeading label="01 / Meet NeuroFly" id="about-title">Small organism.<br />Big questions.</SectionHeading>
            <div className="nf-intro-copy"><p>How does a change in neural activity become a change in movement?</p><p>NeuroFly makes that relationship something you can explore. A digital fly, a controllable environment and selected connectome-informed models come together in one observable experiment.</p></div>
          </div>
          <div className="nf-principles">
            <article><FeatureIcon kind="space" /><h3>A world to move through</h3><p>Inspect a digital specimen and explore its simulated movement inside a 3D laboratory.</p></article>
            <article><FeatureIcon kind="circuit" /><h3>A connection to real science</h3><p>Selected MaleCNS connections inform the circuit structure. Dynamics and movement mappings use explicit modelling assumptions.</p></article>
            <article><FeatureIcon kind="replay" /><h3>An experiment you can revisit</h3><p>Follow trajectories, inspect model responses and compare reproducible simulation runs.</p></article>
          </div>
        </section>

        <section id="explore" className="nf-section nf-container nf-capabilities" aria-labelledby="explore-title">
          <div className="nf-section-top"><SectionHeading label="02 / Your field of exploration" id="explore-title">Look closer.<br />Try something different.</SectionHeading><p>From the organism to the experiment,<br />there is more than one way in.</p></div>
          <div className="nf-feature-grid">
            <Link prefetch={false} href={LAB_HREF} className="nf-feature-card nf-feature-main">
              <div className="nf-feature-top"><span className="nf-card-label">The laboratory</span><Arrow /></div>
              <LabPreview />
              <div className="nf-feature-copy"><h3>A space for curiosity.</h3><p>Explore walking and flight modes, adjust visual conditions and watch how the simulation responds.</p><span className="nf-text-link">Explore the 3D Lab <Arrow /></span></div>
            </Link>
            <Link prefetch={false} href="/scenarios" className="nf-feature-card nf-feature-steering"><div className="nf-feature-top"><FeatureIcon kind="circuit" /><Arrow /></div><div><h3>Observe neural steering.</h3><p>Follow how selected HS/DNp15 model activity contributes to simulated orientation.</p><span className="nf-card-label">Neural model experiments</span></div></Link>
            <Link prefetch={false} href="/visual-lab/fly" className="nf-feature-card nf-feature-specimen"><div className="nf-feature-top"><FeatureIcon kind="space" /><Arrow /></div><div><h3>Meet the digital fly.</h3><p>Orbit, zoom and inspect the specimen. Discover articulated leg and wing presentation in the Lab.</p><span className="nf-card-label">The organism, up close</span></div></Link>
            <Link prefetch={false} href={LAB_HREF} className="nf-feature-card nf-feature-replay"><FeatureIcon kind="replay" /><div><h3>Replay. Compare. Ask again.</h3><p>Reconstruct recorded sessions and compare neural steering ON and OFF in supported laboratory modes.</p></div><Arrow /></Link>
          </div>
        </section>

        <section className="nf-process" aria-labelledby="process-title">
          <div className="nf-container">
            <div className="nf-section-top"><SectionHeading label="03 / From observation to action" id="process-title">How a turn takes shape.</SectionHeading><p>A visible pathway through the model.<br />Every stage has a defined role.</p></div>
            <ol className="nf-process-steps">
              <li><div className="nf-process-number">01 <span aria-hidden="true">→</span></div><FeatureIcon kind="space" /><h3>Environment</h3><p>The fly’s pose and visual scene provide geometric sensory observations.</p><span className="nf-process-tag">Observe the conditions</span></li>
              <li><div className="nf-process-number">02 <span aria-hidden="true">→</span></div><FeatureIcon kind="circuit" /><h3>Neural model</h3><p>Selected connectome-informed dynamics process the modelled inputs.</p><span className="nf-process-tag">Follow the response</span></li>
              <li><div className="nf-process-number">03 <span aria-hidden="true">↗</span></div><FeatureIcon kind="movement" /><h3>Behaviour</h3><p>An engineering projection of the model readout influences simulated movement.</p><span className="nf-process-tag">See what changes</span></li>
            </ol>
            <p className="nf-process-caveat">A computational experiment with explicit assumptions, rather than a complete physiological model of a fly.</p>
          </div>
        </section>

        <section className="nf-section nf-container" aria-labelledby="lab-title">
          <div className="nf-lab-preview">
            <div className="nf-lab-copy"><SectionHeading label="04 / Inside the Lab" id="lab-title">Less reading.<br />More exploring.</SectionHeading><p>See the organism in its environment. Start a supported simulation, follow its trajectory and inspect what happens when the conditions change.</p><ul><li>Walking and flight modes</li><li>Articulated movement and camera inspection</li><li>Neural telemetry and reproducible comparisons</li></ul><ActionLink href={LAB_HREF} variant="quiet">Launch the Laboratory</ActionLink></div>
            <LabPreview />
          </div>
        </section>

        <section id="science" className="nf-section nf-container nf-science" aria-labelledby="science-title">
          <div><SectionHeading label="05 / The scientific foundation" id="science-title">Grounded in connectivity.<br /><span className="nf-secondary-heading">Open about the assumptions.</span></SectionHeading><p className="nf-science-intro">The MaleCNS connectome provides structural evidence for selected neural connections. NeuroFly uses that evidence to build bounded, inspectable circuit models.</p><Link prefetch={false} className="nf-text-link" href={SCIENCE_PAGE_HREF}>Explore the science <Arrow /></Link></div>
          <div className="nf-science-notes"><article><span className="nf-small-dot" aria-hidden="true" /><div><h3>What comes from biology</h3><p>Selected neuron identities and reconstructed connections from MaleCNS.</p></div></article><article><span className="nf-small-dot nf-warm-dot" aria-hidden="true" /><div><h3>What comes from modelling</h3><p>Neural dynamics, sensory reductions and engineering projections into movement. These involve assumptions, not physiological calibration.</p></div></article><p>NeuroFly simulates selected circuits. It is not a whole-fly physiological emulation, and the visual specimen is an artistic 3D asset.</p></div>
        </section>

        <section className="nf-final-cta" aria-labelledby="invitation-title"><div className="nf-container"><p className="nf-eyebrow">Curiosity is a good starting point.</p><h2 id="invitation-title">Step inside<br />the experiment.</h2><ActionLink href={LAB_HREF}>Enter NeuroFly Lab</ActionLink><p>No setup. Open the Lab in your browser.</p></div></section>
      </main>
      <SiteFooter />
    </div>
  );
}
