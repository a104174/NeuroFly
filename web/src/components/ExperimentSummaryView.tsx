import type {
  DNp01Summary,
  ExperimentSummary,
  PopulationSummary,
} from "@/lib/neuroflyClient";

function value(value: number | null, unit = "") {
  return value === null ? "None" : `${value}${unit}`;
}

function id(value: string) {
  return <code className="inline-id">{value}</code>;
}

function PopulationPanel({ population }: { population: PopulationSummary }) {
  return (
    <article className="telemetry-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">VISUAL PATHWAY</p>
          <h3>{population.neuron_type}</h3>
        </div>
        <span className="panel-index">{population.body_count} bodies</span>
      </div>
      <dl className="metric-grid metric-grid-2">
        <div>
          <dt>Population spikes</dt>
          <dd>{population.total_spike_count}</dd>
        </div>
        <div>
          <dt>Bodies spiking</dt>
          <dd>{population.bodies_that_spike}</dd>
        </div>
        <div>
          <dt>First spike</dt>
          <dd>{value(population.first_spike_time_ms, " ms")}</dd>
        </div>
        <div>
          <dt>Feature peak</dt>
          <dd>{population.peak_normalized_feature.toFixed(4)}</dd>
        </div>
        <div>
          <dt>Drive peak</dt>
          <dd>{population.peak_drive_mveq.toFixed(4)} mV_eq</dd>
        </div>
      </dl>
    </article>
  );
}

function DNpPanel({ summary }: { summary: DNp01Summary }) {
  return (
    <article className="telemetry-panel dnp-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">DESCENDING OUTPUT</p>
          <h3>DNp01 · {summary.body_id}</h3>
        </div>
        <span className="panel-index">{summary.soma_side ?? "side not recorded"}</span>
      </div>
      <dl className="metric-grid metric-grid-2">
        <div>
          <dt>Spike count</dt>
          <dd>{summary.total_spike_count}</dd>
        </div>
        <div>
          <dt>First spike</dt>
          <dd>{value(summary.first_spike_time_ms, " ms")}</dd>
        </div>
        <div>
          <dt>Peak membrane</dt>
          <dd>{summary.peak_membrane_mv.toFixed(4)} mV</dd>
        </div>
        <div>
          <dt>Peak synaptic state</dt>
          <dd>{summary.peak_synaptic_state_mveq.toFixed(4)} mV_eq</dd>
        </div>
        <div>
          <dt>Delivered events</dt>
          <dd>{summary.delivered_event_count}</dd>
        </div>
        <div>
          <dt>Model increment sum</dt>
          <dd>{summary.model_increment_sum_mveq.toFixed(4)} mV_eq</dd>
        </div>
      </dl>
    </article>
  );
}

export function ExperimentSummaryView({ summary }: { summary: ExperimentSummary }) {
  return (
    <>
      <section className="hero-panel">
        <div>
          <p className="eyebrow">MODEL EXPERIMENT</p>
          <h1>{summary.candidate.identifier}</h1>
          <p className="hero-copy">
            A reproducible {summary.pathway_condition.toLowerCase()} run across the
            selected LC4/LPLC2 → DNp01 circuit.
          </p>
        </div>
        <div className="validation-flag">
          <span className="status-dot" aria-hidden="true" />
          <span>
            <strong>Empirical validation</strong>
            <small>{summary.validation_status.replaceAll("_", " ")}</small>
          </span>
        </div>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <p className="eyebrow">PROVENANCE</p>
          <h2>What was run</h2>
        </div>
        <dl className="provenance-grid">
          <div><dt>Dataset</dt><dd>{summary.dataset}</dd></div>
          <div><dt>Candidate</dt><dd>{summary.candidate.identifier} · v{summary.candidate.version}</dd></div>
          <div><dt>Graph scope</dt><dd>{summary.graph_scope_id}</dd></div>
          <div><dt>Encoder</dt><dd>{summary.encoder.id} · {summary.encoder.version}</dd></div>
          <div><dt>Neural model</dt><dd>{summary.neural_model.id} · {summary.neural_model.version}</dd></div>
          <div><dt>Artifact</dt><dd>{id(summary.artifact_id)}</dd></div>
          <div><dt>Config</dt><dd>{id(summary.experiment_config_id)}</dd></div>
          <div><dt>Result</dt><dd>{id(summary.result_id)}</dd></div>
        </dl>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <p className="eyebrow">EXPERIMENT</p>
          <h2>Protocol and free parameters</h2>
        </div>
        <div className="protocol-strip">
          <span><strong>{summary.pathway_condition}</strong><small>pathway condition</small></span>
          <span><strong>{summary.duration_ms} ms</strong><small>duration</small></span>
          <span><strong>{summary.dt_ms} ms</strong><small>neural dt</small></span>
        </div>
        <dl className="parameter-grid">
          <div><dt>G_LC4</dt><dd>{summary.free_parameters.lc4_gain_mv_eq} mV_eq</dd></div>
          <div><dt>G_LPLC2</dt><dd>{summary.free_parameters.lplc2_gain_mv_eq} mV_eq</dd></div>
          <div><dt>ω_half</dt><dd>{summary.free_parameters.omega_half_rad_per_s} rad/s</dd></div>
          <div><dt>θ_half</dt><dd>{summary.free_parameters.theta_half_rad} rad</dd></div>
          <div><dt>k_syn</dt><dd>{summary.free_parameters.k_syn_mv_per_contact} mV_eq/contact</dd></div>
        </dl>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <p className="eyebrow">PATHWAYS</p>
          <h2>Visual population output</h2>
        </div>
        <div className="two-column-grid">
          <PopulationPanel population={summary.populations.LC4} />
          <PopulationPanel population={summary.populations.LPLC2} />
        </div>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <p className="eyebrow">OUTPUT</p>
          <h2>DNp01 readouts</h2>
        </div>
        <div className="two-column-grid">
          {summary.dnp01.map((item) => <DNpPanel key={item.body_id} summary={item} />)}
        </div>
        <p className="subtle-note">
          These are model readouts, not motor output or behavioural predictions.
          Structural contact counts remain connectomic metadata, not measured
          physiological synaptic efficacy.
        </p>
      </section>
    </>
  );
}
