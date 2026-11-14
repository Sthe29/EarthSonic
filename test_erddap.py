"""
EarthSonic ERDDAP Integration Test Suite
========================================
Comprehensive automated tests for Milestone 7:
1. Valid offshore Durban coordinate (live + mocked)
2. Land coordinate (Durban Harbor land mask)
3. Invalid latitude and longitude values
4. Invalid dates (bad format, invalid calendar, pre-2002)
5. Missing / fill-value data handling
6. Simulated network timeout and ERDDAP 503/500 upstream errors (mocked)
7. Live ERDDAP end-to-end communication check
"""

import json
from unittest.mock import patch, MagicMock
import urllib.error

from app import app
from erddap_client import fetch_mur_sst, validate_coordinates, validate_date, build_erddap_url

client = app.test_client()


def test_validation_functions():
    print("=== TEST A: UNIT VALIDATION FUNCTIONS ===")
    
    # 1. Valid coordinates
    ok, lat, lon, err = validate_coordinates(-29.85, 31.06)
    assert ok is True and lat == -29.85 and lon == 31.06 and err is None
    
    # 2. String conversion
    ok, lat, lon, err = validate_coordinates("-29.854", " 31.062 ")
    assert ok is True and lat == -29.85 and lon == 31.06 and err is None

    # 3. Invalid latitude
    ok, _, _, err = validate_coordinates(95.0, 31.0)
    assert ok is False and "out of valid range" in err

    # 4. Invalid longitude
    ok, _, _, err = validate_coordinates(0.0, 200.0)
    assert ok is False and "out of valid range" in err

    # 5. Non-numeric
    ok, _, _, err = validate_coordinates("invalid", 31.0)
    assert ok is False and "numeric" in err

    # 6. Missing
    ok, _, _, err = validate_coordinates(None, 31.0)
    assert ok is False and "Missing" in err

    # 7. Valid date
    ok, ts, date_only, err = validate_date("2026-11-13")
    assert ok is True and ts == "2026-11-13T09:00:00Z" and date_only == "2026-11-13"

    # 8. ISO timestamp input
    ok, ts, date_only, err = validate_date("2026-11-13T14:30:00Z")
    assert ok is True and ts == "2026-11-13T09:00:00Z" and date_only == "2026-11-13"

    # 9. Invalid format
    ok, _, _, err = validate_date("13-11-2026")
    assert ok is False and "Expected 'YYYY-MM-DD'" in err

    # 10. Nonexistent calendar date
    ok, _, _, err = validate_date("2026-02-30")
    assert ok is False and "Invalid calendar date" in err

    # 11. Date before dataset commencement (2002-06-01)
    ok, _, _, err = validate_date("1998-05-20")
    assert ok is False and "precedes MUR dataset commencement" in err

    print("Unit validation functions -> ALL PASSED.")


def test_offshore_durban_mocked():
    print("\n=== TEST 1: OFFSHORE DURBAN OCEAN POINT (Mocked & Route Check) ===")
    mock_payload = {
        "table": {
            "columnNames": ["time", "latitude", "longitude", "analysed_sst", "analysis_error", "mask"],
            "rows": [["2026-11-13T09:00:00Z", -29.85, 31.06, 22.858, 0.400, 1]]
        }
    }
    
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps(mock_payload).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        # Test GET
        res = client.get("/api/mur-sst?lat=-29.85&lon=31.06&date=2026-11-13")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.get_json()
        assert data["status"] == "success"
        assert data["is_ocean"] is True
        assert data["mask"] == 1
        assert data["mask_classification"] == "open_sea"
        assert data["analysed_sst_c"] == 22.858
        assert data["analysis_error_c"] == 0.400
        assert data["units"]["analysed_sst"] == "degree_C"
        assert "Level-4" in data["product_type"]

        # Test POST
        res_post = client.post("/api/mur-sst", json={"latitude": -29.85, "longitude": 31.06, "date": "2026-11-13"})
        assert res_post.status_code == 200
        data_post = res_post.get_json()
        assert data_post["status"] == "success"
        assert data_post["analysed_sst_c"] == 22.858

    print(f"Offshore Durban query verified: SST={data['analysed_sst_c']}°C, Mask=1 ({data['mask_classification']}) -> PASSED.")


