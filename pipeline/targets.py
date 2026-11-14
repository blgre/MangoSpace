import json
from pathlib import Path

import earthaccess
import h5py
import numpy as np
import rasterio
from numpy.lib.stride_tricks import sliding_window_view
from pyproj import Geod, Transformer
from rasterio.features import sieve
from rasterio.transform import from_bounds, from_origin
from rasterio.warp import Resampling, reproject


ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT.parent / "app/public/data"
COLLECTION = "NISAR_L2_GCOV_PROVISIONAL_V1"
GRID = "science/LSAR/GCOV/grids/frequencyA"
TARGET = "malinao-dam"
BOUNDS = (124.297, 9.8075, 124.337, 9.8475)
# One track only: the radar angle changes the image, so tracks do not compare.
TRACK = "003"
SIZE = 440
BLACK_DB = -30.0
# One pixel has strong speckle. The mean of 5 x 5 pixels gives two clear HH peaks in the box:
# water near -18 dB and land near -7 dB.
LOOKS = 5
# Halfway between the two peaks. It cuts the outline of the reservoir from the median of all dates.
OUTLINE_DB = -12.5
# A pixel that is half water and half land has the mean power of the two peaks, about -10 dB.
WATER_DB = -10.0
MIN_WATER_PIXELS = 100
# shortcut: water more than 20 m outside the usual outline is not counted. Wet rice fields
# next to the reservoir are as dark as water, so the count stays inside the outline.
# Make this larger if the reservoir grows past its 2026 shore.
SHORE_PIXELS = 5
WEST, SOUTH, EAST, NORTH = BOUNDS
BOX_M2 = abs(Geod(ellps="WGS84").polygon_area_perimeter([WEST, EAST, EAST, WEST], [SOUTH, SOUTH, NORTH, NORTH])[0])
PIXEL_KM2 = BOX_M2 / 1e6 / SIZE**2


def read_window(file):
    grid = file[GRID]
    epsg = int(np.array(grid["projection"]))
    x, y = grid["xCoordinates"][:], grid["yCoordinates"][:]
    xs, ys = Transformer.from_crs(4326, epsg, always_xy=True).transform([WEST, WEST, EAST, EAST], [SOUTH, NORTH, SOUTH, NORTH])
    pad = 300
    columns = np.flatnonzero((x >= min(xs) - pad) & (x <= max(xs) + pad))
    rows = np.flatnonzero((y >= min(ys) - pad) & (y <= max(ys) + pad))
    if not columns.size or not rows.size:
        raise SystemExit("The granule does not cover the target bounds.")
    window = (slice(rows[0], rows[-1] + 1), slice(columns[0], columns[-1] + 1))
    dx, dy = x[1] - x[0], y[0] - y[1]
    transform = from_origin(x[columns[0]] - dx / 2, y[rows[0]] + dy / 2, dx, dy)
    return {"hh": grid["HHHH"][window], "hv": grid["HVHV"][window]}, transform, epsg


def reproject_to_db(power, transform, epsg):
    out = np.full((SIZE, SIZE), np.nan, "float32")
    power = power.astype("float32")
    reproject(
        np.where(power > 0, power, np.nan),
        out,
        src_transform=transform,
        src_crs=f"EPSG:{epsg}",
        dst_transform=from_bounds(*BOUNDS, SIZE, SIZE),
        dst_crs="EPSG:4326",
        resampling=Resampling.average,
        src_nodata=np.nan,
        dst_nodata=np.nan,
    )
    with np.errstate(divide="ignore"):
        return 10 * np.log10(out)


def to_grey(db):
    return np.nan_to_num(np.clip((db - BLACK_DB) / -BLACK_DB * 255, 0, 255)).round().astype("uint8")


def box(values, size, reduce):
    return reduce(sliding_window_view(np.pad(values, size // 2, mode="edge"), (size, size)), axis=(-1, -2))


def despeckle(db):
    return 10 * np.log10(box(10 ** (db / 10), LOOKS, np.mean))


def reservoir_outline(hh_db_by_date):
    usual = np.median(np.stack(hh_db_by_date), axis=0)
    water = sieve((usual < OUTLINE_DB).astype("uint8"), MIN_WATER_PIXELS, connectivity=8)
    return box(water, SHORE_PIXELS, np.max).astype(bool)


def water_area_km2(hh_db, outline):
    return round(float(((hh_db < WATER_DB) & outline).sum() * PIXEL_KM2), 3)


def write_png(path, grey):
    with rasterio.open(path, "w", driver="PNG", width=SIZE, height=SIZE, count=1, dtype="uint8") as png:
        png.write(grey, 1)


def main():
    manifest = json.loads((PUBLIC / "manifest.json").read_text())
    start = min(window["start"] for window in manifest["windows"])
    end = max(window["end"] for window in manifest["windows"])
    results = earthaccess.search_data(short_name=COLLECTION, bounding_box=BOUNDS, temporal=(start, end), count=-1)
    scenes = {}
    for granule in results:
        name = granule["umm"]["GranuleUR"].split("_")
        if name[5] == TRACK:
            date = f"{name[11][:4]}-{name[11][4:6]}-{name[11][6:8]}"
            scenes[date] = next(link for link in granule.data_links() if link.endswith(".h5"))
    print(f"Found {len(results)} granules, {len(scenes)} on track {TRACK}.", flush=True)
    if not scenes:
        raise SystemExit(f"No {COLLECTION} granules on track {TRACK}. targets.json is not changed.")
    if not earthaccess.login(persist=False).authenticated:
        raise SystemExit("Earthdata authentication failed. targets.json is not changed.")
    session = earthaccess.get_fsspec_https_session()
    (PUBLIC / "targets").mkdir(exist_ok=True)
    images, hh = [], []
    for date, url in sorted(scenes.items()):
        with session.open(url, block_size=4 * 1024 * 1024, cache_type="blockcache") as remote, h5py.File(remote, "r") as file:
            power, transform, epsg = read_window(file)
        db = {band: reproject_to_db(values, transform, epsg) for band, values in power.items()}
        valid = float(np.isfinite(db["hh"]).mean())
        if valid < 0.99:
            raise SystemExit(f"{date}: only {valid:.0%} of the target has data. targets.json is not changed.")
        image = {band: f"targets/{TARGET}-{date}-{band}.png" for band in db}
        for band, path in image.items():
            write_png(PUBLIC / path, to_grey(db[band]))
        images.append(image)
        hh.append(despeckle(db["hh"]))
        print(f"{date}: read", flush=True)
    outline = reservoir_outline(hh)
    areas = [water_area_km2(image, outline) for image in hh]
    print(f"Water km2: {dict(zip(sorted(scenes), areas))}")
    path = PUBLIC / "targets.json"
    targets = json.loads(path.read_text())
    target = next(target for target in targets if target["id"] == TARGET)
    target["bounds"] = list(BOUNDS)
    target["nisar"] = {"track": int(TRACK), "dates": sorted(scenes), "images": images, "waterAreaKm2": areas}
    path.write_text(json.dumps(targets, indent=1, ensure_ascii=False) + "\n")
    print(f"Wrote {len(areas)} dates for {TARGET} to {path}")


if __name__ == "__main__":
    main()
