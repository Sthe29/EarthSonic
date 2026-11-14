"""
EarthSonic ERDDAP Client
========================
Client module connecting EarthSonic to the NASA/JPL MUR Sea Surface
Temperature (SST) dataset hosted on NOAA CoastWatch ERDDAP.

Dataset: GHRSST Level 4 MUR Global Foundation Sea Surface Temperature (v4.1)
Provider: NASA JPL / NOAA CoastWatch
ERDDAP Dataset ID: jplMURSST41
Endpoint: https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41

Important Scientific Distinction:
This is a Level-4 (L4) blended foundation sea surface temperature analysis
synthesised from multiple satellite radiometers (infrared MODIS/AVHRR,
microwave AMSR2) and in-situ buoys via Multi-Resolution Variational Analysis
(MRVA). It is an analysed gridded product, not a single raw instrument reading.
"""

from datetime import datetime, timezone
import json
import re
import urllib.error
import urllib.request
from typing import Any, Dict, Optional, Tuple

# Endpoint Configuration
ERDDAP_BASE_URL = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41.json"
DATASET_ID = "jplMURSST41"
DATA_SOURCE = "NASA/JPL MUR-JPL-L4-GLOB-v4.1 via NOAA CoastWatch ERDDAP (jplMURSST41)"
PRODUCT_TYPE = "Level-4 (L4) Blended Foundation SST Analysis (Analyzed gridded product, not a single sensor measurement)"

# Coordinate & Temporal Boundaries
MIN_LAT = -89.99
MAX_LAT = 89.99
MIN_LON = -179.99
MAX_LON = 180.00
EARLIEST_DATE = "2002-06-01"
DEFAULT_REFERENCE_DATE = "2026-11-13"  # Verified stable timestamp
DEFAULT_TIMEOUT_SECONDS = 8.0

# Fill values defined in ERDDAP metadata
SST_FILL_VALUE = -7.768
ERROR_FILL_VALUE = -327.68
MASK_FILL_VALUE = -128

# Categorical Mask Flag Definitions
MASK_DEFINITIONS = {
    1: {
        "label": "open_sea",
        "is_ocean": True,
        "description": "Valid open ocean water"
    },
    2: {
        "label": "land",
        "is_ocean": False,
        "description": "Continental land or island mass (ocean temperature masked)"
    },
    4: {
        "label": "open_lake",
        "is_ocean": False,
        "description": "Inland freshwater lake"
    },
    8: {
        "label": "open_sea_with_ice",
        "is_ocean": False,
        "description": "Polar open sea with sea ice in grid cell"
    },
    16: {
        "label": "open_lake_with_ice",
        "is_ocean": False,
        "description": "Inland lake with surface ice in grid cell"
    }
}


def validate_coordinates(lat_val: Any, lon_val: Any) -> Tuple[bool, Optional[float], Optional[float], Optional[str]]:
    """
    Validate and round geographic coordinates to 0.01-degree grid resolution.

    Returns:
        (is_valid, rounded_lat, rounded_lon, error_message)
    """
    if lat_val is None:
        return False, None, None, "Missing required parameter: latitude."
    if lon_val is None:
        return False, None, None, "Missing required parameter: longitude."

    try:
        lat = float(lat_val)
    except (ValueError, TypeError):
        return False, None, None, f"Invalid latitude '{lat_val}'. Must be a valid numeric value."

    try:
        lon = float(lon_val)
    except (ValueError, TypeError):
        return False, None, None, f"Invalid longitude '{lon_val}'. Must be a valid numeric value."

    if not (MIN_LAT <= lat <= MAX_LAT) and not (-90.0 <= lat <= 90.0):
        return False, None, None, f"Latitude {lat} out of valid range [-90.0, 90.0]."

    # Clamp extreme poles to valid grid bounds (-89.99 to 89.99)
    lat_clamped = max(MIN_LAT, min(MAX_LAT, lat))

    if not (-180.0 <= lon <= 180.0):
        return False, None, None, f"Longitude {lon} out of valid range [-180.0, 180.0]."

    lon_clamped = max(MIN_LON, min(MAX_LON, lon))

    # MUR grid has 0.01-degree spacing
    return True, round(lat_clamped, 2), round(lon_clamped, 2), None


def validate_date(date_val: Optional[Any]) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """
    Validate date string and format to ERDDAP timestamp YYYY-MM-DDT09:00:00Z.

    Returns:
        (is_valid, formatted_timestamp, date_only, error_message)
    """
    if date_val is None or (isinstance(date_val, str) and not date_val.strip()):
        date_str = DEFAULT_REFERENCE_DATE
    else:
        date_str = str(date_val).strip()

    # Match YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ
    date_match = re.match(r"^(\d{4}-\d{2}-\d{2})(?:T.*)?$", date_str)
    if not date_match:
        return False, None, None, f"Invalid date format '{date_str}'. Expected 'YYYY-MM-DD'."

    date_part = date_match.group(1)

    try:
        parsed_dt = datetime.strptime(date_part, "%Y-%m-%d")
    except ValueError:
        return False, None, None, f"Invalid calendar date '{date_part}'."

    earliest_dt = datetime.strptime(EARLIEST_DATE, "%Y-%m-%d")
    if parsed_dt < earliest_dt:
        return False, None, None, f"Date '{date_part}' precedes MUR dataset commencement ({EARLIEST_DATE})."

    # Format standard MUR daily cadence at 09:00:00Z
    formatted_timestamp = f"{date_part}T09:00:00Z"
    return True, formatted_timestamp, date_part, None


