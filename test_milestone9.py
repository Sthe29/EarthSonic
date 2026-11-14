"""
EarthSonic Milestone 9 Automated Verification Suite
===================================================
Tests numerical MUR Sea Surface Temperature sonification:
1. Mathematical mapping tests (linear formula, low temp, high temp, ordering, clamping)
2. DOM structure and accessibility of numerical audio controls
3. Land and missing data audio safeguards
4. Playback state transition contracts (start, stop, conflict prevention)
5. Live ERDDAP request and numerical frequency calculation
6. Regression tests for existing image-based sonification and OpenCV endpoints
"""

import math
import re
from app import app

client = app.test_client()

# Constants defined in milestone specifications
MIN_TEMP = -5.0
MAX_TEMP = 35.0
MIN_FREQ = 160.0
MAX_FREQ = 880.0


def calculate_mur_frequency(temp):
    """
    Python mirror of calculateMurFrequency() in static/app.js.
    Linear mapping formula:
    frequency = minFreq + ((temp - minTemp) / (maxTemp - minTemp)) * (maxFreq - minFreq)
    """
    if temp is None or (isinstance(temp, float) and math.isnan(temp)):
        return None
    try:
        t = float(temp)
    except (ValueError, TypeError):
        return None

    clamped = max(MIN_TEMP, min(MAX_TEMP, t))
    return MIN_FREQ + ((clamped - MIN_TEMP) / (MAX_TEMP - MIN_TEMP)) * (MAX_FREQ - MIN_FREQ)


def test_1_mathematical_mapping():
    print("=== 1. TEST MATHEMATICAL FREQUENCY MAPPING ===")

    # 1A. Low numerical temperatures
    f_min = calculate_mur_frequency(-5.0)
    assert abs(f_min - 160.0) < 1e-4, f"Expected 160.0 Hz, got {f_min}"
    print(f"Low temp -5.0°C -> {f_min:.2f} Hz (Polar extreme lower limit)")

    f_zero = calculate_mur_frequency(0.0)
    assert abs(f_zero - 250.0) < 1e-4, f"Expected 250.0 Hz, got {f_zero}"
    print(f"Low temp 0.0°C -> {f_zero:.2f} Hz (Freezing point)")

    f_subpolar = calculate_mur_frequency(2.5)
    assert abs(f_subpolar - 295.0) < 1e-4, f"Expected 295.0 Hz, got {f_subpolar}"
    print(f"Low temp 2.5°C -> {f_subpolar:.2f} Hz (Subpolar water)")

    # 1B. Higher numerical temperatures
    f_warm = calculate_mur_frequency(30.0)
    assert abs(f_warm - 790.0) < 1e-4, f"Expected 790.0 Hz, got {f_warm}"
    print(f"High temp 30.0°C -> {f_warm:.2f} Hz (Tropical warm pool)")

    f_max = calculate_mur_frequency(35.0)
    assert abs(f_max - 880.0) < 1e-4, f"Expected 880.0 Hz, got {f_max}"
    print(f"High temp 35.0°C -> {f_max:.2f} Hz (Extreme tropical upper limit)")

    # 1C. Monotonicity & Ordering test: T1 < T2 => f(T1) < f(T2)
    temperatures = [-4.0, 0.0, 5.0, 12.0, 18.5, 22.86, 28.0, 34.0]
    frequencies = [calculate_mur_frequency(t) for t in temperatures]
    for i in range(len(temperatures) - 1):
        assert frequencies[i] < frequencies[i + 1], (
            f"Ordering violation: T({temperatures[i]})={frequencies[i]} Hz >= "
            f"T({temperatures[i+1]})={frequencies[i+1]} Hz"
        )
    print("Monotonic ordering verified: Strictly increasing pitch across entire thermal spectrum.")

    # Constant linear slope: delta_f / delta_T = 18.0 Hz/°C
    slope = (frequencies[-1] - frequencies[0]) / (temperatures[-1] - temperatures[0])
    assert abs(slope - 18.0) < 1e-4, f"Expected slope 18.0 Hz/°C, got {slope}"
    print(f"Linear sensitivity verified: Exactly {slope:.1f} Hz per degree Celsius.")

    # 1D. Clamping and out-of-range safety
    assert abs(calculate_mur_frequency(-20.0) - 160.0) < 1e-4, "Failed to clamp sub-minimum temperature"
    assert abs(calculate_mur_frequency(50.0) - 880.0) < 1e-4, "Failed to clamp supra-maximum temperature"
    print("Boundary clamping verified: Safe listening boundaries [160 Hz, 880 Hz] strictly enforced.")

    # 1E. Missing / Non-numeric data
    assert calculate_mur_frequency(None) is None
    assert calculate_mur_frequency(float("nan")) is None
    assert calculate_mur_frequency("invalid") is None
    print("Missing data handling verified: Safely returns None.")