def test_land_coordinate_mocked():
    print("\n=== TEST 2: LAND COORDINATE (Durban Harbor / City Mask) ===")
    mock_payload = {
        "table": {
            "columnNames": ["time", "latitude", "longitude", "analysed_sst", "analysis_error", "mask"],
            "rows": [["2026-11-13T09:00:00Z", -29.85, 31.02, None, None, 2]]
        }
    }
    
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps(mock_payload).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = client.get("/api/mur-sst?lat=-29.85&lon=31.02&date=2026-11-13")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["is_ocean"] is False
        assert data["mask"] == 2
        assert data["mask_classification"] == "land"
        assert data["analysed_sst_c"] is None
        assert data["analysis_error_c"] is None
        assert "warning" in data
        assert "land" in data["warning"]

    print(f"Land coordinate correctly detected: Mask=2 ({data['mask_classification']}), SST=None (Masked) -> PASSED.")


def test_invalid_coordinates():
    print("\n=== TEST 3: INVALID LATITUDE AND LONGITUDE VALUES ===")
    
    # Latitude > 90
    res = client.get("/api/mur-sst?lat=120.5&lon=31.0")
    assert res.status_code == 400
    assert res.get_json()["error_type"] == "ValidationError"

    # Longitude < -180
    res = client.get("/api/mur-sst?lat=-29.0&lon=-220.0")
    assert res.status_code == 400
    assert res.get_json()["error_type"] == "ValidationError"

    # Non-numeric
    res = client.post("/api/mur-sst", json={"latitude": "abc", "longitude": 31.0})
    assert res.status_code == 400
    assert res.get_json()["error_type"] == "ValidationError"

    # Missing parameters
    res = client.get("/api/mur-sst?lat=0")
    assert res.status_code == 400
    assert res.get_json()["error_type"] == "ValidationError"

    print("Invalid coordinates handled with HTTP 400 and ValidationError -> PASSED.")


def test_invalid_dates():
    print("\n=== TEST 4: INVALID DATE VALUES ===")

    # Garbage date string
    res = client.get("/api/mur-sst?lat=-29.85&lon=31.06&date=not-a-date")
    assert res.status_code == 400
    assert "Expected 'YYYY-MM-DD'" in res.get_json()["message"]

    # Nonexistent date (Feb 30)
    res = client.get("/api/mur-sst?lat=-29.85&lon=31.06&date=2026-02-30")
    assert res.status_code == 400
    assert "Invalid calendar date" in res.get_json()["message"]

    # Date before 2002
    res = client.get("/api/mur-sst?lat=-29.85&lon=31.06&date=1995-12-01")
    assert res.status_code == 400
    assert "precedes MUR dataset commencement" in res.get_json()["message"]

    print("Invalid dates rejected with HTTP 400 and helpful error explanations -> PASSED.")


def test_missing_and_fill_value_handling():
    print("\n=== TEST 5: MISSING AND FILL-VALUE DATA HANDLING ===")
    # Fill value for SST is <= -7.768, error <= -327.68
    mock_payload = {
        "table": {
            "columnNames": ["time", "latitude", "longitude", "analysed_sst", "analysis_error", "mask"],
            "rows": [["2026-11-13T09:00:00Z", 0.0, 0.0, -7.768000000000001, -327.68, 1]]
        }
    }
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps(mock_payload).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = client.get("/api/mur-sst?lat=0.0&lon=0.0")
        assert res.status_code == 200
        data = res.get_json()
        assert data["analysed_sst_c"] is None
        assert data["analysis_error_c"] is None
        assert data["status"] == "success"

    print("Fill values (-7.768, -327.68) cleanly converted to null/None without error -> PASSED.")


