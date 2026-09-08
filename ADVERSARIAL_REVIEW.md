# Adversarial review — 2026-09-08

Scope: public EN/PT/ES site, BOM, committed C.04 geometry, assembly inspection and individual-part catalog.

| Severity | Finding | Resolution |
| --- | --- | --- |
| High | Without WebGL the assembly, every card and the part inspector were blank. | Added 53 model-derived part images and exterior/internal/exploded assembly images. Part metadata and measured bounds work without WebGL. Unsupported controls are hidden or disabled. |
| High | Isolating a small component retained the full rotating-head sweep in camera bounds; dimensions still described the whole enclosure. | Fit selected geometry using its transformed corners; isolate dimensions describe the selected geometry in the centered-head reference. |
| Medium | Selecting compute changed renderer mode without updating the active UI tab. Clearing selection retained isolation. | Centralized automatic mode transition in the UI and reset isolation consistently. |
| Medium | Camera isolation omitted shutter/rail; I/O isolation omitted mute. | Included the related physical groups. |
| Medium | Technical metadata still claimed 998 meshes / 279856 triangles. | Corrected to 981 / 278870 and added an asset-derived regression check. These are CAD meshes, not procurement quantities: the BOM has 55 entries. |
| Medium | Display description used an obsolete 94 mm reserve. | Matched catalog: modeled glass 84 × 84 mm, active area 72.53 × 72.53 mm; mounting and connectors remain provisional. |
| Medium | Servo reserve could be confused with supplier body dimensions. | Explicitly distinguished nominal body 23.2 × 12 × 25.5 mm from the conservative 34 × 16 × 34 mm modeled reserve. No unverified shaft relocation or body scaling. |
| Low | Orthographic view was labeled Perspective. Failed model request remained cached forever. | Renamed view to 3/4 and allowed retry after failure, with a 20-second network timeout. |

## Evidence and sources

Browser review reproduced the no-WebGL failure on the live Portuguese page, including the bearing modal. This environment does not expose WebGL: actual GPU shading and pointer-driven rendering remain unverified here. Node tests exercise mesh buffers, finite camera matrices, rigid/flex transforms and UI selection state; they do not replace a GPU browser test.

Primary supplier product pages checked on 2026-09-08:

- [CM5-NANO-B](https://www.waveshare.com/cm5-nano-b.htm): nominal 55 × 41 mm board. Connector placements still need detailed CAD/drawing confirmation.
- [SC09](https://www.waveshare.com/sc09-servo.htm): nominal body 23.2 × 12 × 25.5 mm; 300° positional travel. Supplier rated torque 0.7 kg·cm is different from stall torque 2.3 kg·cm at 6 V. Do not size continuous head load from stall torque.
- [4inch HDMI LCD (C)](https://www.waveshare.com/4inch-hdmi-lcd-c.htm): 720 × 720 IPS capacitive display. Model glass/active-area dimensions above are model values, not newly validated fabrication dimensions.

Static images are rasterized from the exact committed triangles with an orthographic depth buffer, never hand-redrawn. `public/assets/parts/manifest.json` pins the geometry, mesh selections and image hashes. Regenerate with `python3 scripts/render_previews.py` (NumPy, Pillow and g++ required), after rebuilding the catalog. Images use the graphite finish and centered head; the exploded fallback is a fixed overview.

## Remaining engineering gaps

No manufacturing release: supplier connector/mounting CAD, fits, full rotating-assembly interference, cable bend/fatigue, servo torque under load, power conversion, thermal performance and speaker acoustics still need validation. PSU and remaining interconnect/fastener kit lack geometry and final quantities. No geometry dimensions were changed merely to make a visual appear more plausible.

## Repeatable checks

`python3 scripts/build_locales.py`, `python3 scripts/check_locales.py`, `node scripts/check_runtime.cjs`, `node scripts/check_motion.cjs`, `node scripts/check_catalog.cjs`, `node scripts/check_review.cjs`.
