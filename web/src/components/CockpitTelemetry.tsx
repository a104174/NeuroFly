"use client";

import { useMemo } from "react";

import type { ExperimentTimeline, MorphologyBodyId } from "@/lib/neuroflyClient";
import type { CockpitFrame } from "@/lib/cockpitModel";
import type { ActivityStructureProjection } from "@/lib/activityStructure";

interface PlotSeries {
  readonly label: string;
  readonly values: readonly number[];
  readonly color: string;
}

const LEFT = 28;
const RIGHT = 488;
const TOP = 12;
const BOTTOM = 104;

function plotPaths(
  times: readonly number[],
  series: readonly PlotSeries[],
  startMs: number,
  endMs: number,
) {
  const values = series.flatMap((line) => line.values);
  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  const range = maximum === minimum ? 1 : maximum - minimum;
  const low = minimum - range * 0.08;
  const high = maximum + range * 0.08;
  const x = (time: number) => LEFT + ((time - startMs) / (endMs - startMs)) * (RIGHT - LEFT);
  const y = (value: number) => BOTTOM - ((value - low) / (high - low)) * (BOTTOM - TOP);
  return {
    low,
    high,
    paths: series.map((line) => ({
      label: line.label,
      color: line.color,
      path: line.values.map((value, index) =>
        `${index === 0 ? "M" : "L"}${x(times[index]).toFixed(2)},${y(value).toFixed(2)}`,
      ).join(" "),
    })),
  };
}

function TelemetryPlot({
  title,
  source,
  unit,
  times,
  series,
  currentValues,
  startMs,
  endMs,
  frame,
}: {
  title: string;
  source: string;
  unit: string;
  times: readonly number[];
  series: readonly PlotSeries[];
  currentValues: readonly number[];
  startMs: number;
  endMs: number;
  frame: CockpitFrame;
}) {
  const geometry = useMemo(
    () => plotPaths(times, series, startMs, endMs),
    [times, series, startMs, endMs],
  );
  const cursorX = LEFT + frame.cursorFraction * (RIGHT - LEFT);
  return (
    <section className="cockpit-plot" aria-label={title}>
      <div className="cockpit-plot-heading">
        <div>
          <h3>{title}</h3>
          <p>{source}</p>
        </div>
        <span>{unit}</span>
      </div>
      <svg viewBox="0 0 516 128" role="img" aria-label={`${title}; current cursor ${frame.playbackTimeMs.toFixed(3)} milliseconds`}>
        <line x1={LEFT} y1={TOP} x2={LEFT} y2={BOTTOM} className="cockpit-plot-axis" />
        <line x1={LEFT} y1={BOTTOM} x2={RIGHT} y2={BOTTOM} className="cockpit-plot-axis" />
        <line x1={LEFT} y1={(TOP + BOTTOM) / 2} x2={RIGHT} y2={(TOP + BOTTOM) / 2} className="cockpit-plot-gridline" />
        {geometry.paths.map((path) => <path key={path.label} d={path.path} stroke={path.color} className="cockpit-plot-trace" />)}
        <line x1={cursorX} y1={TOP} x2={cursorX} y2={BOTTOM} className="cockpit-plot-cursor" />
        <text x="2" y="17">{geometry.high.toFixed(2)}</text>
        <text x="2" y="102">{geometry.low.toFixed(2)}</text>
        <text x={LEFT} y="122">{startMs.toFixed(1)} ms</text>
        <text x={RIGHT} y="122" textAnchor="end">{endMs.toFixed(1)} ms</text>
      </svg>
      <div className="cockpit-plot-values" aria-live="off">
        {series.map((line, index) => (
          <span key={line.label}>
            <i style={{ backgroundColor: line.color }} aria-hidden="true" />
            {line.label}: <strong>{currentValues[index].toFixed(4)} {unit}</strong>
          </span>
        ))}
      </div>
    </section>
  );
}

export function CockpitTelemetry({
  timeline,
  frame,
  selectedBodyId,
  activity,
  focused,
  onToggleFocus,
}: {
  timeline: ExperimentTimeline;
  frame: CockpitFrame;
  selectedBodyId: MorphologyBodyId | null;
  activity: ActivityStructureProjection;
  focused: boolean;
  onToggleFocus: () => void;
}) {
  const theta = useMemo<PlotSeries[]>(() => [
    { label: "Angular size θ", values: timeline.theta_rad, color: "#e5bd79" },
  ], [timeline.theta_rad]);
  const drives = useMemo<PlotSeries[]>(() => [
    { label: "LC4 type drive", values: timeline.lc4_drive_mveq, color: "#8fd5ff" },
    { label: "LPLC2 type drive", values: timeline.lplc2_drive_mveq, color: "#dc8e5a" },
  ], [timeline.lc4_drive_mveq, timeline.lplc2_drive_mveq]);
  const selectedState = selectedBodyId === 10001 || selectedBodyId === 10010
    ? activity.bodySpecificStates?.[selectedBodyId] ?? null
    : null;
  const selectedTelemetry = selectedState
    ? timeline.selected_body_telemetry.find((body) => body.body_id === selectedState.bodyId)
    : undefined;
  const membrane = useMemo<PlotSeries[]>(() => selectedTelemetry ? [
    {
      label: `DNp01 body ${selectedTelemetry.body_id} membrane`,
      values: selectedTelemetry.membrane_mv,
      color: "#7ad6d2",
    },
  ] : [], [selectedTelemetry]);

  return (
    <section className="cockpit-panel cockpit-telemetry" aria-labelledby="cockpit-telemetry-heading">
      <div className="cockpit-panel-heading">
        <div>
          <p className="eyebrow">03 / EXPERIMENT TELEMETRY</p>
          <h2 id="cockpit-telemetry-heading">Persisted signals</h2>
        </div>
        <div className="cockpit-panel-actions">
          <span className="cockpit-panel-tag">SIMULATED · SOURCE TIMELINE</span>
          <button type="button" className="cockpit-focus-button" aria-pressed={focused} onClick={onToggleFocus}>
            {focused ? "Restore workspace" : "Expand telemetry"}
          </button>
        </div>
      </div>
      <div className="cockpit-plot-grid" data-traces={selectedTelemetry ? 3 : activity.typeLevelDrives ? 2 : 1}>
        <TelemetryPlot title="Looming angular size" source="theta_rad · persisted interval values" unit="rad" times={timeline.step_times_ms} series={theta} currentValues={[frame.thetaRad]} startMs={timeline.start_ms} endMs={timeline.end_ms} frame={frame} />
        {activity.typeLevelDrives ? <TelemetryPlot title="Sensory model drive · TYPE LEVEL" source="Bilateral type-broadcast interval values" unit="mV_eq" times={timeline.step_times_ms} series={drives} currentValues={activity.typeLevelDrives.map((signal) => signal.valueMveq)} startMs={timeline.start_ms} endMs={timeline.end_ms} frame={frame} /> : null}
        {selectedTelemetry && selectedState && membrane.length > 0 ? (
          <TelemetryPlot title={`DNp01 ${selectedTelemetry.body_id} membrane`} source="Body-specific persisted boundary state · simulated" unit="mV" times={timeline.times_ms} series={membrane} currentValues={[selectedState.membraneMv]} startMs={timeline.start_ms} endMs={timeline.end_ms} frame={frame} />
        ) : null}
      </div>
      <details className="cockpit-panel-details">
        <summary>Sampling and cursor</summary>
        <p>The vertical cursor follows experiment time. Numeric interval values use the existing floor selection; DNp01 membrane uses the selected stored boundary. Traces join stored samples for display only.</p>
      </details>
    </section>
  );
}
