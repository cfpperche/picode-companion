# Validation

## Multilingual release

- English is served at the root and `/en/`; Portuguese at `/pt/`; Spanish at `/es/`.
- All 226 catalog messages exist in all three languages.
- Generated pages match the canonical template and selected catalog.
- Page language, canonical URL, alternate languages, active language link and localized script order are verified.
- Internal anchors, local resource references and unique HTML IDs are checked for each language.
- Runtime tests cover shutter labels, microphone labels, material changes and diagnostic fallback in each language.
- App and viewer JavaScript pass `node --check`.
- Header, mode bar and labels have responsive layout adjustments for the longer translated text.
- This release has not undergone visual browser testing; checks are source, catalog, generation and runtime-message checks.

## Geometry and product limits

The original C.02 geometry contains 146 parts and 59,788 triangles. The exterior envelope rounds to 129 × 184 × 184 mm. This is a design/integration model, not manufacturing clearance. Electrical, thermal and acoustic bench validation remain future work.

## Hosting and repository

The initial release's public HTTP checks are retained in `http-verification.json` as a historical record. Each later publication is checked against the new localized files directly. The owner connected the GitHub repository in Vercel and provided dashboard confirmation. The API still returns 403 for project settings; automatic Git deployment is being checked separately. See `VERCEL.md`.

## C.03 interior validation

- 845 visual parts; 267320 triangles. Supplier solids are not a manufacturing BOM.
- ReSpeaker supplier STEP imported at scale 1, with optional XIAO. Source hash and rigid transform recorded in `hardware/`.
- Generated group bounds replace the old manually entered envelope checks. The nominal top-joint union remains one watertight connected solid with zero overlap volume.
- Supplier tessellation includes non-watertight visual solids; their names are recorded. No claim of printable electronics meshes or complete interference clearance.
- EN, PT and ES catalogs and generated HTML passed existing checks; runtime translation checks passed.
- Chromium visual inspection: exterior, interior, isolated microphone board and compute cradle. No page errors and no horizontal overflow at 390 px. The agent-browser daemon failed to start in this environment; the installed Playwright/Chromium renderer was used as fallback.
- Removed the solid ventilation backing after visual inspection. Full tolerance, thermal, acoustic and cable engagement tests remain pending.
