# CAPT-Bot

Verified CAPT project layer extracted from `knowurknottty/CAPT_core`.

## Exact provenance

- Base Core commit: `3be3fd6cc1274f7a7935d35b83641fc5b9dc82e8`
- Project source commit: `c93200626b621bf7a27c1fa6cfcbf04773121c35`
- Added project-owned files are preserved at their original CAPT paths.
- Modifications to pre-existing shared Core files are preserved in `integration/CAPT_CORE.patch`.
- `SOURCE_PROVENANCE.json` SHA-256 binds the isolated payload.

## Deterministic assembly

1. Check out CAPT Core at the base commit above.
2. Apply `integration/CAPT_CORE.patch`.
3. Overlay the project-owned paths from this repository.
4. Run the project verification gates.

This repository does not create a second RuntimeService/EventStore authority plane; it is a separately versioned integration layer for later composition into the Inversion Labs CAPT variant.
