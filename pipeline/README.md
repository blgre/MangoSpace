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

References: [ASF collection names](https://nisar-docs.asf.alaska.edu/earthaccess/)
and [earthaccess downloads](https://earthaccess.readthedocs.io/en/latest/user/howto/download-to-local-machine/).
