"use client";

import dynamic from "next/dynamic";
import {
  Component,
  useCallback,
  useState,
  type ErrorInfo,
  type ReactNode,
} from "react";

import { useExperimentPlayback } from "@/hooks/useExperimentPlayback";
import type {
  ExperimentTimeline,
  ValidationStatus,
} from "@/lib/neuroflyClient";
import {
  flyVisualAssetProvenance,
  flyAssetStatusMessage,
  type FlyAssetLoadStatus,
} from "@/lib/flyVisualAsset";
import { PLAYBACK_RATES, type PlaybackRate } from "@/lib/playback";
import {
  SCENE_PRESENTATION_COORDINATE_SPACE,
  SCENE_PRESENTATION_LAYOUT_ID,
} from "@/lib/sceneLayout";

const FLY_ASSET_PROVENANCE = flyVisualAssetProvenance();

const PlaybackCanvas = dynamic(
  () => import("./PlaybackCanvas").then((module) => module.PlaybackCanvas),
  {
    ssr: false,
    loading: () => (
      <div className="playback-canvas-fallback">Loading 3D renderer…</div>
    ),
  },
);

class PlaybackRenderBoundary extends Component<
  { children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidCatch(_error: Error, _info: ErrorInfo) {
    // The readable scientific summary remains available outside this boundary.
  }

  render() {
    if (this.state.failed) {
      return (
        <div className="playback-canvas-fallback">
          3D playback is unavailable in this browser.
        </div>
      );
    }
    return this.props.children;
  }
}

function shown(value: number | null, unit: string) {
  return value === null ? "unavailable" : `${value.toFixed(4)} ${unit}`;
}

