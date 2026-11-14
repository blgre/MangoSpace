"""Download the provisional NISAR soil-water granules for the app manifest."""

import argparse
import json
from pathlib import Path

import earthaccess


ROOT = Path(__file__).resolve().parent
COLLECTION = "NISAR_L3_SME2_PROVISIONAL_V1"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search-only", action="store_true", help="List matches without login or download")
    args = parser.parse_args()
    manifest = json.loads((ROOT.parent / "app/public/data/manifest.json").read_text())
    start = min(window["start"] for window in manifest["windows"])
    end = max(window["end"] for window in manifest["windows"])
    print(f"Searching {COLLECTION}, {start} through {end}, bounds {manifest['bounds']}", flush=True)
    results = earthaccess.search_data(
        short_name=COLLECTION,
        bounding_box=tuple(manifest["bounds"]),
        temporal=(start, end),
        count=-1,
    )
    print(f"Found {len(results)} granules.", flush=True)
    if not results:
        raise SystemExit("No matching SME2 granules. Check catalogue availability before proceeding to sc-48.")
    if args.search_only:
        return
    auth = earthaccess.login(persist=False)
    if not auth.authenticated:
        raise SystemExit("Earthdata authentication failed; no download started.")
    destination = ROOT / "data/sme2"
    destination.mkdir(parents=True, exist_ok=True)
    print(f"Authenticated. Downloading {len(results)} granules to {destination}", flush=True)
    files = earthaccess.download(results, local_path=str(destination), show_progress=True)
    if not files or any(not Path(path).is_file() for path in files):
        raise SystemExit("Download incomplete. Rerun the command to retry.")
    total = sum(Path(path).stat().st_size for path in files)
    summary = {
        "collection": COLLECTION,
        "bounds": manifest["bounds"],
        "temporal": [start, end],
        "granules": len(results),
        "files": len(files),
        "bytes": total,
    }
    (destination / "download-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"Downloaded {len(files)} files, {total:,} bytes ({total / 1e9:.3f} GB), to {destination}")


if __name__ == "__main__":
    main()
