import type { Metadata } from "next";
import Link from "next/link";
import { SiteHeader, SiteFooter } from "@/components/site/SiteChrome";
import { ActionLink, Arrow, SectionHeading } from "@/components/site/SitePrimitives";
import { SpecimenVisual } from "@/components/site/SpecimenVisual";
import { LabPreview } from "@/components/site/LabPreview";
import { ScienceArchitecture } from "@/components/science/ScienceArchitecture";
import { LAB_HREF, SCIENCE_HREF } from "@/components/site/siteContent";
import { experimentMetadata } from "@/lib/scenarioPresentation";

export const metadata: Metadata = {
  title: "Science & Project · NeuroFly",
  description: "Understand how selected MaleCNS connections, explicit neural models and engineering movement come together in NeuroFly. Explore the evidence, assumptions and limits.",
  openGraph: { title: "The science behind a digital organism · NeuroFly", description: "Biological connectivity. Explicit models. Observable computational behaviour.", type: "website", siteName: "NeuroFly", locale: "en_GB" },
};

const examples = [
  { id: "BASELINE_CONTROL", title: "Begin with stillness", description: "A neutral reference asks what the model does without an effective stimulus. A stationary body is a meaningful control outcome." },
  { id: "HORIZONTAL_MOTION_NEURAL_VALIDATION", title: "Motion into neural activity", description: "A controlled horizontal-motion descriptor passes through the selected HS/DNp15 model. The readout is neural only: this preset defines no body mapping." },
  { id: "EXPLORATORY_COURSE_CONTROL", title: "A turn through feedback", description: "An orientation perturbation changes model-space visual feedback. Inspect the bounded closed loop, including its residual orientation offset. No translation is simulated." },
] as const;