export function PlaybackWorkspace({
  timeline,
  validationStatus,
}: {
  timeline: ExperimentTimeline;
  validationStatus: ValidationStatus;
}) {
  const playback = useExperimentPlayback(timeline);
  const scene = playback.sceneState;
  const [assetStatus, setAssetStatus] = useState<FlyAssetLoadStatus>("loading");
  const handleAssetStatusChange = useCallback((status: FlyAssetLoadStatus) => {
    setAssetStatus(status);
  }, []);

  return (
    <section
      className="section-block playback-section"
      aria-labelledby="playback-heading"
    >
      <div className="section-heading section-heading-inline playback-section-heading">
        <div>
          <p className="eyebrow">IMMERSIVE PLAYBACK / PRESENTATION VIEW</p>
          <h2 id="playback-heading">Persisted experiment in 3D</h2>
        </div>
        <div className="playback-statuses">
          <span className="loaded-badge">TIMELINE SOURCE · READ ONLY</span>
          <span className={`asset-status asset-status-${assetStatus}`}>
            {flyAssetStatusMessage(assetStatus)}
          </span>
        </div>
      </div>

      <div className="playback-stage">
        <div
          className="playback-canvas-shell"
          aria-label="Three-dimensional experiment presentation"
        >
          <PlaybackRenderBoundary>
            <PlaybackCanvas
              sceneState={scene}
              onAssetStatusChange={handleAssetStatusChange}
            />
          </PlaybackRenderBoundary>
        </div>
        <div className="playback-overlay" aria-live="polite">
          <div>
            <span>Simulation time</span>
            <strong>{playback.currentTimeMs.toFixed(3)} ms</strong>
          </div>
          <div>
            <span>Selected state boundary</span>
            <strong>{scene.boundaryTimeMs.toFixed(3)} ms</strong>
          </div>
          <div>
            <span>Selected interval start</span>
            <strong>{scene.intervalStartMs.toFixed(3)} ms</strong>
          </div>
          <div>
            <span>Angular size</span>
            <strong>{scene.thetaRad.toFixed(6)} rad</strong>
          </div>
          <div>
            <span>Angular expansion</span>
            <strong>
              {scene.angularExpansionVelocityRadS.toFixed(6)} rad/s
            </strong>
          </div>
          <div>
            <span>Playback</span>
            <strong>{playback.isPlaying ? "PLAYING" : "PAUSED"}</strong>
          </div>
          <div className="playback-validation">
            <span>Empirical validation</span>
            <strong>{validationStatus.replaceAll("_", " ")}</strong>
          </div>
        </div>
      </div>

      <div className="scene-contract-strip">
        <div className="visual-asset-provenance">
          <p className="eyebrow">VISUAL ASSET PROVENANCE</p>
          <dl>
            <div>
              <dt>Asset</dt>
              <dd>
                {FLY_ASSET_PROVENANCE.assetId} · v
                {FLY_ASSET_PROVENANCE.assetVersion}
              </dd>
            </div>
            <div>
              <dt>GLB SHA-256</dt>
              <dd>{FLY_ASSET_PROVENANCE.sha256Prefix}…</dd>
            </div>
            <div>
              <dt>Export</dt>
              <dd>
                {FLY_ASSET_PROVENANCE.exportTool} {" "}
                {FLY_ASSET_PROVENANCE.exportToolVersion}
              </dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>
                {FLY_ASSET_PROVENANCE.presentationOnly
                  ? "PRESENTATION ONLY"
                  : "UNSPECIFIED"}
              </dd>
            </div>
          </dl>
          <p>
            Visual asset provenance is separate from experiment provenance and
            scientific identity.
          </p>
        </div>

        <div className="data-presentation-legend">
          <p className="eyebrow">DATA / PRESENTATION BOUNDARY</p>
          <div>
            <section aria-labelledby="persisted-data-heading">
              <h3 id="persisted-data-heading">Persisted data</h3>
              <p>
                Simulation time, theta, angular expansion, LC4/LPLC2 model
                values, and DNp01 state/spikes.
              </p>
            </section>
            <section aria-labelledby="presentation-mapping-heading">
              <h3 id="presentation-mapping-heading">Presentation mapping</h3>
              <p>
                Mesh and pathway placement, colors, bounded intensity, camera,
                corridor, and normalized scene scale.
              </p>
            </section>
          </div>
          <p className="scene-layout-identity">
            {SCENE_PRESENTATION_LAYOUT_ID} · {SCENE_PRESENTATION_COORDINATE_SPACE}
            {" · NOT ANATOMICAL COORDINATES"}
          </p>
        </div>
      </div>

      <div
        className="playback-legend"
        aria-label="Current persisted activity values"
      >
        <div className="legend-lc4">
          <span>LC4 normalized feature</span>
          <strong>{scene.lc4NormalizedFeature.toFixed(4)}</strong>
          <small>drive {scene.lc4DriveMveq.toFixed(4)} mV_eq</small>
        </div>
        <div className="legend-lplc2">
          <span>LPLC2 normalized feature</span>
          <strong>{scene.lplc2NormalizedFeature.toFixed(4)}</strong>
          <small>drive {scene.lplc2DriveMveq.toFixed(4)} mV_eq</small>
        </div>
        <div className="legend-dnp01-a">
          <span>DNp01 · 10001 membrane</span>
          <strong>{shown(scene.dnp01[10001].membraneMv, "mV")}</strong>
        </div>
        <div className="legend-dnp01-b">
          <span>DNp01 · 10010 membrane</span>
          <strong>{shown(scene.dnp01[10010].membraneMv, "mV")}</strong>
        </div>
      </div>

      <div
        className="playback-controls"
        aria-label="Experiment playback controls"
      >
        <div className="playback-buttons">
          <button
            type="button"
            onClick={playback.isPlaying ? playback.pause : playback.play}
            aria-label={
              playback.isPlaying
                ? "Pause experiment playback"
                : "Play experiment playback"
            }
          >
            {playback.isPlaying ? "Pause" : "Play"}
          </button>
          <button
            type="button"
            onClick={playback.reset}
            aria-label="Reset experiment playback"
          >
            Reset
          </button>
        </div>
        <label className="playback-scrubber">
          <span>Simulation time · ms</span>
          <input
            type="range"
            min={timeline.start_ms}
            max={timeline.end_ms}
            step={timeline.dt_ms}
            value={playback.currentTimeMs}
            onChange={(event) => playback.seek(Number(event.currentTarget.value))}
            aria-label="Seek persisted experiment simulation time"
          />
        </label>
        <label className="playback-rate">
          <span>Playback speed</span>
          <select
            value={playback.playbackRate}
            onChange={(event) =>
              playback.setPlaybackRate(
                Number(event.currentTarget.value) as PlaybackRate,
              )
            }
            aria-label="Select visualization playback speed"
          >
            {PLAYBACK_RATES.map((rate) => (
              <option key={rate} value={rate}>
                {rate}×
              </option>
            ))}
          </select>
        </label>
      </div>

      <p className="subtle-note playback-note">
        The fly asset, abstract pathway lines, looming corridor, mesh scale,
        position, colors, and brightness are presentation mappings rather than
        anatomical coordinates. The fly remains stationary; DNp01 activity
        does not drive movement or behavior. Scientific values are selected
        directly from persisted boundaries and intervals without interpolation.
      </p>
    </section>
  );
}