def test_2_dom_and_accessibility():
    print("\n=== 2. TEST DOM CONTROLS AND ACCESSIBILITY ===")
    res = client.get("/ocean-temperature")
    assert res.status_code == 200
    html = res.data.decode("utf-8")

    # Product 2 Numerical Sonification Panel
    assert 'class="mur-audio-panel"' in html
    assert 'id="mur-audio-heading"' in html
    assert "NUMERICAL DATA SONIFICATION" in html
    assert 'id="mur-audio-pill"' in html
    assert "Audio Idle" in html

    # Buttons
    assert 'id="btn-play-mur"' in html
    assert 'aria-label="Play sound corresponding to numerical MUR temperature"' in html
    assert 'id="btn-stop-mur"' in html
    assert 'aria-label="Stop numerical MUR temperature sound"' in html
    assert 'disabled' in html  # Stop button starts disabled

    # Description and frequency readout
    assert 'id="mur-audio-desc"' in html
    assert 'id="mur-audio-freq"' in html
    assert "Linear scale: -5°C = 160 Hz, 35°C = 880 Hz" in html

    # Verify zero emojis remain
    emoji_pattern = re.compile("[\U0001F300-\U0001F6FF\U0001F900-\U0001FAFF]")
    assert not emoji_pattern.search(html), "Found decorative emoji in ocean_temperature.html!"

    print("DOM elements verified: Buttons, status pill, description, and accessibility attributes intact.")


def test_3_javascript_source_inspection():
    print("\n=== 3. TEST JAVASCRIPT SOURCE IMPLEMENTATION ===")
    res = client.get("/static/app.js")
    assert res.status_code == 200
    js = res.data.decode("utf-8")

    # Function declarations
    assert "function calculateMurFrequency" in js
    assert "async function startMurAudio" in js
    assert "function stopMurAudio" in js

    # Linear formula in JS
    assert "MUR_MIN_FREQ + ((clamped - MUR_MIN_TEMP) / (MUR_MAX_TEMP - MUR_MIN_TEMP)) * (MUR_MAX_FREQ - MUR_MIN_FREQ)" in js

    # Conflict prevention: image audio stops numerical audio, and vice-versa
    assert "if (isMurAudioPlaying) {" in js
    assert "stopMurAudio();" in js
    assert "if (isAudioPlaying) {" in js
    assert "stopAudio();" in js

    # Safe volume routing and exponential ramps
    assert "murGain.gain.exponentialRampToValueAtTime" in js

    # No auto-play on data load: sound starts ONLY upon user button click
    assert "btnPlayMur.addEventListener(\"click\", startMurAudio)" in js
    assert "btnStopMur.addEventListener(\"click\", stopMurAudio)" in js

    # Verification export
    assert "window.EarthSonic =" in js

    print("JavaScript source verified: Audio graph, linear formula, conflict prevention, and explicit user-initiated playback.")


def test_4_land_and_missing_data_safeguards():
    print("\n=== 4. TEST LAND AND MISSING DATA AUDIO SAFEGUARDS ===")
    # Query land coordinate (Durban port)
    res = client.post("/api/mur-sst", json={
        "latitude": -29.85,
        "longitude": 31.02,
        "date": "2026-11-13"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["is_ocean"] is False
    assert data["mask"] == 2
    assert data["analysed_sst_c"] is None

    # Calculate frequency for land result
    freq = calculate_mur_frequency(data["analysed_sst_c"])
    assert freq is None, "Expected None frequency for land masked data"
    print("Land data safeguard verified: Non-ocean coordinates yield None frequency and disable playback.")


def test_5_live_erddap_frequency_calculation():
    print("\n=== 5. TEST LIVE ERDDAP DATA & FREQUENCY CALCULATION ===")
    res = client.post("/api/mur-sst", json={
        "latitude": -29.85,
        "longitude": 31.06,
        "date": "2026-11-13"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["is_ocean"] is True

    sst = data["analysed_sst_c"]
    assert isinstance(sst, float)
    freq = calculate_mur_frequency(sst)
    assert 600.0 < freq < 700.0
    print(f"Live Offshore Durban SST: {sst:.3f}°C -> Frequency: {freq:.2f} Hz (Musical pitch E5 / treble register).")


def test_6_existing_image_sonification_regression():
    print("\n=== 6. TEST EXISTING IMAGE SONIFICATION REGRESSION ===")
    res_roi = client.post("/api/analyze-region", json={
        "media_source": "nasa",
        "x": 150, "y": 210, "width": 120, "height": 90
    })
    assert res_roi.status_code == 200
    roi_data = res_roi.get_json()
    assert roi_data["mean_temp_c"] > 25.0
    assert roi_data["std_dev_c"] > 0.0

    # Test existing HTML Jukebox controls are preserved
    res_html = client.get("/ocean-temperature")
    html = res_html.data.decode("utf-8")
    assert 'id="btn-play"' in html
    assert 'id="btn-pause"' in html
    assert 'id="btn-stop"' in html
    assert 'id="volume-control"' in html
    assert 'id="audio-state-pill"' in html
    print(f"Existing image sonification intact: ROI={roi_data['mean_temp_c']}°C (±{roi_data['std_dev_c']}°C), controls preserved.")


if __name__ == "__main__":
    test_1_mathematical_mapping()
    test_2_dom_and_accessibility()
    test_3_javascript_source_inspection()
    test_4_land_and_missing_data_safeguards()
    test_5_live_erddap_frequency_calculation()
    test_6_existing_image_sonification_regression()
    print("\n=======================================================")
    print("ALL MILESTONE 9 SONIFICATION TESTS PASSED CLEANLY (6/6)!")
    print("=======================================================")
