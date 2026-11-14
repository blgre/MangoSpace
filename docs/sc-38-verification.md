# Sc-38 download verification

Verified locally on 14 November 2026.

- Collection: `NISAR_L3_SME2_PROVISIONAL_V1`.
- Bounds: `[123.2, 9.4, 124.7, 11.4]`.
- Dates: 21 June through 31 October 2026, from the app manifest.
- Download: 76 granules, 76 HDF5 files, 6,350,176,256 bytes, or 6.350 GB.
- Each HDF5 file opens and contains a readable `science` group.
- The count and size match `pipeline/data/sme2/download-summary.json`.
- Raw files and the summary are ignored by Git. Credentials are not saved by the command.

Run from `pipeline/` to repeat the offline verification:

```sh
uv run python verify_sme2.py
uv run python -m unittest discover -s tests
```

Both command tests pass. `uv sync --locked` also passes with Python 3.12.14.
The app regression checks pass: `npm run lint`, `npm run build`, and `npm test`.
Playwright reports one passing smoke test for the map, slider, town panel,
and absence of console errors. Its video and trace are under `app/test-results/`.
The local download is smaller than the story's initial 12.6 GB estimate.
This check covers file presence and HDF5 structure. Sc-48 must verify the
soil-water datasets and quality flags before the data is used by the app.
