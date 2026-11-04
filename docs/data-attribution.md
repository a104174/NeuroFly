# Data credit and licence

## Dataset

NeuroFly uses the **MaleCNS connectome, v1.0** (male-cns.janelia.org). The official release page
(https://male-cns.janelia.org/release/) states: "The Male CNS dataset is licensed under CC-BY." and links to
the Creative Commons Attribution 4.0 International licence (https://creativecommons.org/licenses/by/4.0/).

Official skeleton files used here come from
`https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/`.

## Paper to cite

Berg S et al. *Sexual dimorphism in the complete connectome of the Drosophila male central nervous system.*
bioRxiv (2025). doi:10.1101/2025.10.09.680999 (https://doi.org/10.1101/2025.10.09.680999).

Title, first author and DOI were read from the DOI registry (Crossref) and the bioRxiv page. The full author
list is not reproduced here: the two sources differ slightly (110 and 111 names, and one spelling), so use the
DOI link for it.

**Missing citation details (follow-up):** the Cell page supplied by the owner
(https://www.cell.com/cell/fulltext/S0092-8674%2826%2900942-6) returned HTTP 403 and could not be read, so
its title, authors, DOI and volume are not recorded or cited anywhere. Add them from the publisher page.

## What NeuroFly changed (it distributes derived files)

| Files | Derived from | Changes |
| --- | --- | --- |
| `data/reference/morphology_artifacts_v1/` (10 files, 3.1 MB; two artifacts of 2 and 6 bodies) | Official MaleCNS v1.0 bulk skeleton (SWC) files for bodies 10001, 10010, 11498, 12032, 14465, 16128 | Converted from SWC to JSON. Node coordinates, radii and parent links are the official values, stored as 32-bit numbers (all 55,596 values checked; largest relative difference 5.7 × 10⁻⁸; parent links identical). Added: identifiers, SHA-256 checksums, neuron type and side labels from the MaleCNS neuron annotations, and project metadata. No healing, smoothing or repair. |
| Circuit and connection files in the runtime bundle (selected neurons and connections, `looming_giant_fiber_v1`) | MaleCNS v1.0 neuron and connection tables | A selected subset (313 and 8 bodies), re-formatted, with identifiers and checksums. |
| Model results, experiments and playback | NeuroFly's own model | Not part of the dataset. Model output is not biological data and does not imply endorsement by the dataset's authors. |

Verification done when these files were added to the repository: the six source skeleton files were downloaded
from the official location and their SHA-256 hashes equal the hashes recorded in the artifact manifests;
every recorded value equals the official number rounded to 32 bits.

## Where the credit appears

- Site footer (every page) and the Science page, section "Data credit and licence" (`/science#data-credit`).
- This file, linked from the README.
