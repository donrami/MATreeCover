#!/usr/bin/env python3
"""Measure mean relative luminance of a screenshot (SC-001 gate).

Usage:
    python scripts/measure_luminance.py IMAGE [IMAGE2 ...]
    python scripts/measure_luminance.py --assert-ratio OLD NEW 0.70

Luminance: 0.2126 R + 0.7152 G + 0.0722 B (Rec. 709), per pixel,
averaged over the whole image. PNG (and WEBP) read via rasterio/GDAL.
With --assert-ratio OLD NEW RATIO, exits 0 iff mean(NEW) <= RATIO *
mean(OLD), else exits 1 and prints both means. The assertion is the
SC-001 gate: the new bundle must be >= (1 - RATIO) darker.
"""
from __future__ import annotations

import argparse
import sys
import warnings

import numpy as np
import rasterio

warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)


def mean_luminance(path: str) -> float:
    with rasterio.open(path) as ds:
        rgb = ds.read([1, 2, 3]).astype(np.float64) / 255.0
    lum = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    return float(lum.mean())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("images", nargs="*", help="image path(s) to measure")
    ap.add_argument(
        "--assert-ratio",
        nargs=3,
        metavar=("OLD", "NEW", "RATIO"),
        help="exit 1 unless mean(NEW) <= RATIO * mean(OLD)",
    )
    args = ap.parse_args()

    if args.assert_ratio:
        old_path, new_path, ratio_s = args.assert_ratio
        old, new = mean_luminance(old_path), mean_luminance(new_path)
        ratio = float(ratio_s)
        print(f"old luminance: {old:.4f}")
        print(f"new luminance: {new:.4f}")
        print(f"ratio new/old: {new / old:.4f} (gate <= {ratio})")
        return 0 if new <= ratio * old else 1

    for path in args.images:
        print(f"{path}: {mean_luminance(path):.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
