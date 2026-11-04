import Link from "next/link";
import type { ReactNode } from "react";
import { EXPERIMENTS_LABEL } from "@/components/site/siteContent";
import { ButtonLink, KindBadge, KindGlyph, ProvenanceLabel, Readout } from "@/components/ui";
import { MALECNS_RELEASE, type DataKind } from "@/content/science-copy";
import type { DNp01Summary, ExperimentSummary, PopulationSummary } from "@/lib/neuroflyClient";
import { isEngineeringTest, recordedRunPurpose } from "@/lib/recordedExperimentPresentation";
import styles from "./ExperimentDetail.module.css";

/** Top bar of the page: back link, status and the primary action (section 1 of the brief). */
export function ExperimentActions({ summary }: { summary: ExperimentSummary }) {
  return (
    <div className={styles.bar}>
      <Link href="/experiments" prefetch={false} className={styles.back}>← Experiments</Link>
      <div className={styles.barRight}>
        <KindBadge kind="not-evaluated" />
        {isEngineeringTest(summary.experiment_config_id) ? <span className={styles.tag}><KindGlyph kind="unavailable" size={11} /> {EXPERIMENTS_LABEL}</span> : null}
        <span className={styles.scenario}>Scenario: <span>Not recorded</span></span>
        <ButtonLink href={`/experiments/${summary.artifact_id}/cockpit`}>Open Cockpit</ButtonLink>
      </div>
    </div>
  );
}

export function ExperimentLead({ summary }: { summary: ExperimentSummary }) {
  const purpose = recordedRunPurpose(summary.experiment_config_id);
  return (
    <>
      <p>
        This run applied the {summary.pathway_condition.toLowerCase()} condition to the selected LC4 and LPLC2 → DNp01 circuit,
        for {summary.duration_ms} ms in steps of {summary.dt_ms} ms.
      </p>
      <p>{purpose ?? "It has not been compared with real fly data."}</p>
    </>
  );
}

export function DetailSection({ id, title, kind, children }: { id: string; title: string; kind?: DataKind; children: ReactNode }) {
  return (
    <section className={styles.section} aria-labelledby={id}>
      <div className={styles.sectionHead}>
        <h2 id={id}>{title}</h2>
        {kind ? <KindBadge kind={kind} /> : null}
      </div>
      {children}
    </section>
  );
}

function SetupRow({ kind, label, children }: { kind: DataKind; label: string; children: ReactNode }) {
  return (
    <div className={styles.setupRow}>
      <dt><KindGlyph kind={kind} size={12} /> {label}</dt>
      <dd>{children}</dd>
    </div>
  );
}

export function SetupSection({ summary }: { summary: ExperimentSummary }) {
  const p = summary.free_parameters;
  return (
    <DetailSection id="setup" title="Setup">
      <dl className={styles.setup}>
        <SetupRow kind="structural" label="Circuit (structural)">
          {summary.dataset}. {summary.candidate.identifier} v{summary.candidate.version}, graph scope {summary.graph_scope_id}.
        </SetupRow>
        <SetupRow kind="model-assumption" label="Stimulus encoder (model assumption)">
          {summary.encoder.id} {summary.encoder.version}. Condition: {summary.pathway_condition}.
        </SetupRow>
        <SetupRow kind="model-assumption" label="Neuron model (model assumption)">
          {summary.neural_model.id} {summary.neural_model.version}.
        </SetupRow>
        <SetupRow kind="unavailable" label="Body model">
          Not recorded in this experiment summary.
        </SetupRow>
      </dl>
      <h3 className={styles.sub}>Free parameters <KindBadge kind="model-assumption" /></h3>
      <div className={styles.readouts}>
        <Readout kind="model-assumption" label="G_LC4" value={p.lc4_gain_mv_eq} unit="mV_eq" />
        <Readout kind="model-assumption" label="G_LPLC2" value={p.lplc2_gain_mv_eq} unit="mV_eq" />
        <Readout kind="model-assumption" label="ω_half" value={p.omega_half_rad_per_s} unit="rad/s" />
        <Readout kind="model-assumption" label="θ_half" value={p.theta_half_rad} unit="rad" />
        <Readout kind="model-assumption" label="k_syn" value={p.k_syn_mv_per_contact} unit="mV_eq/contact" />
      </div>
    </DetailSection>
  );
}