def build_erddap_url(lat: float, lon: float, timestamp: str) -> str:
    """
    Construct properly encoded ERDDAP griddap request URL for point data.
    """
    variables = ["analysed_sst", "analysis_error", "mask"]
    query_parts = [
        f"{var}[({timestamp})][({lat}):1:({lat})][({lon}):1:({lon})]"
        for var in variables
    ]
    return f"{ERDDAP_BASE_URL}?{','.join(query_parts)}"


def fetch_mur_sst(
    lat_val: Any,
    lon_val: Any,
    date_val: Optional[Any] = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS
) -> Dict[str, Any]:
    """
    Fetch numerical Sea Surface Temperature data for a specific geographic point.

    Returns a structured dictionary indicating success or failure.
    """
    # 1. Coordinate Validation
    coord_valid, lat, lon, coord_err = validate_coordinates(lat_val, lon_val)
    if not coord_valid:
        return {
            "status": "error",
            "error_type": "ValidationError",
            "message": coord_err,
            "data_source": DATA_SOURCE
        }

    # 2. Date Validation
    date_valid, timestamp, date_only, date_err = validate_date(date_val)
    if not date_valid:
        return {
            "status": "error",
            "error_type": "ValidationError",
            "message": date_err,
            "data_source": DATA_SOURCE
        }

    # 3. Construct URL
    url = build_erddap_url(lat, lon, timestamp)

    # 4. Execute HTTP Request
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "EarthSonic-Flask/1.0 (NASA Space Apps Challenge 2026; Accessible Earth Data)",
            "Accept": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.status
            raw_bytes = response.read()
    except urllib.error.HTTPError as http_err:
        err_msg = f"NOAA ERDDAP HTTP error {http_err.code}: {http_err.reason}"
        try:
            body = http_err.read().decode("utf-8", errors="replace")
            # Extract ERDDAP Error message if present
            msg_match = re.search(r'message="([^"]+)"', body)
            if msg_match:
                err_msg = f"NOAA ERDDAP Error: {msg_match.group(1)}"
        except Exception:
            pass
        return {
            "status": "error",
            "error_type": "ERDDAPHttpError",
            "http_status": http_err.code,
            "message": err_msg,
            "data_source": DATA_SOURCE
        }
    except (urllib.error.URLError, TimeoutError) as net_err:
        return {
            "status": "error",
            "error_type": "ConnectionTimeoutError" if isinstance(net_err, TimeoutError) else "NetworkError",
            "message": f"Failed to connect to NOAA CoastWatch ERDDAP service: {str(net_err)}",
            "data_source": DATA_SOURCE
        }
    except Exception as exc:
        return {
            "status": "error",
            "error_type": "UnexpectedError",
            "message": f"Unexpected error during ERDDAP query: {str(exc)}",
            "data_source": DATA_SOURCE
        }

    # 5. Parse JSON
    try:
        data = json.loads(raw_bytes.decode("utf-8"))
        table = data.get("table", {})
        col_names = table.get("columnNames", [])
        rows = table.get("rows", [])
    except Exception as parse_err:
        return {
            "status": "error",
            "error_type": "ParseError",
            "message": f"Failed to parse ERDDAP JSON response: {str(parse_err)}",
            "data_source": DATA_SOURCE
        }

    if not rows:
        return {
            "status": "error",
            "error_type": "NoDataFound",
            "message": f"No data returned from ERDDAP for coordinates ({lat}, {lon}) on {timestamp}.",
            "data_source": DATA_SOURCE
        }

    # 6. Extract Row Values
    row = rows[0]
    col_index = {col: i for i, col in enumerate(col_names)}

    raw_time = row[col_index.get("time", 0)] if "time" in col_index else timestamp
    grid_lat = row[col_index.get("latitude", 1)] if "latitude" in col_index else lat
    grid_lon = row[col_index.get("longitude", 2)] if "longitude" in col_index else lon
    raw_sst = row[col_index.get("analysed_sst", 3)] if "analysed_sst" in col_index else None
    raw_err = row[col_index.get("analysis_error", 4)] if "analysis_error" in col_index else None
    raw_mask = row[col_index.get("mask", 5)] if "mask" in col_index else None

    # 7. Evaluate Mask and Interpret Values
    mask_int = int(raw_mask) if raw_mask is not None and raw_mask != MASK_FILL_VALUE else None
    mask_info = MASK_DEFINITIONS.get(
        mask_int,
        {
            "label": "unknown_mask",
            "is_ocean": False,
            "description": f"Unrecognized mask flag value ({mask_int})"
        }
    )

    is_ocean = mask_info["is_ocean"]

    # SST value evaluation (native units are degree_C)
    if raw_sst is None or raw_sst <= SST_FILL_VALUE:
        sst_c = None
    else:
        sst_c = round(float(raw_sst), 3)

    # Analysis error evaluation
    if raw_err is None or raw_err <= ERROR_FILL_VALUE or raw_err < 0.0:
        error_c = None
    else:
        error_c = round(float(raw_err), 3)

    response_payload = {
        "status": "success",
        "coordinates": {
            "requested_latitude": lat,
            "requested_longitude": lon,
            "grid_latitude": grid_lat,
            "grid_longitude": grid_lon
        },
        "time": {
            "requested_date": date_only,
            "dataset_timestamp": raw_time
        },
        "analysed_sst_c": sst_c,
        "analysis_error_c": error_c,
        "mask": mask_int,
        "mask_classification": mask_info["label"],
        "mask_description": mask_info["description"],
        "is_ocean": is_ocean,
        "units": {
            "analysed_sst": "degree_C",
            "analysis_error": "degree_C"
        },
        "data_source": DATA_SOURCE,
        "product_type": PRODUCT_TYPE
    }

    if not is_ocean:
        response_payload["warning"] = (
            f"Point ({lat}, {lon}) is classified as '{mask_info['label']}' ({mask_info['description']}). "
            "Ocean temperature data is masked in the MUR dataset."
        )

    return response_payload