def test_simulated_network_and_http_errors():
    print("\n=== TEST 6: SIMULATED TIMEOUT AND HTTP ERRORS ===")

    # 1. Connection Timeout
    with patch("urllib.request.urlopen", side_effect=TimeoutError("Request timed out after 8s")):
        res = client.get("/api/mur-sst?lat=-29.85&lon=31.06")
        assert res.status_code == 504
        assert res.get_json()["error_type"] == "ConnectionTimeoutError"
        print("Simulated timeout -> HTTP 504 Gateway Timeout verified.")

    # 2. HTTP 503 from NOAA ERDDAP
    http_error_503 = urllib.error.HTTPError(
        url="https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41.json",
        code=503,
        msg="Service Unavailable",
        hdrs={},
        fp=MagicMock(read=lambda: b'Error { code=503; message="ERDDAP is busy, try again later"; }')
    )
    with patch("urllib.request.urlopen", side_effect=http_error_503):
        res = client.get("/api/mur-sst?lat=-29.85&lon=31.06")
        assert res.status_code == 502
        data = res.get_json()
        assert data["error_type"] == "ERDDAPHttpError"
        assert "ERDDAP is busy" in data["message"]
        print("Simulated ERDDAP 503 -> HTTP 502 Bad Gateway with upstream message verified.")

    # 3. HTTP 500 from NOAA ERDDAP
    http_error_500 = urllib.error.HTTPError(
        url="https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41.json",
        code=500,
        msg="Internal Server Error",
        hdrs={},
        fp=MagicMock(read=lambda: b'Error { code=500; message="Internal Server Error"; }')
    )
    with patch("urllib.request.urlopen", side_effect=http_error_500):
        res = client.get("/api/mur-sst?lat=-29.85&lon=31.06")
        assert res.status_code == 502
        assert res.get_json()["error_type"] == "ERDDAPHttpError"
        print("Simulated ERDDAP 500 -> HTTP 502 Bad Gateway verified.")


def test_live_erddap_request():
    print("\n=== TEST 7: REAL LIVE REQUEST TO NOAA COASTWATCH ERDDAP ===")
    # Direct live call to test genuine network communication
    try:
        res = client.get("/api/mur-sst?lat=-29.85&lon=31.06&date=2026-11-13")
        print(f"Live ERDDAP HTTP Status: {res.status_code}")
        data = res.get_json()
        
        if res.status_code == 200:
            assert data["status"] == "success"
            assert data["coordinates"]["requested_latitude"] == -29.85
            assert data["coordinates"]["requested_longitude"] == 31.06
            assert data["mask"] == 1
            assert data["mask_classification"] == "open_sea"
            assert isinstance(data["analysed_sst_c"], float)
            assert 15.0 < data["analysed_sst_c"] < 30.0
            print(f"LIVE DATA RETRIEVED: {data['analysed_sst_c']}°C (Error: ±{data['analysis_error_c']}°C, Mask: {data['mask']})")
            print("Live ERDDAP request -> ALL ASSERTIONS PASSED.")
        elif res.status_code == 502 or res.status_code == 504:
            print(f"Notice: Upstream ERDDAP returned temporary service status ({res.status_code}): {data.get('message')}")
            print("Upstream error handled gracefully according to specifications.")
        else:
            raise AssertionError(f"Unexpected status code {res.status_code}: {data}")
    except Exception as exc:
        raise AssertionError(f"Live ERDDAP request failed with unexpected exception: {exc}")


if __name__ == "__main__":
    test_validation_functions()
    test_offshore_durban_mocked()
    test_land_coordinate_mocked()
    test_invalid_coordinates()
    test_invalid_dates()
    test_missing_and_fill_value_handling()
    test_simulated_network_and_http_errors()
    test_live_erddap_request()
    print("\n==================================================")
    print("ALL ERDDAP INTEGRATION TESTS PASSED SUCCESSFULLY!!")
    print("==================================================")
