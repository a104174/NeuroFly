import type { ExperimentTimeline } from "@/lib/neuroflyClient";

function peak(values: number[]) {
  return values.length === 0 ? null : Math.max(...values);
}

function shown(value: number | null, unit: string) {
  return value === null ? "None" : `${value.toFixed(4)} ${unit}`;
}

export function TimelineInspector({ timeline }: { timeline: ExperimentTimeline }) {
  const stepCount = timeline.step_times_ms.length;
  return (
    <section className="section-block timeline-section">
      <div className="section-heading section-heading-inline">
        <div>
          <p className="eyebrow">PERSISTED TELEMETRY</p>
          <h2>Simulation timeline</h2>
        </div>
        <span className="loaded-badge">LOADED · {stepCount} intervals</span>
      </div>
      <div className="timeline-window">
        <span><strong>{timeline.start_ms} ms</strong><small>start</small></span>
        <span><strong>{timeline.end_ms} ms</strong><small>end</small></span>
        <span><strong>{timeline.times_ms.length}</strong><small>state boundaries</small></span>
        <span><strong>{stepCount}</strong><small>step values</small></span>
      </div>
      <dl className="timeline-metrics">
        <div><dt>Peak θ</dt><dd>{shown(peak(timeline.theta_rad), "rad")}</dd></div>
        <div><dt>Peak expansion velocity</dt><dd>{shown(peak(timeline.angular_expansion_velocity_rad_s), "rad/s")}</dd></div>
        <div><dt>Peak LC4 drive</dt><dd>{shown(peak(timeline.lc4_drive_mveq), "mV_eq")}</dd></div>
        <div><dt>Peak LPLC2 drive</dt><dd>{shown(peak(timeline.lplc2_drive_mveq), "mV_eq")}</dd></div>
      </dl>
      <p className="subtle-note">
        State samples use simulation boundaries. Feature and drive samples apply
        on <code>[t_n, t_n + dt)</code>; no interpolation or render-frame
        resampling is applied.
      </p>
    </section>
  );
}
