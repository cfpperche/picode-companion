# PiCode Companion

[English](https://picode-companion-c02.vercel.app/en/) · [Português](https://picode-companion-c02.vercel.app/pt/) · [Español](https://picode-companion-c02.vercel.app/es/)

An interactive product studio for the PiCode Companion C.04 desktop AI hardware concept. Explore the original 3D model, exploded assembly, electronics, dimensions and material studies.

**Live site:** https://picode-companion-c02.vercel.app/  
**Repository:** https://github.com/cfpperche/picode-companion

The hardware is a preliminary integration study, not a manufacturing-ready product. Voice, vision and PiCode integration are planned capabilities. The website does not execute agents, collect sign-ups or access the camera or microphone.

## Languages

English is the default at `/` and `/en/`. Brazilian Portuguese is available at `/pt/`, and Spanish at `/es/`. The header language links work without JavaScript. Opening `/` always shows English; the site does not override the requested default based on browser language.

Each language has pre-rendered HTML, translated metadata and accessible labels, canonical/hreflang links, and its own runtime message catalog. Component details, materials, shutter states and viewer errors are translated as well. Hardware names and units are preserved.

## Edit and build

- `src/index.html`: canonical English HTML template.
- `locales/en.json`, `locales/pt.json`, `locales/es.json`: complete translation catalogs; English message text is the key.
- `scripts/build_locales.py`: dependency-free static locale generator.
- `public/app.js`: explorer controls and translated UI updates.
- `public/viewer.js`: WebGL renderer and translated annotations.
- `public/styles.css`: responsive styling.
- `public/assets/companion-c04.b64`: current geometry, gzip/base64 JSON. See `hardware/verificacao.json` for measured counts and bounds.
- `public/{en,pt,es}/index.html` and `public/locales/*.js`: generated files. Commit them after editing the template or catalogs.

```bash
python3 scripts/build_locales.py
python3 scripts/check_locales.py
node scripts/check_runtime.cjs
node --check public/app.js
node --check public/viewer.js
```

Python 3.9+ generates the static files. Node.js is used only for source and runtime-message checks; there are no production package dependencies.

To run locally:

```bash
python3 -m http.server 8080 --directory public
```

Open `http://localhost:8080/`. An HTTP server is required to fetch the geometry; `file://` is not supported. The 3D viewer requires WebGL 1 and gzip DecompressionStream. Failure messages are localized; the product information remains readable without the viewer.

## Vercel

The existing Vercel project is `picode-companion-c02`. `vercel.json` selects `public` as the output directory, framework Other, and no build command because generated pages are committed.

The files-based deployment and GitHub repository are separate operations. See [VERCEL.md](VERCEL.md) for the exact repository link to configure and its current verification status. Do not create a second Vercel project to enable Git deployments.

## Sources and validation

[BENCHMARKS.md](BENCHMARKS.md) records the original design research. [VALIDATION.md](VALIDATION.md) records the checks and limitations. The original prototype layout keeps the speaker under a recessed top grille and four microphone ports on the left side.

## C.03 interior revision

The model now includes native-scale supplier ReSpeaker geometry, proposed mounting cradles, flat CSI routing and a detailed generic speaker. Use **Isolate component** to inspect a subsystem. See [hardware documentation](hardware/README.md) and [component evidence](hardware/components.json). Other module details remain simplified and the assembly is not released for manufacturing.

## C.04 rotating head

The head now has a −180° to +180° motion control. The keyboard stays fixed.
A proposed SC09 microservo drives a 72:48 belt transmission, with two bearing
reserves, a hollow spindle and a rotating electronics tray. The base is 32 mm
wider and the head sits 40 mm higher: 160 × 224 × 184 mm neutral envelope.

[Mechanical design, torque, wiring and assembly](hardware/ROTATING_HEAD.md).
The actuator and harness are packaging studies pending bench validation.

```sh
node scripts/check_motion.cjs
```

## Parts catalog and bill of materials

The **Parts & materials** navigation link opens a 55-entry catalog of the C.04 design. Switch between a grid of model-derived previews and a materials table, filter by category or search, and download a localized UTF-8 CSV. Each modeled item opens in a native accessible dialog with an independent 3D camera, view presets, zoom and keyboard controls. Repeated items open on a representative unit; the selector also exposes the complete item and individual CAD elements.

- `hardware/bom.json` is the source for item IDs, quantities, specifications, sources, definition status and geometry selection. Quantities count physical parts or explicitly named kits, not supplier mesh solids.
- `scripts/build_catalog.py` verifies the geometry hash and maps all 979 physical visual meshes exactly once. The two excluded meshes are branding text. Changes to the C.04 asset require reviewing the mapping and updating the recorded hash.
- `public/catalog.json`, localized catalog HTML and `public/bom/*.csv` are generated by `python3 scripts/build_locales.py` and must be committed.
- `public/model.js` shares one geometry download/decompression between the assembly and catalog. `public/part-renderer.js` fits selected geometry independently of the assembly's head sweep. Thumbnails load only near the visible cards, using one shared WebGL context, plus one context for the dialog.
- Geometry names in the element selector are source CAD labels. Material and interface text is localized in English, Portuguese and Spanish.
- Run `node scripts/check_catalog.cjs` after generation, in addition to the existing locale and motion checks.

This is a preliminary design BOM. Unselected components and unspecified quantities remain explicit. Power supply and remaining interconnect/fastener requirements have entries without invented 3D geometry. Model bounds are distinct from verified manufacturing dimensions; prices and final material selections are not asserted.
