# Pipeline setup and SME2 download

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run from `pipeline/`:

```sh
uv sync --locked
uv run python download_sme2.py --search-only
uv run python download_sme2.py
uv run python verify_sme2.py
```

The download reads the bounds and earliest/latest window dates from
`app/public/data/manifest.json`. It uses `NISAR_L3_SME2_PROVISIONAL_V1`, matching
the manifest's provisional status. It exits with an error if the catalogue has
no matching granules, rather than treating missing data as a successful download.

Downloads require an [Earthdata Login](https://urs.earthdata.nasa.gov/).
The command uses earthaccess's existing credential lookup and otherwise prompts
in your terminal. Credentials entered at the prompt are not saved. Do not put
credentials in source files or paste them into chat. For noninteractive runs,
set `EARTHDATA_USERNAME` and `EARTHDATA_PASSWORD` in your local environment.

Raw files and `download-summary.json` go into the ignored `pipeline/data/sme2/`
directory. Copy the final file count and byte total into sc-38 after the download
finishes. Rerunning uses earthaccess's existing-file handling; remove a corrupt
local file before retrying it.

Run the offline command check with `uv run python -m unittest discover -s tests`.
The verification command compares the local count and byte total with the saved
summary and opens each HDF5 science group. It does not validate soil-water values
or quality flags; sc-48 covers those.

## Malinao Dam images and water area

```sh
uv run python targets.py
```

The command finds the `NISAR_L2_GCOV_PROVISIONAL_V1` granules on track 003 that
cover the dam, for the manifest's dates. It reads only the dam window from each
remote file, so it does not download the 5 GB granules. It writes one HH and one
HV image for each date into `app/public/data/targets/` and replaces the `bounds`
and `nisar` fields of the `malinao-dam` entry in `targets.json`. It does not
change the other fields or the other targets.

The water area is the count of HH pixels below −10 dB inside the outline of the
reservoir, after a 5 × 5 pixel mean that removes speckle. The outline comes from
the median of all dates. The comments in `targets.py` say how the limits were
selected and what the count leaves out. The command needs the same Earthdata
Login as the download.

References: [ASF collection names](https://nisar-docs.asf.alaska.edu/earthaccess/)
and [earthaccess downloads](https://earthaccess.readthedocs.io/en/latest/user/howto/download-to-local-machine/).