function ms(value: number | null) {
  return value === null ? ({ state: "not-recorded" } as const) : ({ value, unit: "ms" } as const);
}

function PopulationResults({ population }: { population: PopulationSummary }) {
  const first = ms(population.first_spike_time_ms);
  return (
    <div className={styles.group}>
      <h3>{population.neuron_type} <span className={styles.count}>{population.body_count} bodies</span></h3>
      <div className={styles.readouts}>
        <Readout kind="model-state" label="Population spikes" value={population.total_spike_count} unit="dimensionless" />
        <Readout kind="model-state" label="Bodies spiking" value={population.bodies_that_spike} unit="dimensionless" />
        {"state" in first ? <Readout kind="model-state" label="First spike" state="not-recorded" /> : <Readout kind="model-state" label="First spike" value={first.value} unit="ms" />}
        <Readout kind="model-state" label="Feature peak" value={population.peak_normalized_feature} digits={4} unit="dimensionless" />
        <Readout kind="model-state" label="Drive peak" value={population.peak_drive_mveq} digits={4} unit="mV_eq" />
      </div>
    </div>
  );
}

function DnpResults({ item }: { item: DNp01Summary }) {
  const first = ms(item.first_spike_time_ms);
  return (
    <div className={styles.group}>
      <h3>DNp01 · {item.body_id} <span className={styles.count}>{item.soma_side ?? "side not recorded"}</span></h3>
      <div className={styles.readouts}>
        <Readout kind="model-state" label="Spike count" value={item.total_spike_count} unit="dimensionless" />
        {"state" in first ? <Readout kind="model-state" label="First spike" state="not-recorded" /> : <Readout kind="model-state" label="First spike" value={first.value} unit="ms" />}
        <Readout kind="model-state" label="Peak membrane" value={item.peak_membrane_mv} digits={4} unit="mV_eq" />
        <Readout kind="model-state" label="Peak synaptic state" value={item.peak_synaptic_state_mveq} digits={4} unit="mV_eq" />
        <Readout kind="model-state" label="Delivered events" value={item.delivered_event_count} unit="dimensionless" />
        <Readout kind="model-state" label="Model increment sum" value={item.model_increment_sum_mveq} digits={4} unit="mV_eq" />
      </div>
    </div>
  );
}

export function ResultsSection({ summary }: { summary: ExperimentSummary }) {
  return (
    <DetailSection id="results" title="Results" kind="model-state">
      <p className={styles.note}>Every number below is model state. Counts are dimensionless. Units ending in _eq are model-equivalent, not measured.</p>
      <PopulationResults population={summary.populations.LC4} />
      <PopulationResults population={summary.populations.LPLC2} />
      {summary.dnp01.map((item) => <DnpResults key={item.body_id} item={item} />)}
    </DetailSection>
  );
}

export function LimitsSection() {
  return (
    <DetailSection id="limits" title="What this does not show">
      <ul className={styles.list}>
        <li>These are model readouts. They are not motor output or behavioural predictions.</li>
        <li>No comparison with real fly data has been made, so the result is Not evaluated.</li>
        <li>Structural contact counts are connectome metadata. They are not measured synaptic strength.</li>
        <li>Units ending in _eq are model-equivalent. They were not measured in a fly.</li>
      </ul>
      <p className={styles.note}>See <Link href="/science/status" prefetch={false}>what is and is not established</Link>.</p>
    </DetailSection>
  );
}

export function DataSection({ summary }: { summary: ExperimentSummary }) {
  return (
    <DetailSection id="data" title="Data">
      <ProvenanceLabel
        variant="card"
        kind="model-state"
        source={`${MALECNS_RELEASE}, ${summary.dataset}`}
        modelVersion={`${summary.neural_model.id} ${summary.neural_model.version}`}
        status="NOT_EVALUATED"
        artifactId={summary.artifact_id}
      />
      <dl className={styles.ids}>
        <div><dt>Config ID</dt><dd><code>{summary.experiment_config_id}</code></dd></div>
        <div><dt>Result ID</dt><dd><code>{summary.result_id}</code></dd></div>
        <div><dt>Config checksum</dt><dd><code>{summary.experiment_config_sha256}</code></dd></div>
      </dl>
    </DetailSection>
  );
}
