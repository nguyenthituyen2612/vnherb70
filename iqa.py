# -*- coding: utf-8 -*-
"""
iqa.py — P5: Kiểm tra chất lượng ảnh đặc thù cho ảnh cây thuốc.
Trả về điểm số + cờ pass/warn/fail cho từng tiêu chí.
"""
from dataclasses import dataclass, field
from typing import List, Dict
import numpy as np
from PIL import Image

# Ngưỡng — chỉnh tại đây
CFG = {
    "laplacian": {"min": 120.0, "warn_factor": 1.4, "label": "Độ nét (Laplacian var)"},
    "object_ratio": {"min": 0.40, "warn_pad": 0.08, "label": "Đối tượng chiếm khung"},
    "resolution": {"min": 224, "label": "Phân giải cạnh ngắn (px)"},
    "brightness": {"min": 55.0, "max": 215.0, "label": "Độ sáng trung bình"},
    "saturation": {"max": 0.78, "label": "Bão hòa (lọc ảnh filter/nghệ thuật)"},
}


@dataclass
class Check:
    key: str
    label: str
    value: float
    display: str
    status: str  # pass | warn | fail


@dataclass
class IQAResult:
    laplacian: float
    object_ratio: float
    resolution: int
    brightness: float
    saturation: float
    checks: List[Check] = field(default_factory=list)
    passed: bool = False

    def to_dict(self) -> Dict:
        return {
            "passed": self.passed,
            "laplacian_var": round(self.laplacian, 1),
            "object_ratio": round(self.object_ratio, 3),
            "resolution_short_px": self.resolution,
            "brightness_mean": round(self.brightness, 1),
            "saturation_mean": round(self.saturation, 3),
            "flags": [
                {"metric": c.key, "status": c.status, "value": c.display}
                for c in self.checks if c.status != "pass"
            ],
        }


def _laplacian_variance(gray: np.ndarray) -> float:
    k = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    h, w = gray.shape
    # simple valid convolution
    out = (
        gray[:-2, 1:-1] + gray[2:, 1:-1] +
        gray[1:-1, :-2] + gray[1:-1, 2:] -
        4 * gray[1:-1, 1:-1]
    )
    return float(out.var())


def _object_ratio(rgb: np.ndarray) -> float:
    """Ước lượng tỉ lệ foreground bằng cách so với màu nền lấy từ viền ảnh."""
    h, w, _ = rgb.shape
    border = np.concatenate([
        rgb[0, :, :], rgb[-1, :, :], rgb[:, 0, :], rgb[:, -1, :]
    ], axis=0).astype(np.float32)
    bg = border.mean(axis=0)
    dist = np.abs(rgb.astype(np.float32) - bg).sum(axis=2)
    fg = (dist > 60).mean()
    return float(fg)


def analyze(img: Image.Image) -> IQAResult:
    img = img.convert("RGB")
    short_side = min(img.size)
    # downscale for speed but keep ratio info
    work = img.copy()
    work.thumbnail((512, 512))
    rgb = np.asarray(work, dtype=np.uint8)
    gray = (0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]).astype(np.float32)

    laplacian = _laplacian_variance(gray)
    brightness = float(gray.mean())
    mx = rgb.max(axis=2).astype(np.float32)
    mn = rgb.min(axis=2).astype(np.float32)
    sat = np.where(mx == 0, 0, (mx - mn) / np.where(mx == 0, 1, mx))
    saturation = float(sat.mean())
    object_ratio = _object_ratio(rgb)

    checks: List[Check] = []

    # laplacian
    c = CFG["laplacian"]
    st = "pass"
    if laplacian < c["min"]:
        st = "fail"
    elif laplacian < c["min"] * c["warn_factor"]:
        st = "warn"
    checks.append(Check("laplacian", c["label"], laplacian, f"{laplacian:.0f}", st))

    # object ratio
    c = CFG["object_ratio"]
    st = "pass"
    if object_ratio < c["min"]:
        st = "fail"
    elif object_ratio < c["min"] + c["warn_pad"]:
        st = "warn"
    checks.append(Check("object_ratio", c["label"], object_ratio, f"{object_ratio*100:.0f}%", st))

    # resolution
    c = CFG["resolution"]
    st = "pass" if short_side >= c["min"] else "fail"
    checks.append(Check("resolution", c["label"], short_side, f"{short_side}px", st))

    # brightness
    c = CFG["brightness"]
    st = "pass" if c["min"] <= brightness <= c["max"] else "fail"
    checks.append(Check("brightness", c["label"], brightness, f"{brightness:.0f}/255", st))

    # saturation (too high → likely filtered/artistic)
    c = CFG["saturation"]
    st = "fail" if saturation > c["max"] else "pass"
    checks.append(Check("saturation", c["label"], saturation, f"{saturation*100:.0f}%", st))

    passed = all(ch.status != "fail" for ch in checks)
    return IQAResult(laplacian, object_ratio, short_side, brightness, saturation, checks, passed)
