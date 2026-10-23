# NeuroFly white branding and consolidated Lab release

The approved user-supplied emblem is now white on real alpha transparency.
`BrandLogo` centralizes its use in public header/footer, Lab and the existing
`AppHeader` used by scenarios, experiments, morphology, scientific and research
pages. The wordmark text and approved product composition are preserved.

## Source and derivation

The clean source is `files/Emblema Geométrico de Inseto Alado.png`, 1774×887 RGBA,
SHA-256 `3d60e4f3d41cd2266fc70108aa5bad3582e170317e65e508646d450d9fa9d676`.
It is the same emblem already displayed in the website. Its original alpha is
retained, cropped to its full bounds, resized with Lanczos within 480×248 and
centred in a 512×280 transparent canvas. RGB is white. Internal negative spaces
and partially transparent edges are preserved; no background threshold or new
symbol generation is used. The original source is untouched.

The supplied `files/neurofly-white.png` was also inspected: visible dark pixels
and alpha residue outside the intended strokes make it unsuitable as the public
canonical asset. It and both older sources remain local, unchanged and excluded
from publication. Use of the supplied branding for NeuroFly was explicitly
authorized; no independent third-party or general-purpose reuse licence is asserted.

`web/public/assets/brand/neurofly-logo-white.png` is the sole shared navigation
asset. No white CSS backing remains. The source and derived file SHA-256 values,
dimensions, byte sizes and transformation are recorded in
[`neurofly-logo-source.json`](../../web/public/assets/brand/neurofly-logo-source.json).
The source files are not runtime or test dependencies. PNG metadata is omitted.

## Browser icons

The former SVG monogram/embedded raster route is replaced by a genuine `icon.png`.
The favicon ICO contains 16/32/48/64 RGBA frames. These use the same white mark
with a narrow navy contour, retaining transparent corners and no opaque square.
Pure white on transparency disappears on light tabs; this contour is the limited
favicon presentation treatment. The Apple PNG keeps the white transparent mark.
Actual browser-chrome styling remains OS dependent; light/dark swatches and served
icon metadata can be tested without claiming native OS integration acceptance.

## Publication boundary

The consolidated release includes the approved v10.2/v10.2a Lab, necessary shared
branding components/styles, icons, tests and these provenance updates. It excludes
original user images, the old dark logo derivative and the unused local removal
of a legacy `.brand-mark` selector in `scenarios.css`. The selector is not used by
the new shared logo and is harmless in a clean checkout.

No Lab camera, scene composition, neural equations, body navigation, flight,
gait mathematics, model data, parameters, horizon, scientific schema or replay
hashing is changed by the white-logo integration. The previous local validation
reports describe their respective historical phases; this consolidated release
is separately authorized for one commit/push and a protected Preview only.
