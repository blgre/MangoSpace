"""Report SME2 retrieval quality within Cebu and Bohol province boundaries."""

import argparse
import json
from pathlib import Path

import h5py
import numpy as np
from shapely import intersects_xy
from shapely.geometry import shape


def recommended(soil, flags, soil_fill, flag_fill):
    valid = np.isfinite(soil) & (soil != soil_fill) & (flags != flag_fill)
    return valid, valid & ((flags & 1) == 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--boundaries", type=Path, required=True)
    args = parser.parse_args()
    boundaries = json.loads(args.boundaries.read_text())
    report = {"file": args.file.name, "boundary_file": str(args.boundaries), "provinces": {}}
    with h5py.File(args.file) as product:
        grid = product["science/LSAR/SME2/grids"]
        soil, flags = grid["soilMoisture"], grid["retrievalQualityFlag"]
        report["soil_variable"] = soil.name
        report["quality_variable"] = flags.name
        report["quality_description"] = flags.attrs["description"].decode()
        valid, good = recommended(soil[:], flags[:], soil.attrs["_FillValue"], flags.attrs["_FillValue"])
        lon, lat = np.meshgrid(grid["longitude"][:], grid["latitude"][:])
        for name in ("Cebu", "Bohol"):
            feature = next(f for f in boundaries["features"] if f["properties"]["shapeName"] == name)
            inside = intersects_xy(shape(feature["geometry"]), lon, lat)
            count, retrieved, accepted = (int(np.count_nonzero(mask)) for mask in (inside, inside & valid, inside & good))
            values, counts = np.unique(flags[:][inside], return_counts=True)
            meanings = {}
            for value, number in zip(values, counts):
                value = int(value)
                meaning = "missing" if value == flags.attrs["_FillValue"] else (
                    ("not recommended" if value & 1 else "recommended")
                    + "; algorithms: " + ", ".join(label for bit, label in ((2, "PMI"), (4, "TSR"), (8, "DSG")) if value & bit)
                )
                meanings[str(value)] = {"pixels": int(number), "meaning": meaning}
            report["provinces"][name] = {
                "grid_pixels_inside_boundary": count,
                "valid_retrievals": retrieved,
                "recommended_retrievals": accepted,
                "recommended_share_of_grid_pixels": accepted / count if count else None,
                "recommended_share_of_valid_retrievals": accepted / retrieved if retrieved else None,
                "flags": meanings,
            }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
