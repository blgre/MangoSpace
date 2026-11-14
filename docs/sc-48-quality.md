# Sc-48: first SME2 quality check

Input: `NISAR_L3_PR_SME2_023_104_D_083_4005_DHDH_A_20260621T101649_20260621T101723_P05023_N_F_J_001.h5`.

The averaged soil-water field is `/science/LSAR/SME2/grids/soilMoisture`.
Its quality field is `/science/LSAR/SME2/grids/retrievalQualityFlag`.
The file's description defines bit 0 as recommended when zero. Bits 1, 2,
and 3 identify PMI, TSR, and DSG respectively. Missing flags and soil-water
values are -9999 and are excluded from valid retrievals. NaNs are also excluded.

Observed flag values are -9999 (missing), 8 (recommended DSG), and 9
(not recommended DSG). Testing the entire flag for zero would discard the
recommended DSG retrievals.

| Province | Grid centers inside boundary | Valid retrievals | Recommended | Recommended / valid | Recommended / grid centers |
| --- | ---: | ---: | ---: | ---: | ---: |
| Cebu | 121,555 | 100,675 | 3,246 | 3.22% | 2.67% |
| Bohol | 98,967 | 4,514 | 109 | 2.41% | 0.11% |

The grid-center denominator is restricted to this file's rectangular grid.
Missing values include areas without retrievals and do not distinguish causes.
This is one acquisition, not a province-wide time-series quality estimate.
Most valid retrievals in this file are not recommended. The tech lead should
treat the ranking as provisional until additional acquisitions are checked.

Boundaries: geoBoundaries PHL ADM2, release `41af8f1`, simplified provinces,
representing 2020. Sources are NAMRIA, PSA, and OCHA Philippines, distributed
under CC BY 3.0 IGO. Simplification affects coastal pixel selection. This is
not a substitute for sc-66's town boundaries.

Download [the boundary GeoJSON](https://github.com/wmgeolab/geoBoundaries/raw/41af8f1/releaseData/gbOpen/PHL/ADM2/geoBoundaries-PHL-ADM2_simplified.geojson)
to `pipeline/data/provinces.geojson`. From the repository root run:

```powershell
$file = (Get-ChildItem pipeline/data/sme2 -Filter '*.h5' | Sort-Object Name | Select-Object -First 1).FullName
pipeline/.venv/Scripts/python.exe pipeline/check_soil_quality.py $file --boundaries pipeline/data/provinces.geojson
```

Run the offline tests from `pipeline/` with
`uv run python -m unittest discover -s tests`.

[ASF's SME2 guide](https://nisar-docs.asf.alaska.edu/sme2/) also cautions that
the provisional collection is not fully calibrated.
