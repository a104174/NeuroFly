import type { Metadata } from "next";
import Link from "next/link";
import { ArticleSection, ArticleShell } from "@/components/science/ArticleShell";
import { ScienceArchitecture } from "@/components/science/ScienceArchitecture";
import { StageFigure } from "@/components/science/StageFigure";
import { KindBadge, KindGlyph } from "@/components/ui";
import { AUTHOR_HREF, AUTHOR_NAME, LAB_HREF, EXPERIMENTS_HREF, EXPERIMENTS_LABEL, MALECNS_HREF, SCIENCE_HREF, STATUS_HREF } from "@/components/site/siteContent";
import { CAPABILITIES, CAPABILITY_GROUPS, DATA_KINDS, KIND_COPY, MALECNS_RELEASE, OPEN_QUESTIONS } from "@/content/science-copy";
import { experimentMetadata } from "@/lib/scenarioPresentation";
import styles from "@/components/science/Article.module.css";

export const metadata: Metadata = {
  title: "Science · NeuroFly",
  description: "What NeuroFly models, where the data comes from, how the model works, what each kind of number means and what has not been done.",
  openGraph: { title: "The science behind NeuroFly", description: "Selected connectivity. Explicit models. Observable computational behaviour.", type: "website", siteName: "NeuroFly", locale: "en_GB" },
};

const CONTENTS = [
  { id: "scope", label: "What NeuroFly models" },
  { id: "data", label: "Where the data comes from" },
  { id: "model", label: "How the model works" },
  { id: "numbers", label: "What each number means" },
  { id: "limits", label: "What has not been done" },
  { id: "capabilities", label: "What works today" },
  { id: "sources", label: "Sources" },
] as const;

const examples = [
  { id: "BASELINE_CONTROL", title: "Begin with stillness", description: "A neutral reference asks what the model does without an effective stimulus. A stationary body is a meaningful control outcome." },
  { id: "HORIZONTAL_MOTION_NEURAL_VALIDATION", title: "Motion into neural activity", description: "A controlled horizontal-motion descriptor passes through the selected HS/DNp15 model. The readout is neural only: this preset defines no body mapping." },
  { id: "EXPLORATORY_COURSE_CONTROL", title: "A turn through feedback", description: "An orientation perturbation changes model-space visual feedback. Inspect the bounded closed loop, including its residual orientation offset. No translation is simulated." },
] as const;

const REFERENCES = [
  { href: "https://male-cns.janelia.org/download/", title: "MaleCNS dataset & access", note: "Official annotations, connectivity and source data" },
  { href: "https://www.nature.com/articles/s41593-025-01948-9", title: "Erginkaya et al. · Nature Neuroscience, 2025", note: "Primary research on optic-flow processing; background, not evidence that the model matches real flies" },
  { href: "https://github.com/a104174/NeuroFly/blob/main/docs/science/hs_dnp15_neural_validation.md", title: "The selected HS/DNp15 model", note: "Source identities, equations and explicit assumptions" },
  { href: "https://github.com/a104174/NeuroFly/blob/main/docs/science/experiment_artifact_contract.md", title: "Experiment integrity & replay", note: "Portable records, integrity checks and reconstruction" },
  { href: "https://github.com/a104174/NeuroFly/blob/main/docs/science/empirical_hs_dnp15_response_benchmark_v9_2.md", title: "The empirical comparison boundary", note: "Why the published observations are not treated as matching model outputs" },
] as const;

