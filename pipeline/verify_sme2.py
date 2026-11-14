"""Check the downloaded SME2 file count, byte total, and HDF5 structure offline."""

import json
from pathlib import Path

import h5py


def main():
    directory = Path(__file__).resolve().parent / "data/sme2"
    summary = json.loads((directory / "download-summary.json").read_text())
    files = sorted(directory.glob("*.h5"))
    total = sum(path.stat().st_size for path in files)
    if len(files) != summary["files"] or total != summary["bytes"]:
        raise SystemExit("Local files do not match download-summary.json.")
    if not files or len(files) != summary["granules"]:
        raise SystemExit("Expected one SME2 HDF5 file per granule.")
    for path in files:
        with h5py.File(path, "r") as product:
            if "science" not in product:
                raise SystemExit(f"Missing science group: {path.name}")
    print(f"Verified {len(files)} HDF5 files, {total:,} bytes ({total / 1e9:.3f} GB).")
    print("Science groups are readable. Soil-water values and quality flags still need sc-48.")


if __name__ == "__main__":
    main()
