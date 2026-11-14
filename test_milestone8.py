"""
EarthSonic Milestone 8 Automated Verification Suite
===================================================
Tests frontend integration of numerical MUR SST data:
1. Template inspection (DOM elements, form inputs, accessibility, no emojis)
2. Real live ERDDAP request (offshore Durban coordinates)
3. Land coordinate masking request (Durban port)
4. Invalid coordinates validation (HTTP 400)
5. Invalid date validation (HTTP 400)
6. Network failure / upstream error handling (HTTP 502/504)
7. Existing OpenCV image analysis regression (ROI and single pixel)
8. Existing upload workflow regression
9. Existing navigation regression (Landing <-> Workspace)
"""

import io
import re
from unittest.mock import patch, MagicMock
import urllib.error
from app import app

client = app.test_client()


def test_1_template_inspection():
    print("=== 1. TEST FRONTEND TEMPLATE INSPECTION ===")
    res = client.get("/ocean-temperature")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    html = res.data.decode("utf-8")

    # Product 1: Visualization estimate
    assert "PRODUCT 1: VISUALIZATION ESTIMATE" in html
    assert "Colormap Temperature Analysis" in html
    assert 'id="temp-primary-value"' in html

    # Product 2: Numerical MUR data
    assert "PRODUCT 2: AUTHENTIC NUMERICAL DATA" in html
    assert "NASA/JPL MUR Analysis (via NOAA ERDDAP)" in html
    assert 'id="mur-query-form"' in html
    assert 'id="mur-input-lat"' in html
    assert 'id="mur-input-lon"' in html
    assert 'id="mur-input-date"' in html
    assert 'id="btn-fetch-mur"' in html
    assert 'id="btn-sync-canvas-coords"' in html
    assert 'id="mur-loading"' in html
    assert 'id="mur-error"' in html
    assert 'id="mur-results"' in html
    assert 'id="mur-temp-value"' in html
    assert 'id="mur-mask-pill"' in html
    assert 'id="mur-error-val"' in html

    # Labels and accessibility
    assert '<label for="mur-input-lat">' in html
    assert '<label for="mur-input-lon">' in html
    assert '<label for="mur-input-date">' in html
    assert 'role="region"' in html
    assert 'role="status"' in html
    assert 'role="alert"' in html

    # Verify zero emojis in rendered HTML
    emoji_pattern = re.compile(
        "[\U0001F1E0-\U0001F1FF"
        "\U0001F300-\U0001F5FF"
        "\U0001F600-\U0001F64F"
        "\U0001F680-\U0001F6FF"
        "\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF"
        "\U0001F800-\U0001F8FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\U00002702-\U000027B0]"
    )
    assert not emoji_pattern.search(html), "Found emoji in ocean_temperature.html!"

    print("Template inspection: Product 1 and Product 2 DOM components, labels, and zero emojis -> PASSED.")


def test_2_live_offshore_durban():
    print("\n=== 2. TEST LIVE ERDDAP REQUEST (Offshore Durban) ===")
    res = client.post("/api/mur-sst", json={
        "latitude": -29.85,
        "longitude": 31.06,
        "date": "2026-11-13"
    })
    print(f"HTTP Status: {res.status_code}")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.get_json()
    assert data["status"] == "success"
    assert data["is_ocean"] is True
    assert data["mask"] == 1
    assert data["mask_classification"] == "open_sea"
    assert isinstance(data["analysed_sst_c"], float)
    assert 20.0 < data["analysed_sst_c"] < 26.0
    assert data["analysis_error_c"] is not None
    assert "Level-4" in data["product_type"]
    print(f"Live Offshore Durban: SST={data['analysed_sst_c']}°C, Error=±{data['analysis_error_c']}°C -> PASSED.")