export default function SciencePage() {
  return (
    <ArticleShell
      eyebrow="Science"
      title="The science behind NeuroFly"
      contents={CONTENTS}
      lead={<>
        <p>How does a connection become a turn?</p>
        <p>NeuroFly brings selected biological connectivity into an explicit computational model, then makes its behaviour visible in an interactive world.</p>
      </>}
    >
      <ArticleSection id="scope" title="What NeuroFly models">
        <p className={styles.lede} data-claim="scope">
          NeuroFly models two selected circuits from the {MALECNS_RELEASE} connectome: the looming circuit, where the visual neurons LC4 and LPLC2 feed DNp01 (313 bodies), and the HS → DNp15 steering circuit (8 bodies). They are separate models with their own states and outputs, so their counts are not added together. Neither is a whole brain, and no result has been compared with data from real flies.
        </p>
        <div className={styles.actions}>
          <KindBadge kind="structural" explain />
          <KindBadge kind="model-assumption" explain />
          <KindBadge kind="model-state" explain />
        </div>
        <p>Selected circuits run here. The full MaleCNS nervous system does not. The three labels above appear next to every number on the site, so you can tell wiring from modelling from output.</p>
      </ArticleSection>

      <ArticleSection id="data" title="Where the data comes from">
        <div className={styles.pair}>
          <article className={styles.card} data-claim="source">
            <span className={styles.cardLabel} data-kind="structural"><KindGlyph kind="structural" size={11} /> From biological data</span>
            <h3>A record of connections.</h3>
            <p>MaleCNS reconstructs the male fruit fly’s central nervous system. Its data include neuron annotations and synaptic relationships. NeuroFly uses selected records pinned to <code>male-cns:v1.0</code>.</p>
            <p>These records help establish which identified cells connect. They do not, on their own, specify an executable nervous system.</p>
            <p><a href={MALECNS_HREF}>Explore the official MaleCNS source <span aria-hidden="true">↗</span></a></p>
          </article>
          <article className={styles.card} data-claim="states">
            <span className={styles.cardLabel} data-kind="model-assumption"><KindGlyph kind="model-assumption" size={11} /> From computational modelling</span>
            <h3>A rule for what changes.</h3>
            <p>Inputs, state variables, timescales and transfer rules are explicit model choices. In the HS/DNp15 path, continuous, dimensionless proxy states evolve through smoothing rules.</p>
            <p>Those values are computed model activity. They are not measured membrane voltages, calcium signals or biological spike recordings.</p>
          </article>
        </div>
        <p data-claim="structure">In the selected HS/DNp15 model, structural contact counts are retained as provenance. They are not used as measured physiological connection strengths.</p>
      </ArticleSection>

      <ArticleSection id="model" title="How the model works">
        <h3>A small circuit. An inspectable model.</h3>
        <p data-claim="circuit">The current steering path keeps six HS source identities and two DNp15 target identities distinct. Three HS proxies on each side feed that side’s DNp15 proxy through the selected chemical feedforward motif. A right–left readout can then be projected into a simulated turn.</p>
        <p>NeuroFly also implements LC4/LPLC2 → DNp01 models for its looming scenarios. These are separate circuit models with their own state and output contracts.</p>
        <details className={styles.disclosure}>
          <summary>Look closer at the steering assumptions</summary>
          <div>
            <p>The HS/DNp15 kernel averages the three selected source states per side and updates source and target states from the previous numerical boundary. Broader recurrent, inhibitory and electrical network dynamics are outside this selected motif.</p>
            <p>The ground observer reduces completed body motion relative to geometric landmarks into bounded side descriptors. It does not reconstruct a calibrated retinal image.</p>
            <p>The neural contribution is an engineering yaw projection. Propulsion and wall response have separate engineering authorities.</p>
          </div>
        </details>
        <ScienceArchitecture />

        <h3>A body in a world</h3>
        <StageFigure kind="lab" caption={<span data-claim="body">An actual Lab capture. The visible specimen is an artistic 3D asset, not anatomy reconstructed from MaleCNS.</span>} />
        <ol className={styles.layers}>
          <li data-claim="navigation"><div><h3>Engineering movement</h3><p>Explore combines forward propulsion, neural heading influence and geometric boundary response in a 30-second run. Contact constraints and inward steering keep the accepted pose inside the enclosure.</p></div></li>
          <li data-claim="gait"><div><h3>Articulated presentation</h3><p>The leg animation follows completed body movement. It makes walking visible; it does not generate propulsion or simulate muscle forces.</p></div></li>
          <li data-claim="flight"><div><h3>Separate flight experiments</h3><p>Research modes combine an engineering flight plant with selected neural yaw influence. Their motor mapping is an experimental engineering hypothesis, without physiological or aerodynamic calibration.</p></div></li>
        </ol>
        <details className={styles.disclosure} data-claim="shadow">
          <summary>Where does DNg100/T1 fit?</summary>
          <div><p>The experimental DNg100/T1 pathway retains its shadow-only status. It is not the applied ground motor controller in Explore.</p></div>
        </details>
        <StageFigure kind="specimen" caption={<>The 3D model shown in the Lab: <i>Drosophila melanogaster</i>, artistic 3D model · male specimen.</>} />

        <h3>Different scenarios, different questions</h3>
        <p data-claim="experiments">The five canonical scenarios answer specific computational questions. Their millisecond scientific timelines are distinct from the Lab’s live exploration.</p>
        <ul className={styles.examples}>
          {examples.map((example) => (
            <li key={example.id}>
              <span className={styles.meta}><span>{experimentMetadata[example.id].kind}</span><span><strong>{experimentMetadata[example.id].duration}</strong> scientific duration</span></span>
              <h3>{example.title}</h3>
              <p>{example.description}</p>
              <p><Link prefetch={false} href={`/scenarios/${example.id}`}>Open this scenario <span aria-hidden="true">→</span></Link></p>
            </li>
          ))}
        </ul>
        <p data-claim="circuitcheck">A “circuit check” runs the model through the selected circuit and confirms that it executes as specified. Some circuit checks are preregistered, such as the HS → DNp15 check. A circuit check is not biological validation: it does not compare the result with real fly data.</p>
        <p><Link prefetch={false} href="/scenarios">Explore all five scenarios <span aria-hidden="true">→</span></Link></p>

        <h3>A result needs a trail of evidence</h3>
        <p>Reproducibility is part of each run’s contract. It is not a score for biological realism.</p>
        <ol className={styles.layers}>
          <li data-claim="reproducibility"><div><h3>Define: keep the conditions explicit.</h3><p>Versioned configurations record source identities, model assumptions, initial state and scientific time steps. Current Explore uses deterministic rules without random drive.</p></div></li>
          <li data-claim="integrity"><div><h3>Reconstruct: check more than a file hash.</h3><p>Supported replays recompute the authoritative model from recorded configuration and events. Validators compare reconstructed outputs under the relevant contract; hashes also identify and protect the stored payloads.</p></div></li>
          <li data-claim="availability"><div><h3>Interpret: keep data and display accountable.</h3><p>The recorded archive is a separate read-only collection. If its integrity checks fail, the interface withholds results. Lab sessions are not automatically saved there. Some scientific workflows require explicitly supplied external source data.</p></div></li>
        </ol>
      </ArticleSection>

      <ArticleSection id="numbers" title="What each number means">
        <p data-claim="kinds">Where a value is labelled by kind, the label comes with a shape. Some older panels (scenario playback, parts of the Cockpit and the Lab tools) do not carry kind labels yet.</p>
        <dl className={styles.kinds}>
          {DATA_KINDS.map((kind) => (
            <div key={kind}><dt><KindBadge kind={kind} /></dt><dd>{KIND_COPY[kind].tooltip}</dd></div>
          ))}
        </dl>
        <p>Model values carry model-equivalent units such as <code>mV_eq</code>, which means the simulation produced the number. It was not measured in a fly.</p>
      </ArticleSection>

      <ArticleSection id="limits" title="What has not been done">
        <p data-claim="limits">NeuroFly is a computational experimental system, not a complete biological reconstruction.</p>
        <ul>
          <li>Selected circuits run here. The full MaleCNS nervous system does not.</li>
          <li>Visible movement is not evidence of consciousness, sentience or genuine learning.</li>
          <li>Engineering body motion and animation do not establish biological muscle control or physiological flight.</li>
          <li data-claim="empirical">The empirical HS/DNp15 audit did not establish agreement with published calcium responses. Stimulus and observable incompatibilities remain; the external visual-motion adapter is contract-only.</li>
        </ul>
        <h3>Open questions</h3>
        <p data-claim="open">The project’s own v1 status records these as unresolved:</p>
        <ul>{OPEN_QUESTIONS.map((question) => <li key={question}>{question}</li>)}</ul>
      </ArticleSection>

      <ArticleSection id="capabilities" title="What works today">
        <p>A summary of the capabilities and their state. The <Link prefetch={false} href={STATUS_HREF}>Status and limits</Link> page gives the reason for each one.</p>
        <div className={styles.tableWrap} role="region" aria-label="Capabilities, grouped by state" tabIndex={0}>
          <table className={styles.table}>
            <caption>Capabilities, grouped by state</caption>
            <thead><tr><th scope="col">Capability</th><th scope="col">State</th></tr></thead>
            <tbody>
              {CAPABILITIES.map((capability) => (
                <tr key={capability.id}><th scope="row">{capability.name}</th><td>{CAPABILITY_GROUPS[capability.group].title}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
        <p><Link prefetch={false} href={STATUS_HREF}>Read the reasons on Status and limits <span aria-hidden="true">→</span></Link></p>
      </ArticleSection>

      <ArticleSection id="sources" title="Sources">
        <p>Primary sources describe the biology. Project reports document the implemented models, assumptions and limits.</p>
        <ol className={styles.references}>
          {REFERENCES.map((reference) => (
            <li key={reference.href}><a href={reference.href}><span>{reference.title}</span><small>{reference.note}</small></a></li>
          ))}
        </ol>
        <p>Terms are defined in the <Link prefetch={false} href="/science/glossary">glossary</Link>. The full reports are in the <a href={SCIENCE_HREF}>scientific documentation <span aria-hidden="true">↗</span></a>. The one recorded run is listed as <Link prefetch={false} href={EXPERIMENTS_HREF}>{EXPERIMENTS_LABEL}</Link>.</p>
        <p data-credit="author">Created by <a href={AUTHOR_HREF}>{AUTHOR_NAME}</a>.</p>
        <div className={styles.actions}>
          <Link prefetch={false} className={styles.action} href={LAB_HREF}>Enter the Lab</Link>
          <Link prefetch={false} className={styles.actionQuiet} href="/visual-lab/arena/research">Open the research tools</Link>
        </div>
      </ArticleSection>
    </ArticleShell>
  );
}
