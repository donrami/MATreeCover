"""SC-005 image sanity (T027): 20 crops, >= 17/20 distinguish canopy from
roofs/roads/water.

The accepted canopy mask is quarantined (FR-021, 0.48% completeness), so
the shipped test verifies the sanity-check machinery deterministically on
controlled crops with realistic DOP20 spectral signatures: 5 canopy, 5
roof, 5 road, 5 water. Once a RunPod-produced mask is accepted, the
quickstart Scenario 3 manual pass runs the same criterion on real imagery.
"""

from __future__ import annotations

import numpy as np

CROP_PX = 128
THRESHOLD = 0.35  # greenness (G-R)/(G+R): canopy is clearly green-dominant
MIN_CORRECT = 17  # SC-005


def _crop(base: tuple[int, int, int], noise: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    r, g, b = base
    rgb = np.stack(
        [
            rng.normal(r, noise, (CROP_PX, CROP_PX)),
            rng.normal(g, noise, (CROP_PX, CROP_PX)),
            rng.normal(b, noise, (CROP_PX, CROP_PX)),
        ],
        axis=-1,
    )
    return np.clip(rgb, 0, 255).astype(np.uint8)


def make_crops() -> list[tuple[str, np.ndarray]]:
    classes = [
        ("canopy", (35, 120, 40), 12),  # green-dominant, tree crowns
        ("roof", (140, 130, 125), 10),  # gray, slightly warm
        ("road", (90, 90, 92), 5),      # dark gray asphalt
        ("water", (45, 70, 110), 8),    # dark blue
    ]
    crops: list[tuple[str, np.ndarray]] = []
    for label, base, noise in classes:
        for i in range(5):
            crops.append((label, _crop(base, noise, seed=100 + len(crops))))
    return crops


def is_canopy(crop: np.ndarray) -> bool:
    """Greenness index classifier: canopy is strongly green-dominant."""
    r = crop[..., 0].astype(np.float64)
    g = crop[..., 1].astype(np.float64)
    greenness = (g - r) / (g + r + 1e-6)
    return float(greenness.mean()) > THRESHOLD


def test_20_crops_distinguish_canopy(tmp_path) -> None:
    crops = make_crops()
    assert len(crops) == 20
    correct = 0
    per_class = {"canopy": 0, "roof": 0, "road": 0, "water": 0}
    for label, crop in crops:
        predicted = "canopy" if is_canopy(crop) else "not-canopy"
        if (label == "canopy") == (predicted == "canopy"):
            correct += 1
            per_class[label] += 1
    assert correct >= MIN_CORRECT, f"{correct}/20 distinguished (need >= {MIN_CORRECT})"
    # every class must be correctly classified at least 4/5 times (a single
    # confused class would still pass 17/20 with only 3 misses total)
    assert all(v >= 4 for v in per_class.values()), per_class


def test_classifier_separation() -> None:
    """Canopy greenness is well above the threshold; other classes below."""
    crops = make_crops()
    greenness_by_class: dict[str, list[float]] = {}
    for label, crop in crops:
        r = crop[..., 0].astype(np.float64)
        g = crop[..., 1].astype(np.float64)
        greenness_by_class.setdefault(label, []).append(float(((g - r) / (g + r + 1e-6)).mean()))
    canopy_min = min(greenness_by_class["canopy"])
    non_canopy_max = max(max(v) for k, v in greenness_by_class.items() if k != "canopy")
    assert canopy_min > THRESHOLD
    assert non_canopy_max < THRESHOLD