def test_3_land_coordinate():
    print("\n=== 3. TEST LAND COORDINATE (Durban Harbor / City Mask) ===")
    res = client.post("/api/mur-sst", json={
        "latitude": -29.85,
        "longitude": 31.02,
        "date": "2026-11-13"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["is_ocean"] is False
    assert data["mask"] == 2
    assert data["mask_classification"] == "land"
    assert data["analysed_sst_c"] is None
    assert data["analysis_error_c"] is None
    assert "warning" in data
    print(f"Land Coordinate: Mask={data['mask']} ({data['mask_classification']}), SST=None (Masked) -> PASSED.")


def test_4_invalid_coordinates():
    print("\n=== 4. TEST INVALID COORDINATES VALIDATION ===")
    # Out of range latitude
    res1 = client.post("/api/mur-sst", json={"latitude": 105.0, "longitude": 31.06})
    assert res1.status_code == 400
    assert res1.get_json()["error_type"] == "ValidationError"

    # Out of range longitude
    res2 = client.post("/api/mur-sst", json={"latitude": -29.85, "longitude": -200.0})
    assert res2.status_code == 400
    assert res2.get_json()["error_type"] == "ValidationError"

    # Non-numeric
    res3 = client.post("/api/mur-sst", json={"latitude": "bad", "longitude": 31.06})
    assert res3.status_code == 400

    print("Invalid coordinates rejected with HTTP 400 ValidationError -> PASSED.")


def test_5_invalid_dates():
    print("\n=== 5. TEST INVALID DATES VALIDATION ===")
    # Pre-dataset commencement (<2002)
    res1 = client.post("/api/mur-sst", json={"latitude": -29.85, "longitude": 31.06, "date": "1999-01-01"})
    assert res1.status_code == 400
    assert "precedes MUR dataset commencement" in res1.get_json()["message"]

    # Invalid calendar date
    res2 = client.post("/api/mur-sst", json={"latitude": -29.85, "longitude": 31.06, "date": "2026-02-30"})
    assert res2.status_code == 400
    assert "Invalid calendar date" in res2.get_json()["message"]

    # Garbage string
    res3 = client.post("/api/mur-sst", json={"latitude": -29.85, "longitude": 31.06, "date": "invalid"})
    assert res3.status_code == 400

    print("Invalid dates rejected with HTTP 400 ValidationError -> PASSED.")


def test_6_network_and_upstream_failures():
    print("\n=== 6. TEST NETWORK AND UPSTREAM FAILURE SIMULATION ===")
    # Simulated Timeout
    with patch("urllib.request.urlopen", side_effect=TimeoutError("Connection timed out after 8s")):
        res = client.post("/api/mur-sst", json={"latitude": -29.85, "longitude": 31.06})
        assert res.status_code == 504
        assert res.get_json()["error_type"] == "ConnectionTimeoutError"
        print("Timeout simulation -> HTTP 504 verified.")

    # Simulated ERDDAP 503
    mock_503 = urllib.error.HTTPError(
        url="https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41.json",
        code=503,
        msg="Service Unavailable",
        hdrs={},
        fp=MagicMock(read=lambda: b'Error { code=503; message="ERDDAP is busy"; }')
    )
    with patch("urllib.request.urlopen", side_effect=mock_503):
        res = client.post("/api/mur-sst", json={"latitude": -29.85, "longitude": 31.06})
        assert res.status_code == 502
        assert "ERDDAP is busy" in res.get_json()["message"]
        print("Upstream 503 simulation -> HTTP 502 with message verified.")


def test_7_existing_image_analysis():
    print("\n=== 7. TEST EXISTING OPENCV IMAGE ANALYSIS REGRESSION ===")
    # Region analysis
    roi_res = client.post("/api/analyze-region", json={
        "media_source": "nasa",
        "x": 150, "y": 210, "width": 120, "height": 90
    })
    assert roi_res.status_code == 200
    roi_data = roi_res.get_json()
    assert roi_data["ocean_coverage_pct"] > 90.0
    assert roi_data["mean_temp_c"] > 25.0
    print(f"OpenCV ROI Analysis: {roi_data['mean_temp_c']}°C ({roi_data['classification']}) -> PASSED.")

    # Pixel sampling
    px_res = client.post("/api/sample-pixel", json={
        "media_source": "nasa",
        "x": 420, "y": 160
    })
    assert px_res.status_code == 200
    px_data = px_res.get_json()
    assert px_data["is_ocean"] is True
    assert 20.0 < px_data["estimated_temp_c"] < 26.0
    print(f"OpenCV Pixel Sampling: {px_data['estimated_temp_c']}°C -> PASSED.")


def test_8_existing_upload_workflow():
    print("\n=== 8. TEST EXISTING UPLOAD FUNCTIONALITY REGRESSION ===")
    fake_img = io.BytesIO(b"fake-image-bytes-for-regression-test")
    up_res = client.post("/ocean-temperature", data={"media": (fake_img, "test_upload.png")}, content_type="multipart/form-data")
    assert up_res.status_code == 200
    assert b"test_upload.png" in up_res.data
    print("Upload workflow on /ocean-temperature -> PASSED.")


def test_9_existing_dashboard_navigation():
    print("\n=== 9. TEST EXISTING DASHBOARD NAVIGATION REGRESSION ===")
    # Landing page
    landing_res = client.get("/")
    assert landing_res.status_code == 200
    assert b"Listen to Our Changing Planet" in landing_res.data
    assert b"Sea Surface Temperature (SST)" in landing_res.data
    assert b"/ocean-temperature" in landing_res.data

    # Return link from workspace
    sst_res = client.get("/ocean-temperature")
    assert sst_res.status_code == 200
    assert b'href="/"' in sst_res.data
    print("Dashboard navigation between Landing and Ocean Temperature -> PASSED.")


if __name__ == "__main__":
    test_1_template_inspection()
    test_2_live_offshore_durban()
    test_3_land_coordinate()
    test_4_invalid_coordinates()
    test_5_invalid_dates()
    test_6_network_and_upstream_failures()
    test_7_existing_image_analysis()
    test_8_existing_upload_workflow()
    test_9_existing_dashboard_navigation()
    print("\n=======================================================")
    print("ALL MILESTONE 8 INTEGRATION TESTS PASSED CLEANLY (9/9)!")
    print("=======================================================")
