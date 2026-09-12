import type { ExperimentSceneState } from "./playback";
import { FLY_VISUAL_ASSET } from "./flyVisualAsset";

export const SCENE_PRESENTATION_LAYOUT_ID =
  "neurofly_scene_layout_v1" as const;
export const SCENE_PRESENTATION_COORDINATE_SPACE =
  "NEUROFLY_PRESENTATION_MAPPING" as const;

export type PresentationPoint = readonly [number, number, number];
export type VisualPathwayId = "LC4" | "LPLC2";
export type Dnp01BodyId = 10001 | 10010;

const LC4_COLOR = "#72d5d0";
const LPLC2_COLOR = "#87a9ff";
const DNP01_10001_COLOR = "#e5bd79";
const DNP01_10010_COLOR = "#e58d79";

export const SCENE_PRESENTATION_LAYOUT = Object.freeze({
  layout_id: SCENE_PRESENTATION_LAYOUT_ID,
  coordinate_space: SCENE_PRESENTATION_COORDINATE_SPACE,
  scientific_status: "PRESENTATION_ONLY_NOT_ANATOMICAL" as const,
  camera: Object.freeze({
    position: Object.freeze([0, 3.55, 8.6] as const),
    field_of_view_degrees: 38,
    near: 0.1,
    far: 30,
  }),
  fly: Object.freeze({
    origin: Object.freeze(
      [...FLY_VISUAL_ASSET.canonical_transform.scene_position] as const,
    ),
  }),
  looming: Object.freeze({
    axis_start: Object.freeze([0, 1.45, -4.1] as const),
    axis_end: Object.freeze([0, 1.45, -2.4] as const),
    corridor_radius: 0.035,
  }),
  pathways: Object.freeze({
    LC4: Object.freeze({
      anchor: Object.freeze([-2.3, 1.35, -0.3] as const),
      color: LC4_COLOR,
    }),
    LPLC2: Object.freeze({
      anchor: Object.freeze([-1.55, 1.9, -0.45] as const),
      color: LPLC2_COLOR,
    }),
  }),
  dnp01: Object.freeze({
    10001: Object.freeze({
      body_id: 10001 as const,
      anchor: Object.freeze([1.55, 1.85, -0.35] as const),
      color: DNP01_10001_COLOR,
    }),
    10010: Object.freeze({
      body_id: 10010 as const,
      anchor: Object.freeze([2.3, 1.15, 0.1] as const),
      color: DNP01_10010_COLOR,
    }),
  }),
  reference_grid: Object.freeze({
    size: 12,
    divisions: 24,
    position: Object.freeze([0, -0.03, 0] as const),
    major_color: "#1e464b",
    minor_color: "#10262b",
  }),
});

export interface PresentationPathwayState {
  pathwayId: VisualPathwayId;
  rawNormalizedFeature: number;
  rawDriveMveq: number;
  presentationLevel: number;
  presentationIntensity: number;
}

export interface PresentationDnp01State {
  bodyId: Dnp01BodyId;
  rawMembraneMv: number | null;
  rawSynapticStateMveq: number | null;
  presentationLevel: number;
  presentationIntensity: number;
  persistedBoundarySpike: boolean;
}

export interface PresentationOverlayState {
  layoutId: typeof SCENE_PRESENTATION_LAYOUT_ID;
  coordinateSpace: typeof SCENE_PRESENTATION_COORDINATE_SPACE;
  looming: {
    rawThetaRad: number;
    rawAngularExpansionVelocityRadS: number;
    presentationLevel: number;
    presentationScale: number;
    presentationPosition: PresentationPoint;
  };
  pathways: Readonly<Record<VisualPathwayId, PresentationPathwayState>>;
  dnp01: Readonly<Record<Dnp01BodyId, PresentationDnp01State>>;
}

export function mapPresentationIntensity(level: number): number {
  const boundedLevel = Math.min(1, Math.max(0, level));
  const minimumIntensity = 0.16;
  const maximumIntensity = 0.82;
  return (
    minimumIntensity +
    boundedLevel * (maximumIntensity - minimumIntensity)
  );
}

function pointAlongPresentationAxis(
  start: PresentationPoint,
  end: PresentationPoint,
  level: number,
): PresentationPoint {
  const boundedLevel = Math.min(1, Math.max(0, level));
  return [
    start[0] + (end[0] - start[0]) * boundedLevel,
    start[1] + (end[1] - start[1]) * boundedLevel,
    start[2] + (end[2] - start[2]) * boundedLevel,
  ];
}

export function derivePresentationOverlayState(
  sceneState: ExperimentSceneState,
): PresentationOverlayState {
  const loomingLevel = Math.min(
    1,
    Math.max(0, sceneState.stimulusPresentationLevel),
  );
  return {
    layoutId: SCENE_PRESENTATION_LAYOUT_ID,
    coordinateSpace: SCENE_PRESENTATION_COORDINATE_SPACE,
    looming: {
      rawThetaRad: sceneState.thetaRad,
      rawAngularExpansionVelocityRadS:
        sceneState.angularExpansionVelocityRadS,
      presentationLevel: loomingLevel,
      presentationScale: 0.32 + loomingLevel * 1.28,
      presentationPosition: pointAlongPresentationAxis(
        SCENE_PRESENTATION_LAYOUT.looming.axis_start,
        SCENE_PRESENTATION_LAYOUT.looming.axis_end,
        loomingLevel,
      ),
    },
    pathways: {
      LC4: {
        pathwayId: "LC4",
        rawNormalizedFeature: sceneState.lc4NormalizedFeature,
        rawDriveMveq: sceneState.lc4DriveMveq,
        presentationLevel: sceneState.lc4PresentationLevel,
        presentationIntensity: mapPresentationIntensity(
          sceneState.lc4PresentationLevel,
        ),
      },
      LPLC2: {
        pathwayId: "LPLC2",
        rawNormalizedFeature: sceneState.lplc2NormalizedFeature,
        rawDriveMveq: sceneState.lplc2DriveMveq,
        presentationLevel: sceneState.lplc2PresentationLevel,
        presentationIntensity: mapPresentationIntensity(
          sceneState.lplc2PresentationLevel,
        ),
      },
    },
    dnp01: {
      10001: {
        bodyId: 10001,
        rawMembraneMv: sceneState.dnp01[10001].membraneMv,
        rawSynapticStateMveq: sceneState.dnp01[10001].synapticStateMveq,
        presentationLevel: sceneState.dnp01[10001].presentationLevel,
        presentationIntensity: mapPresentationIntensity(
          sceneState.dnp01[10001].presentationLevel,
        ),
        persistedBoundarySpike:
          sceneState.dnp01[10001].spikedAtSelectedBoundary,
      },
      10010: {
        bodyId: 10010,
        rawMembraneMv: sceneState.dnp01[10010].membraneMv,
        rawSynapticStateMveq: sceneState.dnp01[10010].synapticStateMveq,
        presentationLevel: sceneState.dnp01[10010].presentationLevel,
        presentationIntensity: mapPresentationIntensity(
          sceneState.dnp01[10010].presentationLevel,
        ),
        persistedBoundarySpike:
          sceneState.dnp01[10010].spikedAtSelectedBoundary,
      },
    },
  };
}
