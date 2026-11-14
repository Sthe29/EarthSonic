"""
EarthSonic Vision Engine
========================
Modular OpenCV-based computer vision and scientific calibration engine.
Extracts calibrated Sea Surface Temperature (SST) estimates from NASA
Earth Information Center visualizations (SVS ID 5101 / JPL MUR).
"""

import os
from pathlib import Path
import cv2
import numpy as np

# Base paths
BASE_DIR = Path(__file__).resolve().parent
NASA_DIR = BASE_DIR / "static" / "nasa"
COLORBAR_PATH = NASA_DIR / "sst_mur_colorbar.png"
SST_MAP_PATH = NASA_DIR / "sst_mur_print.jpg"

class VisionEngine:
    """Handles calibration, ROI extraction, and color-to-temperature mapping."""

    def __init__(self, colorbar_path=None):
        self.colorbar_path = Path(colorbar_path) if colorbar_path else COLORBAR_PATH
        self.gradient_bgr = None
        self.gradient_lab = None
        self.temps = None
        self.is_calibrated = False
        self._init_calibration()

    def _init_calibration(self):
        """Extract continuous horizontal gradient from NASA SST colorbar (-5°C to +35°C)."""
        if not self.colorbar_path.exists():
            print(f"Warning: Colorbar file not found at {self.colorbar_path}")
            return

        cb = cv2.imread(str(self.colorbar_path), cv2.IMREAD_UNCHANGED)
        if cb is None:
            print(f"Warning: Could not read colorbar at {self.colorbar_path}")
            return

        # Convert 16-bit to 8-bit if needed
        if cb.dtype == np.uint16:
            cb8 = (cb / 256).astype(np.uint8)
        else:
            cb8 = cb.astype(np.uint8)

        # The calibrated linear range spans from X=480 (-5°C) to X=3365 (+35°C)
        # Vertical strip centered around Y=1080 (Y=1070..1090)
        # Subsample with step=4 for 722 calibration points (smooth and very fast)
        x_start = 480
        x_end = 3365
        step = 4

        strip_bgr = cb8[1070:1090, x_start:x_end:step, :3].mean(axis=0).astype(np.uint8)
        self.gradient_bgr = strip_bgr  # shape (N, 3)

        # Convert to CIE L*a*b* for perceptually uniform Delta E matching
        gradient_lab_2d = cv2.cvtColor(strip_bgr.reshape(1, -1, 3), cv2.COLOR_BGR2LAB)
        self.gradient_lab = gradient_lab_2d.reshape(-1, 3).astype(np.float32)

        # Published NASA temperature range: -5.0°C to +35.0°C
        self.temps = np.linspace(-5.0, 35.0, len(self.gradient_lab)).astype(np.float32)
        self.is_calibrated = True

    def pixel_to_geo(self, x, y, width=1024, height=512):
        """Convert pixel coordinates on equirectangular map to lat/lon degrees."""
        lon = (x / width) * 360.0 - 180.0
        lat = 90.0 - (y / height) * 180.0
        return round(float(lat), 2), round(float(lon), 2)

    def roi_to_geo_bbox(self, x, y, w, h, width=1024, height=512):
        """Convert pixel ROI to geographic bounding box."""
        north_lat, west_lon = self.pixel_to_geo(x, y, width, height)
        south_lat, east_lon = self.pixel_to_geo(x + w, y + h, width, height)
        return {
            "north_lat": north_lat,
            "south_lat": south_lat,
            "west_lon": west_lon,
            "east_lon": east_lon,
            "description": f"{abs(south_lat)}°{'S' if south_lat < 0 else 'N'}–{abs(north_lat)}°{'S' if north_lat < 0 else 'N'}, {abs(west_lon)}°{'W' if west_lon < 0 else 'E'}–{abs(east_lon)}°{'W' if east_lon < 0 else 'E'}"
        }

    def classify_ocean_temp(self, temp_c):
        """Qualitative description of temperature zone."""
        if temp_c is None:
            return "Unknown"
        if temp_c < 0.0:
            return "Freezing Polar Ocean"
        elif temp_c < 10.0:
            return "Cold Subpolar Waters"
        elif temp_c < 18.0:
            return "Temperate Ocean Waters"
        elif temp_c < 26.0:
            return "Subtropical Ocean Waters"
        elif temp_c < 30.0:
            return "Tropical Warm Waters"
        else:
            return "Equatorial Warm Pool (High SST)"

    def estimate_pixel(self, image_bgr, x, y):
        """
        Estimate temperature for a single pixel (x, y).
        Filters out land masks and missing data.
        """
        if not self.is_calibrated:
            return {"error": "Vision engine is not calibrated"}

        h, w = image_bgr.shape[:2]
        x = max(0, min(w - 1, int(x)))
        y = max(0, min(h - 1, int(y)))

        bgr = image_bgr[y, x]
        pixel_bgr_2d = np.array([[bgr]], dtype=np.uint8)
        pixel_lab = cv2.cvtColor(pixel_bgr_2d, cv2.COLOR_BGR2LAB).reshape(3).astype(np.float32)

        # Chroma check: distance from neutral grey (a=128, b=128)
        chroma = float(np.hypot(pixel_lab[1] - 128, pixel_lab[2] - 128))
        luma = float(pixel_lab[0])

        # Gray land/ice mask or border detection
        is_masked = (chroma < 7.5) or (luma < 15.0) or (luma > 245.0)

        # Geographic coordinates if standard 1024x512 equirectangular
        lat, lon = self.pixel_to_geo(x, y, w, h)

        if is_masked:
            return {
                "x": x,
                "y": y,
                "lat": lat,
                "lon": lon,
                "bgr": [int(bgr[0]), int(bgr[1]), int(bgr[2])],
                "rgb": [int(bgr[2]), int(bgr[1]), int(bgr[0])],
                "is_ocean": False,
                "status": "Land mask or non-ocean pixel",
                "chroma": round(chroma, 1),
                "estimated_temp_c": None,
                "confidence": "Excluded (neutral grayscale land/ice mask)"
            }

        # Vectorized Euclidean distance in Lab (Delta E)
        diffs = self.gradient_lab - pixel_lab
        dists = np.sum(diffs**2, axis=1)
        best_idx = int(np.argmin(dists))
        delta_e = float(np.sqrt(dists[best_idx]))
        estimated_temp = round(float(self.temps[best_idx]), 1)

        return {
            "x": x,
            "y": y,
            "lat": lat,
            "lon": lon,
            "bgr": [int(bgr[0]), int(bgr[1]), int(bgr[2])],
            "rgb": [int(bgr[2]), int(bgr[1]), int(bgr[0])],
            "is_ocean": True,
            "status": "Valid ocean measurement",
            "chroma": round(chroma, 1),
            "estimated_temp_c": estimated_temp,
            "classification": self.classify_ocean_temp(estimated_temp),
            "delta_e": round(delta_e, 2),
            "confidence": "High" if delta_e < 5.0 else ("Moderate" if delta_e < 12.0 else "Low")
        }

    def analyze_roi(self, image_bgr, x, y, width, height):
        """
        Analyze a rectangular Region of Interest (ROI).
        Returns valid pixel counts, statistical distribution, land exclusion,
        and geographic alignment.
        """
        if not self.is_calibrated:
            return {"error": "Vision engine is not calibrated"}

        img_h, img_w = image_bgr.shape[:2]

        # Clamp ROI to image boundary
        x0 = max(0, min(img_w - 1, int(x)))
        y0 = max(0, min(img_h - 1, int(y)))
        x1 = max(x0 + 1, min(img_w, int(x + width)))
        y1 = max(y0 + 1, min(img_h, int(y + height)))

        roi_w = x1 - x0
        roi_h = y1 - y0
        total_pixels = roi_w * roi_h

        roi = image_bgr[y0:y1, x0:x1]

        # Convert ROI to Lab
        roi_lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)

        # Calculate Chroma and Luma
        chroma = np.hypot(roi_lab[:, 1] - 128.0, roi_lab[:, 2] - 128.0)
        luma = roi_lab[:, 0]

        # Ocean mask: valid saturated ocean colors, excluding gray continents and polar ice
        ocean_mask = (chroma >= 8.5) & (luma >= 15.0) & (luma <= 245.0)
        valid_pixel_count = int(np.count_nonzero(ocean_mask))
        masked_pixel_count = total_pixels - valid_pixel_count
        ocean_ratio = valid_pixel_count / total_pixels if total_pixels > 0 else 0.0

        geo_bbox = self.roi_to_geo_bbox(x0, y0, roi_w, roi_h, img_w, img_h)

        # If less than 5% ocean in a sizeable box, treat as land/ice mask
        is_predominantly_land = (valid_pixel_count == 0) or (ocean_ratio < 0.05 and total_pixels >= 100)

        if is_predominantly_land:
            return {
                "roi": {"x": x0, "y": y0, "width": roi_w, "height": roi_h},
                "geo_bbox": geo_bbox,
                "total_pixels": total_pixels,
                "valid_pixel_count": valid_pixel_count,
                "masked_pixel_count": masked_pixel_count,
                "ocean_coverage_pct": round(ocean_ratio * 100.0, 1),
                "status": "Continental Land / Sea-Ice Mask",
                "warning": "The selected region is predominantly over continental land or polar ice. Ocean temperature calculation is suppressed to avoid land contamination.",
                "mean_temp_c": None,
                "median_temp_c": None,
                "min_temp_c": None,
                "max_temp_c": None,
                "std_dev_c": None,
                "classification": "Land / Ice Mask",
                "confidence": "Excluded (continental land / sea-ice mask)"
            }

        valid_lab = roi_lab[ocean_mask]

        # Fast vectorized matrix distance against LUT:
        # ||u - v||^2 = ||u||^2 + ||v||^2 - 2 * u . v
        u2 = np.sum(valid_lab**2, axis=1, keepdims=True)
        v2 = np.sum(self.gradient_lab**2, axis=1, keepdims=True).T
        uv = np.dot(valid_lab, self.gradient_lab.T)
        dists = u2 + v2 - 2.0 * uv

        best_indices = np.argmin(dists, axis=1)
        min_dists = np.sqrt(np.take_along_axis(dists, best_indices[:, None], axis=1).squeeze())

        pixel_temps = self.temps[best_indices]

        mean_temp = float(np.mean(pixel_temps))
        median_temp = float(np.median(pixel_temps))
        min_temp = float(np.min(pixel_temps))
        max_temp = float(np.max(pixel_temps))
        std_dev = float(np.std(pixel_temps))
        mean_delta_e = float(np.mean(min_dists))

        # Thermal thermal zones breakdown
        zones = {
            "polar_cold_below_0": round(float(np.count_nonzero(pixel_temps < 0.0) / valid_pixel_count * 100), 1),
            "subpolar_0_to_10": round(float(np.count_nonzero((pixel_temps >= 0.0) & (pixel_temps < 10.0)) / valid_pixel_count * 100), 1),
            "temperate_10_to_20": round(float(np.count_nonzero((pixel_temps >= 10.0) & (pixel_temps < 20.0)) / valid_pixel_count * 100), 1),
            "subtropical_20_to_26": round(float(np.count_nonzero((pixel_temps >= 20.0) & (pixel_temps < 26.0)) / valid_pixel_count * 100), 1),
            "tropical_above_26": round(float(np.count_nonzero(pixel_temps >= 26.0) / valid_pixel_count * 100), 1)
        }

        # Confidence level
        if ocean_ratio > 0.85 and mean_delta_e < 6.0:
            confidence = "High (Clean ocean coverage and close colormap alignment)"
        elif ocean_ratio > 0.40 and mean_delta_e < 10.0:
            confidence = "Moderate (Mixed region with land/coastal masking)"
        else:
            confidence = "Low (High noise, sparse ocean coverage, or colormap disparity)"

        return {
            "roi": {"x": x0, "y": y0, "width": roi_w, "height": roi_h},
            "geo_bbox": geo_bbox,
            "total_pixels": total_pixels,
            "valid_pixel_count": valid_pixel_count,
            "masked_pixel_count": masked_pixel_count,
            "ocean_coverage_pct": round(ocean_ratio * 100.0, 1),
            "mean_temp_c": round(mean_temp, 2),
            "median_temp_c": round(median_temp, 2),
            "min_temp_c": round(min_temp, 2),
            "max_temp_c": round(max_temp, 2),
            "std_dev_c": round(std_dev, 2),
            "classification": self.classify_ocean_temp(mean_temp),
            "mean_delta_e": round(mean_delta_e, 2),
            "confidence": confidence,
            "thermal_zones": zones,
            "scientific_disclaimer": "Experimental visualization-based estimate calibrated against SVS 5101 colormap. Does not replace raw numerical MUR sensor arrays."
        }

# Global instance
engine = VisionEngine()
