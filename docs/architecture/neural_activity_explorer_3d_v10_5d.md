# v10.5d — verified MaleCNS neural anatomy and live activity view

## Scope and scientific interpretation

The first 3D view contains the exact eight identities already pinned by the
HS/DNp15 model contract: six horizontal-system sources and two DNp15 targets.
The model's state slots are identity-resolved computational proxies associated
with the corresponding MaleCNS `body_id`. They are not measurements of those
cells' physiological activity. In particular, the HS identities share the
same simplified proxy rule, and the DNp15 readout is a continuous
`dnp15_state_eq` model quantity without a voltage or spike calibration.

The activity is computed by the existing browser simulation. This viewer does
not run another solver. Its data are taken from the left boundary of the latest
20 ms interval, while the displayed body pose is the accepted state at the
following tick. The interface shows both tick numbers so that this timing is
explicit. Pause holds both the latest accepted body state and the latest model
sample; resume advances both through the existing session.

One signed proxy value is associated with each entire skeleton for display.
No local activity distribution along its branches is modeled. Color and
opacity are a visual encoding of the signed dimensionless model value, not
fluorescence, `Δf/F`, membrane voltage, or observed neural imaging.

## Identity and source mapping

The identity contract below is also checked against the existing
`interactive_neural_locomotion_v2` runtime configuration and the frozen
`male-cns:v1.0` selected-motif authority. The morphology source URL is the
official versioned bulk SWC path for that exact `body_id`.

| MaleCNS body ID | Curated type/side | Model slot | Role | Official v1.0 SWC SHA-256 | Nodes | Source sampling |
|---:|---|---|---|---|---:|---|
| 10015 | HSN / R | `hs_states[0]` | HS source | `af6e498120fac5e7e5394ae733027ddb84c2b48986976e7db4992b9b7cf2ab6b` | 10,092 | `downresLevel=2`, `ds_intv=15/15/15` |
| 10016 | HSE / R | `hs_states[1]` | HS source | `96029efd958f9ac3e89316d5360adb64ff88fe68b933a14ae4b45a8bd6b985d1` | 11,071 | `downresLevel=2`, `ds_intv=15/15/15` |
| 10023 | HSS / R | `hs_states[2]` | HS source | `c275ee6cdf54e7048e8fbef391975ee3abb0210ace223bda06d0be78fa37231b` | 2,515 | `downresLevel=coarse`, `ds_intv=63/63/63` |
| 10034 | HSE / L | `hs_states[3]` | HS source | `c1de2fd253a781cd3dd40c68eccd472fe8b950f66ef8c0bc605503a446f4aa07` | 2,614 | `downresLevel=coarse`, `ds_intv=63/63/63` |
| 10181 | HSN / L | `hs_states[4]` | HS source | `4bcf9377e4b49cabd54cc5417ead5ed1273461447b9947b764bc1546ce2cd694` | 2,301 | `downresLevel=coarse`, `ds_intv=63/63/63` |
| 10419 | HSS / L | `hs_states[5]` | HS source | `0f02271a583448c355a1dac9efc8d62b08fe4b548ab962e7f7086695f91bf6ec` | 2,545 | `downresLevel=coarse`, `ds_intv=63/63/63` |
| 11215 | DNp15 / R | `dnp15_states[0]` | DNp15 target | `8f8fdfaac7f1c3cbb289e0ad3cbdc3e5230a1008da00888ea4e02e7c007054f3` | 2,132 | `downresLevel=coarse`, `ds_intv=63/63/63` |
| 12069 | DNp15 / L | `dnp15_states[1]` | DNp15 target | `bb2ce1c67a2ddf748994498fbd2fa17bcf78ea825d199b0388d7892f8a4b38da` | 2,195 | `downresLevel=coarse`, `ds_intv=63/63/63` |

All eight SWCs have one root and are retained without healing, smoothing,
repair, interpolation, or branch synthesis. The different `ds_intv` values
are preserved as source sampling metadata; fine and coarse skeletons are not
presented as equally sampled detail. The SWC morphology class/type field is
not used to infer the curated HSN/HSE/HSS/DNp15 identity; that identity comes
from the pinned annotation contract.

## Coordinates and display transform

The assets are from
`https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/{bodyId}.swc`.
The official source defines these SWCs in MaleCNS EM native coordinates in
8 nm voxels. No JRC2018 unisex-template transform, mirroring, side-based
reflection, or axis remapping is applied. The view preserves native x/y/z as
view x/y/z; no anatomical names or left/right direction are inferred for those
axes.

At runtime, the viewer computes one center and one uniform scale from the
combined bounds of all eight skeletons. It then applies
`view = (native_xyz - shared_center) * shared_scale` for presentation. This
does not change source data, model values, or scientific identity. There are
no spatially drawn synapses: the selected MaleCNS route set is shown as
identity metadata because this artifact does not include synapse coordinates.
The six route contact counts are provenance only, not model gains.

## Asset bundle and integrity

The eight original SWC source files and `manifest.json` are stored under
`web/public/assets/neural/malecns-v1.0/hs-dnp15/`. This is a fixed subset,
not the full MaleCNS dataset. The checked-in manifest SHA-256 is
`c538f94a6a3ea02390bfcb09ee77226fe6f0418455c0794cdfedd64593070697`.
The client verifies that manifest hash, dataset/schema/identity order, source
URL, coordinates, selected route identities and every raw source-file hash
before rendering. The SWC parser rejects malformed records, duplicate node
IDs, missing parents, cycles, non-finite coordinates/radii, wrong node counts,
or unexpected components. A failed check shows an unavailable state and does
not display replacement anatomy.

The MaleCNS v1.0 dataset is licensed CC-BY. Attribution and the official
download link are visible in the explorer. Source morphology has not been
modified; the runtime view transformation is the only presentation change.

## Causal scope

The supported chain is: existing geometric/model sensory inputs → six HS
computational proxy states → two DNp15 continuous proxy states → existing
signed neural yaw projection → engineering boundary response and motor
integration → accepted body pose. The six selected structural routes are
frozen by the existing MaleCNS-derived authority. Wider recurrent/electrical
relationships remain outside the model. The selected cell is not asserted to
have independently chosen a movement, and the viewer does not infer anatomy
or activity beyond the eight fixed identities.

The geometry selector, orbit camera, activity colors, and opacity do not feed
the simulation. No complete live-session recording is created; the view uses
the current bounded telemetry sample only.
