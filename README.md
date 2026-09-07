# PiCode Companion

[English](https://picode-companion-c02.vercel.app/en/) · [Português](https://picode-companion-c02.vercel.app/pt/) · [Español](https://picode-companion-c02.vercel.app/es/)

An interactive product studio for the PiCode Companion C.03 desktop AI hardware concept. Explore the original 3D model, exploded assembly, electronics, dimensions and material studies.

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
- `public/assets/companion-c03.b64`: current geometry, gzip/base64 JSON. See `hardware/verificacao.json` for measured counts and bounds.
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