export default function SciencePage() {
  return <div className="nf-site nf-science-page">
    {/* Match the existing homepage fallback for the inherited streaming boundary. */}
    <noscript><style>{`body > [hidden]:has(> .nf-science-page) { display: block !important; }
      body:has(> [hidden] > .nf-science-page) > .app-shell { display: none !important; }`}</style></noscript>
    <a className="nf-skip-link" href="#science-main">Skip to content</a>
    <SiteHeader activeHref="/science" />
    <main id="science-main" tabIndex={-1}>
      <section className="science-hero nf-container" aria-labelledby="science-hero-title">
        <div className="science-hero-copy">
          <p className="nf-eyebrow"><span className="nf-small-dot" aria-hidden="true" /> Science &amp; project</p>
          <h1 id="science-hero-title">The science behind<br /><span>a digital organism.</span></h1>
          <p>How does a connection become a turn?</p>
          <p>NeuroFly brings selected biological connectivity into an explicit computational model, then makes its behaviour visible in an interactive world.</p>
          <div className="nf-actions"><ActionLink href={LAB_HREF}>Enter the Lab</ActionLink><a href="#architecture" className="nf-button nf-button--quiet">Follow the model <Arrow /></a></div>
        </div>
        <SpecimenVisual variant="hero" />
        <div className="science-reading-key" aria-label="Three layers of evidence"><span><i aria-hidden="true" /> Biological structure</span><span><i aria-hidden="true" /> Explicit modelling</span><span><i aria-hidden="true" /> Computational behaviour</span></div>
      </section>

      <nav className="science-contents nf-container" aria-label="On this page"><a href="#architecture">The loop</a><a href="#foundations">Data &amp; model</a><a href="#evidence">Experiments</a><a href="#methodology">Methodology</a><a href="#limits">Limits &amp; sources</a></nav>

      <section id="architecture" className="science-section nf-container" aria-labelledby="architecture-title">
        <div className="science-section-intro"><SectionHeading label="01 / From connection to behaviour" id="architecture-title">A loop you can<br />look inside.</SectionHeading><p>The environment changes the input. The model changes the turn. Movement changes the next observation. Each part has a different scientific role.</p></div>
        <ScienceArchitecture />
      </section>

      <section id="foundations" className="science-source" aria-labelledby="foundations-title">
        <div className="nf-container">
          <div className="science-section-intro"><SectionHeading label="02 / The evidence and the choices" id="foundations-title">Biology is the starting point.<br />The model makes choices.</SectionHeading></div>
          <div className="science-distinction">
            <article data-claim="source"><span className="science-evidence-label">From biological data</span><h3>A record of connections.</h3><p>MaleCNS reconstructs the male fruit fly’s central nervous system. Its data include neuron annotations and synaptic relationships. NeuroFly uses selected records pinned to <code>male-cns:v1.0</code>.</p><p>These records help establish which identified cells connect. They do not, on their own, specify an executable nervous system.</p><a className="nf-text-link" href="https://male-cns.janelia.org/download/">Explore the official MaleCNS source <Arrow /></a></article>
            <article data-claim="states"><span className="science-evidence-label science-evidence-label--model">From computational modelling</span><h3>A rule for what changes.</h3><p>Inputs, state variables, timescales and transfer rules are explicit model choices. In the HS/DNp15 path, continuous, dimensionless proxy states evolve through smoothing rules.</p><p>Those values are computed model activity. They are not measured membrane voltages, calcium signals or biological spike recordings.</p></article>
          </div>
          <p className="science-source-note" data-claim="structure">In the selected HS/DNp15 model, structural contact counts are retained as provenance. They are not used as measured physiological connection strengths.</p>
        </div>
      </section>

      <section className="science-section nf-container science-circuit" aria-labelledby="circuit-title" data-claim="circuit">
        <div><SectionHeading label="03 / Selected, not exhaustive" id="circuit-title">A small circuit.<br />An inspectable model.</SectionHeading><p className="science-lead">The current steering path keeps six HS source identities and two DNp15 target identities distinct.</p></div>
        <div className="science-circuit-copy"><p>Three HS proxies on each side feed that side’s DNp15 proxy through the selected chemical feedforward motif. A right–left readout can then be projected into a simulated turn.</p><p>NeuroFly also implements LC4/LPLC2 → DNp01 models for its looming experiments. These are separate circuit models with their own state and output contracts.</p><details className="science-disclosure"><summary>Look closer at the steering assumptions</summary><div><p>The HS/DNp15 kernel averages the three selected source states per side and updates source and target states from the previous numerical boundary. Broader recurrent, inhibitory and electrical network dynamics are outside this selected motif.</p><p>The ground observer reduces completed body motion relative to geometric landmarks into bounded side descriptors. It does not reconstruct a calibrated retinal image.</p><p>The neural contribution is an engineering yaw projection. Propulsion and wall response have separate engineering authorities.</p></div></details></div>
      </section>

      <section className="science-body nf-container" aria-labelledby="body-title">
        <div className="science-body-media"><LabPreview /><p data-claim="body">An actual Lab capture. The visible specimen is an artistic 3D asset, not anatomy reconstructed from MaleCNS.</p></div>
        <div className="science-body-copy"><SectionHeading label="04 / A body in a world" id="body-title">What you see.<br />What moves it.</SectionHeading>
          <ol className="science-body-layers">
            <li data-claim="navigation"><span>01</span><div><h3>Engineering movement</h3><p>Explore combines forward propulsion, neural heading influence and geometric boundary response in a 30-second run. Contact constraints and inward steering keep the accepted pose inside the enclosure.</p></div></li>
            <li data-claim="gait"><span>02</span><div><h3>Articulated presentation</h3><p>The leg animation follows completed body movement. It makes walking visible; it does not generate propulsion or simulate muscle forces.</p></div></li>
            <li data-claim="flight"><span>03</span><div><h3>Separate flight experiments</h3><p>Research modes combine an engineering flight plant with selected neural yaw influence. Their motor mapping is an experimental engineering hypothesis, without physiological or aerodynamic calibration.</p></div></li>
          </ol>
          <details className="science-disclosure" data-claim="shadow"><summary>Where does DNg100/T1 fit?</summary><div><p>The experimental DNg100/T1 pathway retains its shadow-only status. It is not the applied ground motor controller in Explore.</p></div></details>
        </div>
      </section>

      <section id="evidence" className="science-section nf-container" aria-labelledby="evidence-title" data-claim="experiments">
        <div className="science-section-intro"><SectionHeading label="05 / Ask a bounded question" id="evidence-title">Different experiments.<br />Different evidence.</SectionHeading><p>The five canonical presets answer specific computational questions. Their millisecond scientific timelines are distinct from the Lab’s live exploration.</p></div>
        <div className="science-examples">{examples.map(example => <article key={example.id}><div className="science-example-kind"><span>{experimentMetadata[example.id].kind}</span><strong>{experimentMetadata[example.id].duration}</strong><small>Scientific duration</small></div><div><h3>{example.title}</h3><p>{example.description}</p></div><Link prefetch={false} href={`/scenarios/${example.id}`} aria-label={`Inspect ${example.title}`} className="science-example-link">Inspect <Arrow /></Link></article>)}</div>
        <Link prefetch={false} className="nf-text-link" href="/scenarios">Explore all five experiments <Arrow /></Link>
      </section>

      <section id="methodology" className="science-methodology" aria-labelledby="methodology-title">
        <div className="nf-container science-method-grid"><div><SectionHeading label="06 / Make the result inspectable" id="methodology-title">A result needs<br />a trail of evidence.</SectionHeading><p>Reproducibility is part of the experiment’s contract. It is not a score for biological realism.</p></div><ol className="science-method-list">
          <li data-claim="reproducibility"><span>Define</span><div><h3>Keep the conditions explicit.</h3><p>Versioned configurations record source identities, model assumptions, initial state and scientific time steps. Current Explore uses deterministic rules without random drive.</p></div></li>
          <li data-claim="integrity"><span>Reconstruct</span><div><h3>Check more than a file hash.</h3><p>Supported replays recompute the authoritative model from recorded configuration and events. Validators compare reconstructed outputs under the relevant contract; hashes also identify and protect the stored payloads.</p></div></li>
          <li data-claim="availability"><span>Interpret</span><div><h3>Keep data and display accountable.</h3><p>The recorded archive is a separate read-only collection. If its integrity checks fail, the interface withholds results. Lab sessions are not automatically saved there. Some scientific workflows require explicitly supplied external source data.</p></div></li>
        </ol></div>
      </section>

      <section id="limits" className="science-section nf-container" aria-labelledby="limits-title">
        <div className="science-limits" data-claim="limits"><div><p className="nf-eyebrow">07 / Read the boundary</p><h2 id="limits-title">A computational experiment.<br /><span>An explicit scope.</span></h2><p>NeuroFly is a computational experimental system, not a complete biological reconstruction.</p></div><ul><li>Selected circuits run here. The full MaleCNS nervous system does not.</li><li>Visible movement is not evidence of consciousness, sentience or genuine learning.</li><li>Engineering body motion and animation do not establish biological muscle control or physiological flight.</li><li data-claim="empirical">The empirical HS/DNp15 audit did not establish agreement with published calcium responses. Stimulus and observable incompatibilities remain; the external visual-motion adapter is contract-only.</li></ul></div>
      </section>

      <section className="science-references nf-container" aria-labelledby="references-title">
        <div><p className="nf-eyebrow">Sources &amp; methodology</p><h2 id="references-title">Follow the evidence.</h2><p>Primary sources describe the biology. Project reports document the implemented models, assumptions and limits.</p></div>
        <ol><li><a href="https://male-cns.janelia.org/download/"><span>01</span><span>MaleCNS dataset &amp; access<small>Official annotations, connectivity and source data</small></span><Arrow /></a></li><li><a href="https://www.nature.com/articles/s41593-025-01948-9"><span>02</span><span>Erginkaya et al. · Nature Neuroscience, 2025<small>Primary research on optic-flow processing; background, not model validation</small></span><Arrow /></a></li><li><a href="https://github.com/a104174/NeuroFly/blob/main/docs/science/hs_dnp15_neural_validation.md"><span>03</span><span>The selected HS/DNp15 model<small>Source identities, equations and explicit assumptions</small></span><Arrow /></a></li><li><a href="https://github.com/a104174/NeuroFly/blob/main/docs/science/experiment_artifact_contract.md"><span>04</span><span>Experiment integrity &amp; replay<small>Portable records, validation and reconstruction</small></span><Arrow /></a></li><li><a href="https://github.com/a104174/NeuroFly/blob/main/docs/science/empirical_hs_dnp15_response_benchmark_v9_2.md"><span>05</span><span>The empirical comparison boundary<small>Why the published observations are not treated as matching model outputs</small></span><Arrow /></a></li></ol>
      </section>

      <section className="science-invitation nf-container" aria-labelledby="science-invitation-title"><div><p className="nf-eyebrow">From explanation to exploration</p><h2 id="science-invitation-title">See the model<br />in its world.</h2></div><div><ActionLink href={LAB_HREF}>Enter the Lab</ActionLink><Link prefetch={false} className="nf-text-link" href="/visual-lab/arena/research">Open the research tools <Arrow /></Link><a className="science-documentation-link" href={SCIENCE_HREF}>Browse scientific documentation ↗</a></div></section>
    </main>
    <SiteFooter />
  </div>;
}
