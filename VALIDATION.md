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

The initial release's public HTTP checks are retained in `http-verification.json` as a historical record. Each later publication is checked against the new localized files directly. Native Git integration remains pending because the Vercel settings connection returned 403; see `VERCEL.md`.
