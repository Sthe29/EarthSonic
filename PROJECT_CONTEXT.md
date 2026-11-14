# EarthSonic — Permanent Project Context & Technical Architecture

> **Document Status:** Active Technical Reference  
> **Last Updated:** 2026-11-14  
> **Repository Root:** `C:\Users\User\Videos\EarthSonic-main`  
> **Challenge:** NASA Space Apps Challenge 2026 — *The Earth Information Jukebox* (Durban Local Event)  
> **Maintenance Rule:** Every engineering task that modifies this project must update this document.

---

## 1. Project Overview

### 1.1 What EarthSonic Is
EarthSonic is a modular Earth science data sonification platform. It converts NASA Earth Information Center (EIC) scientific visualizations and datasets into intuitive, accessible, non-speech audio soundscapes.

### 1.2 Purpose and Intended Users
Scientific visualizations communicate crucial environmental changes, but visual-only experiences can exclude blind and low-vision audiences and remain difficult for general audiences to interpret. EarthSonic bridges this gap by translating visual and numerical data features (such as thermal gradients, velocity fields, and geographic variance) into musical pitch, harmonic timbre, and acoustic texture.
- **Primary Audience:** Blind and low-vision students, researchers, and science center visitors who require multi-sensory Earth data access.
- **Secondary Audience:** Educators, sighted researchers, and museum attendees seeking a multi-sensory perspective on global environmental dynamics.

### 1.3 NASA Space Apps Challenge Context
EarthSonic was conceived for the NASA Space Apps Challenge 2026 challenge track: **"The Earth Information Jukebox"**. The challenge invites participants to transform NASA Earth Information Center displays into interactive, data-driven audio experiences.

### 1.4 The Accessibility Objective
EarthSonic is engineered around universal design:
- High-contrast visual representations.
- Non-speech sonification where physical dimensions directly control sound parameters.
- Screen-reader compatibility using ARIA live regions (`aria-live="polite"`).
- Keyboard shortcuts and focus management.
- Plain-language scientific explanations for every auditory feature.

---

## 2. Current Application Structure

EarthSonic is organized into a modular platform consisting of a central landing page and dedicated scientific workspaces.

```
+----------------------------------------------------------------------------------------------------+
|                                    LANDING DASHBOARD (/)                                           |
|                     Modular scientific exploration suite with 4 module cards                       |
+----------------------------------------------------------------------------------------------------+
                                      |
         +----------------------------+----------------------------+-------------------------+
         |                                                         |                         |
         v                                                         v                         v
+-------------------------------+                            +------------+            +------------+
|  OCEAN TEMPERATURE WORKSPACE  |                            |   OCEAN    |            |  WEATHER & |
|     (/ocean-temperature)      |                            |  CURRENTS  |            | ATMOSPHERE |
|                               |                            | (Disabled) |            | (Disabled) |
| • SVS 5101 Equirectangular    |                            +------------+            +------------+
| • OpenCV CIE Lab Calibration  |
| • ROI Bounding Box & Point    |
| • Dual-Oscillator Web Audio   |
| • Land / Sea-Ice Masking      |
| • Upload Drawer (Custom Media)|
+-------------------------------+
```

### 2.1 The Modular Landing Dashboard (`/`)
Located at the root route (`GET /`), [templates/landing.html](file:///C:/Users/User/Videos/EarthSonic-main/templates/landing.html) introduces the platform and presents four scientific modules:
1. **Sea Surface Temperature (SST):**  
   - *Status:* **Available Now** (active emerald badge).  
   - *Action:* Launches the dedicated SST workspace (`/ocean-temperature`).
2. **Ocean Currents & Circulation:**  
   - *Status:* **Coming Soon** (amber badge).  
   - *Action:* Clean disabled state (`btn-disabled-module`, `aria-disabled="true"`, zero broken links).
3. **Weather & Atmosphere:**  
   - *Status:* **Coming Soon** (amber badge).  
   - *Action:* Clean disabled state.
4. **More Earth Data (Biosphere & Cryosphere):**  
   - *Status:* **Planned Module** (slate/blue badge).  
   - *Action:* Clean disabled state.

### 2.2 The Ocean Temperature Workspace (`/ocean-temperature`)
Located at route `GET, POST /ocean-temperature`, [templates/ocean_temperature.html](file:///C:/Users/User/Videos/EarthSonic-main/templates/ocean_temperature.html) houses the working Sea Surface Temperature sonification engine:
- **Navigation:** Header includes a prominent `← All Modules` button and brand link returning to the landing page (`/`).
- **Visual Display:** Interactive HTML5 canvas rendering NASA SVS ID 5101 global SST equirectangular visualization.
- **Selection Tools:** Drag-and-drop bounding box (ROI mode) and single-pixel inspection (Point mode).
- **Preset Quick Regions:** 1-click exploration buttons for the Equatorial Pacific, North Atlantic, Southern Polar Ocean, Mediterranean Sea, and Sahara Desert (land mask test).
- **Auditory Jukebox:** Controls for Play, Pause, Stop, Volume, and real-time audio state indicator.
- **Readout Panel:** Primary temperature display, classification pill, 6-metric grid, and 5-zone thermal distribution bar.
- **Alternative Upload Drawer:** Collapsible panel preserving user upload functionality.

### 2.3 Application Routes and HTTP Methods
- `GET /`: Renders `landing.html`.
- `GET /ocean-temperature`: Renders `ocean_temperature.html` with default NASA SVS 5101 imagery.
- `POST /ocean-temperature`: Handles file uploads (images/videos up to 250 MB), saving them to `uploads/` and loading them in the workspace.
- `GET /uploads/<path:filename>`: Safely serves uploaded media via Flask `send_from_directory`.
- `POST /api/analyze-region`: REST endpoint accepting JSON `{ media_source, filename, x, y, width, height }`; returns OpenCV ROI statistics.
- `POST /api/sample-pixel`: REST endpoint accepting JSON `{ media_source, filename, x, y }`; returns single-pixel statistics.
- `GET /api/dataset-info`: REST endpoint returning dataset metadata.
- `GET, POST /api/mur-sst`: REST endpoint querying authentic numerical Level-4 MUR Sea Surface Temperature from NOAA CoastWatch ERDDAP (`jplMURSST41`). Accepts query parameters `?lat=...&lon=...&date=...` (GET) or JSON payload `{"latitude": ..., "longitude": ..., "date": ...}` (POST). Returns temperature in Celsius, observation error, mask status, and dataset provenance.

---

## 3. Technology Stack

| Layer | Technology | Version | Purpose in EarthSonic |
| :--- | :--- | :--- | :--- |
| **Backend Runtime** | Python (Windows x64) | `3.14.2` | Application server and computer vision environment. |
| **Web Framework** | Flask | `3.1.3` | HTTP routing, template rendering, upload handling, REST API endpoints. |
| **WSGI / Utilities** | Werkzeug, Jinja2, Click | `3.1.9`, `3.1.6`, `8.5.1` | Form parsing, template inheritance, safe filename generation. |
| **Computer Vision** | OpenCV (`opencv-python`) | `5.0.0.93` | Colorbar gradient sampling, color-space conversions (CIE L\*a\*b\*), ROI array slicing, distance matrix operations. |
| **Numerical Computing**| NumPy | `2.5.4` | Vectorized matrix operations, standard deviation, percentile masking, statistics. |
| **Frontend Core** | Vanilla HTML5 & CSS3 | Standard | Semantic layout, ARIA live accessibility, custom dark scientific theme. |
| **Client Rendering** | HTML5 Canvas 2D API | Standard | Equirectangular map rendering, bounding box drag-and-drop, pixel coordinate mapping. |
| **Audio Synthesis** | Web Audio API | Standard | Dual-oscillator synthesizer (master sine pitch + LFO tremolo modulation + GainNode). |

> **Note on OpenCV:** The folder `C:\Users\User\Videos\opencv-5.0.0` was an uncompiled C++ source archive. EarthSonic does not compile from source; it uses the official precompiled binary wheel `opencv-python==5.0.0.93` installed directly in the project's virtual environment (`.venv`).

---

## 4. Project File Structure

```text
C:\Users\User\Videos\EarthSonic-main\
├── .git/                               # Git version control repository
├── .gitignore                          # Ignores .venv/, uploads/, __pycache__/, etc.
├── .venv/                              # Isolated Python 3.14 virtual environment
├── app.py                              # Flask application controller & API routes (183 lines)
├── erddap_client.py                    # NOAA CoastWatch ERDDAP MUR SST client & validator (245 lines)
├── vision_engine.py                    # Modular OpenCV computer vision & calibration engine (283 lines)
├── requirements.txt                    # Project dependency manifest (Flask, opencv-python, numpy)
├── README.txt                          # Legacy developer notes from original prototype
├── test_modular.py                     # Automated UI & OpenCV regression test suite (6 test cases)
├── test_erddap.py                      # Automated ERDDAP integration test suite (7 test scenarios)
├── test_milestone8.py                  # Automated frontend numerical integration test suite (9 test cases)
├── test_milestone9.py                  # Automated numerical sonification test suite (6 test scenarios)
├── PROJECT_CONTEXT.md                  # This permanent project technical memory document
├── static/
│   ├── app.js                          # Client canvas interaction, API client, Web Audio engine (773 lines)
│   ├── style.css                       # Modern dark scientific dashboard & landing styles (1,436 lines)
│   └── nasa/
│       ├── sst_mur_print.jpg           # NASA SVS 5101 Equirectangular SST map (1024×512, JPEG)
│       ├── sst_mur_colorbar.png        # NASA master colorbar graphic (3840×2160, RGBA, 16-bit)
│       └── colorbar_cropped.png        # Cropped legend graphic displayed in the UI (3360×750, PNG)
├── templates/
│   ├── landing.html                    # Modular landing dashboard with 4 scientific exploration cards
│   ├── ocean_temperature.html          # Dedicated Ocean Temperature workspace with dual-product panels (430 lines)
│   └── index.html                      # Backward-compatible template (includes ocean_temperature.html)
└── uploads/                            # Server directory storing user-uploaded media files
```

### Detailed File Responsibilities
- **[app.py](file:///C:/Users/User/Videos/EarthSonic-main/app.py):**  
  Entry point for Flask. Manages configuration, routes `/` and `/ocean-temperature`, upload file size limits (250 MB), static file serving from `uploads/`, `/api/analyze-region`, `/api/sample-pixel`, `/api/dataset-info`, and `/api/mur-sst`.
- **[erddap_client.py](file:///C:/Users/User/Videos/EarthSonic-main/erddap_client.py):**  
  Dedicated scientific data client for NOAA CoastWatch ERDDAP (`jplMURSST41`):
  - `validate_coordinates(lat, lon)`: Validates ranges ($[-90^\circ, 90^\circ]$ and $[-180^\circ, 180^\circ]$) and snaps to 0.01° grid.
  - `validate_date(date_val)`: Validates format (`YYYY-MM-DD`), enforces dataset boundary ($\ge 2002-06-01$), and formats to daily `09:00:00Z` timestamp.
  - `build_erddap_url(lat, lon, timestamp)`: Constructs properly dimensioned ERDDAP griddap query.
  - `fetch_mur_sst(lat, lon, date_val, timeout)`: Executes HTTP request with 8-second timeout, parses JSON payload, handles missing/fill values, maps categorical mask flags (`open_sea`, `land`, `open_lake`, `open_sea_with_ice`, `open_lake_with_ice`), and formats structured response in degrees Celsius.
- **[vision_engine.py](file:///C:/Users/User/Videos/EarthSonic-main/vision_engine.py):**  
  Core computer vision module:
  - `VisionEngine._init_calibration()`: Reads `sst_mur_colorbar.png`, samples the horizontal gradient from $X=480$ ($-5^\circ\text{C}$) to $X=3365$ ($+35^\circ\text{C}$), converts to CIE L\*a\*b\*, and builds a 722-sample lookup table (`self.gradient_lab`, `self.temps`).
  - `VisionEngine.estimate_pixel(image_bgr, x, y)`: Maps single pixels to temperature and detects land masks.
  - `VisionEngine.analyze_roi(image_bgr, x, y, width, height)`: Vectorized region analysis computing mean, median, min, max, std dev ($\sigma$), ocean coverage %, and thermal zones.
  - `VisionEngine.pixel_to_geo()` & `roi_to_geo_bbox()`: Converts 1024×512 pixel coordinates to geographic latitude/longitude degrees.
  - `VisionEngine.fetch_mur_point(lat, lon, date_str, timeout)`: Convenience bridge to `erddap_client.fetch_mur_sst`.
- **[test_erddap.py](file:///C:/Users/User/Videos/EarthSonic-main/test_erddap.py):**  
  Automated test suite executing 7 comprehensive test scenarios: unit validation functions, offshore Durban point query (mocked), Durban land coordinate detection, invalid coordinates handling (HTTP 400), invalid dates rejection (HTTP 400), fill-value parsing, simulated timeouts / 503 errors (HTTP 504 / 502), and a real live network call to NOAA CoastWatch ERDDAP.
- **[test_milestone8.py](file:///C:/Users/User/Videos/EarthSonic-main/test_milestone8.py):**  
  Automated integration and regression suite executing 9 test scenarios: template DOM inspection, live offshore Durban ERDDAP request, Durban port land mask request, invalid coordinates handling, invalid dates handling, simulated upstream timeout/503 errors, OpenCV ROI/pixel regressions, file upload regression, and dashboard navigation regression.
- **[test_milestone9.py](file:///C:/Users/User/Videos/EarthSonic-main/test_milestone9.py):**  
  Automated sonification test suite executing 6 test scenarios: linear frequency mapping calculations, monotonicity and ordering across thermal spectrum, DOM audio controls and accessibility, JavaScript audio graph contracts, land/missing data safeguards, and live ERDDAP frequency calculation ($661.44\text{ Hz}$ for Durban).
- **[static/app.js](file:///C:/Users/User/Videos/EarthSonic-main/static/app.js):**  
  Client controller:
  - `initCanvas()`, `drawOverlay()`: Renders visualization onto canvas and draws ROI dashed box.
  - `requestRoiAnalysis()`, `requestPixelAnalysis()`: Asynchronous JSON fetch calls to Flask backend for OpenCV colormap estimates.
  - `syncCoordinatesFromCanvas()`: Translates canvas selection center/point to geographic coordinates and populates ERDDAP form inputs.
  - `requestMurNumericalData(lat, lon, date)`: Asynchronous JSON call to `/api/mur-sst` with client validation, loading state, and error handling.
  - `updateMurResults(data)`: Renders numerical SST, observation uncertainty, surface classification, and metadata into DOM.
  - `calculateMurFrequency(temp)`: Linear mapping converting numerical SST ($-5^\circ\text{C} \dots +35^\circ\text{C}$) to audio frequency ($160\text{ Hz} \dots 880\text{ Hz}$).
  - `startMurAudio()`, `stopMurAudio()`: Independent Web Audio sonification engine for authentic numerical MUR temperatures with safe ramped gain.
  - `initAudioContext()`, `updateSoundTone()`, `startAudio()`, `pauseAudio()`, `stopAudio()`: Dual-oscillator synthesizer for image-based spatial colormap estimates.
  - `announce()`: Pushes natural language status updates to `#accessibility-announcer` (`aria-live="polite"`).
- **[static/style.css](file:///C:/Users/User/Videos/EarthSonic-main/static/style.css):**  
  Custom CSS variables, high-contrast typography, responsive flex/grid layouts, dashed bounding box overlays, monochrome SVG icon styling, accessible focus rings, dedicated `.mur-numerical-card` styles, and `.mur-audio-panel` sonification layout.

---

## 5. Scientific Data and Processing

### 5.1 NASA SVS 5101 & JPL MUR Dataset
- **Visualization:** NASA Scientific Visualization Studio Entry [SVS 5101](https://svs.gsfc.nasa.gov/5101/) (*Sea Surface Temperature — Near Real Time*).
- **Underlying Dataset:** JPL MUR Sea Surface Temperature Analysis ([MUR-JPL-L4-GLOB-v4.1](https://podaac.jpl.nasa.gov/dataset/MUR-JPL-L4-GLOB-v4.1)).
- **Physical Parameter:** Foundation Sea Surface Temperature (SST).
- **Discipline Discipline:** **Sea Surface Temperature only.** It does **not** depict ocean currents, surface winds, atmospheric storms, precipitation, or weather forecasts.
- **Spatial Grid:** 0.01° $\times$ 0.01° ($\sim 1\text{ km}$) global grid, rendered as a 1024×512 equirectangular Plate Carrée map.
- **Calibrated Legend:** Published range spanning **-5.0°C to +35.0°C**.

### 5.2 Color Calibration in CIE L\*a\*b\* Color Space
In the initial prototype, temperature was estimated by projecting pixel RGB values onto a 3D line connecting two arbitrary endpoints. This produced massive errors because the NASA SVS 5101 colormap is non-linear and diverging:
- $-5^\circ\text{C}$ to $5^\circ\text{C}$: Deep navy blue $\to$ bright cyan.
- $10^\circ\text{C}$ to $15^\circ\text{C}$: Cyan $\to$ neutral pale off-white (global ocean transition zone).
- $20^\circ\text{C}$ to $35^\circ\text{C}$: Warm gold/orange $\to$ deep crimson red $\to$ dark maroon.

**The Solution:**  
OpenCV converts RGB/BGR images into the **CIE L\*a\*b\*** color space. In CIE L\*a\*b\*, Euclidean distance represents human perceptual color difference ($\Delta E$):

$$\Delta E = \sqrt{(L_1 - L_2)^2 + (a_1 - a_2)^2 + (b_1 - b_2)^2}$$

At server startup, `vision_engine.py` extracts 722 color steps along the horizontal gradient of `sst_mur_colorbar.png`. When evaluating an ocean pixel, the engine finds the entry that minimizes $\Delta E$ and retrieves the corresponding calibrated temperature.

### 5.3 Region of Interest (ROI) Vectorized Calculation
For an arbitrary region of $N$ pixels, evaluating each pixel individually in Python loops would be slow. EarthSonic uses vectorized matrix expansion in NumPy:

$$\|\mathbf{u} - \mathbf{v}\|^2 = \|\mathbf{u}\|^2 + \|\mathbf{v}\|^2 - 2(\mathbf{u} \cdot \mathbf{v})$$

Processing a 10,000-pixel bounding box takes **$\sim 44$ milliseconds**, producing:
- **Spatial Mean Temperature:** $\bar{T} = \frac{1}{N_{\text{ocean}}} \sum T_i$
- **Spatial Variance / Heterogeneity:** $\sigma = \sqrt{\frac{1}{N_{\text{ocean}}} \sum (T_i - \bar{T})^2}$
- **Extreme Range:** $T_{\min}$ and $T_{\max}$
- **Median Temperature:** $T_{\text{median}}$
- **Colormap Fit Quality:** Mean $\Delta E$ across the region (typically $\Delta E < 3.5$).

### 5.4 Land, Continent, and Polar Sea-Ice Detection
Continents and sea-ice in SVS 5101 are represented by neutral gray (`RGB 104,104,104`).
In CIE L\*a\*b\*, neutral gray has $a \approx 128, b \approx 128$, giving zero Chroma:

$$\text{Chroma} = \sqrt{(a - 128)^2 + (b - 128)^2}$$

- **Ocean Pixels:** High chroma ($\text{Chroma} \ge 8.5$).
- **Land / Mask Pixels:** Low chroma ($\text{Chroma} < 8.5$) or extreme luma ($L < 15$ or $L > 245$).
- **Filtering Logic:** Land pixels are excluded from ocean temperature averages. If a region has $<5\%$ ocean pixels, temperature calculation is suppressed to avoid continental land contamination, and a warning is issued.

### 5.5 Scientific Status: Image-Derived Estimate vs Numerical Sensor Data
> [!IMPORTANT]
> Any temperature displayed by EarthSonic is currently an **experimental visualization-based estimate** derived from colorbar gradient inversion. While calibrated via CIE L\*a\*b\*, lossy 8-bit JPEG/MP4 compression causes minor chroma quantization shifts. It must not be presented as certified radiometer measurements until verified against raw numerical MUR arrays.

### 5.6 MUR Numerical Data Validation via NOAA CoastWatch ERDDAP
- **Validation Status:** **PASS** (Empirically verified live on 2026-11-14).
- **Public Endpoint Verified:** `https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41` (REST/JSON format).
- **Authentication:** Zero authentication, token exchange, or API credentials required (unauthenticated public scientific data service).
- **Dimensions & Ordering:**
  - `time` (Double, `seconds since 1970-01-01T00:00:00Z`, daily reference at `09:00:00Z`).
  - `latitude` (Float, `degrees_north`, $-89.99^\circ \dots +89.99^\circ$, $0.01^\circ$ resolution).
  - `longitude` (Float, `degrees_east`, $-179.99^\circ \dots +180.00^\circ$, $0.01^\circ$ resolution).
  - Dimension constraint order: `[time][latitude][longitude]`.
- **Variables Verified:**
  1. `analysed_sst` (Double, units: `degree_C`): Foundation Sea Surface Temperature ($SST_{\text{fnd}}$) blended via Multi-Resolution Variational Analysis (MRVA). Native units on ERDDAP are degrees Celsius. Fill value: `-7.768000000000001` (parsed as `null`/`None` in JSON). Valid range: $-7.767^\circ\text{C} \dots 57.767^\circ\text{C}$.
  2. `analysis_error` (Double, units: `degree_C`): Estimated $1\sigma$ uncertainty standard deviation of the analysed SST. Fill value: `-327.68` (`null` in JSON). Valid range: $0.0^\circ\text{C} \dots 327.67^\circ\text{C}$.
  3. `mask` (Byte, unitless flag): Categorical sea/land/ice classification bitmask. Flag masks and meanings:
     - `1`: `open_sea`
     - `2`: `land`
     - `4`: `open_lake`
     - `8`: `open_sea_with_ice_in_the_grid`
     - `16`: `open_lake_with_ice_in_the_grid`
     Fill value: `-128`.
  4. `sea_ice_fraction` (Double, units: `1`, range $0.0 \dots 1.0$): Dimensionless sea-ice area fraction from EUMETSAT OSI-SAF. Fill value: `-1.28` (`null` in JSON).
- **Live Empirical Test Results (Durban Coastline, South Africa):**
  - **Verified Reference Timestamp:** `2026-11-13T09:00:00Z`
  - **Sample 1: Durban Harbor / City (Lat -29.85°, Lon +31.02°):**  
    `mask = 2` (`land`), `analysed_sst = null`, `analysis_error = null`. The dataset accurately recognized continental port land and withheld ocean temperature.
  - **Sample 2: Durban Offshore Indian Ocean (3×3 Grid, Lat -29.86°..-29.84°, Lon +31.06°..+31.08°):**  
    `mask = 1` (`open_sea`), `analysed_sst = 22.833°C .. 22.879°C`, `analysis_error = 0.4°C`, `sea_ice_fraction = null`. Payload: 9 rows, $\approx 1.2\text{ KB}$, sub-second response.
  - **Sample 3: Coastline Transect (Lat -29.85° across Lon +31.00° to +31.06°):**
    - $+31.00^\circ\text{E} \dots +31.03^\circ\text{E}$: `mask = 2` (Land), `SST = None (Masked)`
    - $+31.04^\circ\text{E}$: `mask = 1` (Open Ocean), `SST = 22.868 °C (±0.4 °C)`
    - $+31.05^\circ\text{E}$: `mask = 1` (Open Ocean), `SST = 22.863 °C (±0.4 °C)`
    - $+31.06^\circ\text{E}$: `mask = 1` (Open Ocean), `SST = 22.858 °C (±0.4 °C)`
- **Scientific Interpretation:**
  - `analysed_sst` is an analyzed Level-4 (L4) product, not a single raw instrument reading. It combines infrared (MODIS, AVHRR), microwave (AMSR2), and in-situ buoys via variational interpolation, removing cloud gaps while providing a continuous foundation temperature.
  - `analysis_error` provides ground-truth observation uncertainty ($\pm 0.4^\circ\text{C}$ in clear coastal waters) that EarthSonic can sonify as an auditory confidence dimension.
- **Integration Feasibility:** Confirmed feasible, high-speed ($\approx 1.2\text{ KB}$ JSON payload, sub-second latency), and fully compatible with EarthSonic's existing coordinate mapping.

### 5.7 Live MUR Numerical Data Integration via Flask (`/api/mur-sst`)
Implemented in Milestone 7 via [erddap_client.py](file:///C:/Users/User/Videos/EarthSonic-main/erddap_client.py) and registered as route `GET, POST /api/mur-sst` in [app.py](file:///C:/Users/User/Videos/EarthSonic-main/app.py):

#### 1. Input Validation Architecture
- **Coordinate Validation (`validate_coordinates`):**
  - Confirms latitude is numeric and within $[-90.0^\circ, +90.0^\circ]$; clamped to MUR grid bounds $[-89.99^\circ, +89.99^\circ]$ and rounded to $0.01^\circ$.
  - Confirms longitude is numeric and within $[-180.0^\circ, +180.0^\circ]$; clamped to $[-179.99^\circ, +180.00^\circ]$ and rounded to $0.01^\circ$.
  - Returns `(False, ..., error_message)` if missing, non-numeric, or out of range, mapped to HTTP 400 `ValidationError`.
- **Date Validation (`validate_date`):**
  - Accepts `YYYY-MM-DD` or ISO timestamp `YYYY-MM-DDTHH:MM:SSZ`. Defaults to `2026-11-13` if omitted.
  - Validates calendar dates using `datetime.strptime` (rejects invalid dates like `2026-02-30`).
  - Enforces dataset commencement limit: dates before `2002-06-01` are rejected with HTTP 400.
  - Normalizes timestamps to the standard MUR daily index `YYYY-MM-DDT09:00:00Z`.

#### 2. Upstream Network & Timeout Architecture
- Constructs single-grid-cell queries for `analysed_sst`, `analysis_error`, and `mask`:
  ```text
  https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41.json?analysed_sst[(timestamp)][(lat):1:(lat)][(lon):1:(lon)],analysis_error[...],mask[...]
  ```
- **Timeout:** Enforces a strict 8.0-second HTTP timeout using standard library `urllib.request`.
- **Error Handling:**
  - `TimeoutError` / `URLError`: Mapped to HTTP 504 Gateway Timeout.
  - Upstream ERDDAP 500 / 503 errors: Mapped to HTTP 502 Bad Gateway, parsing and preserving ERDDAP's internal error explanation.
  - JSON parse errors / empty tables: Handled safely with descriptive error payloads.

#### 3. Data Interpretation & Mask Filtering
- **Celsius Consistency:** ERDDAP serves `analysed_sst` natively in Celsius; no temperature offset is subtracted.
- **Fill Values:** Negative fill values (`-7.768` for SST, `-327.68` for error, `-128` for mask) are automatically parsed as `null` / `None`.
- **Categorical Masks:** Decodes mask integers into descriptive metadata:
  - `1`: `open_sea` (`is_ocean: True`)
  - `2`: `land` (`is_ocean: False`, sets continental warning, suppresses SST)
  - `4`: `open_lake` (`is_ocean: False`)
  - `8`: `open_sea_with_ice` (`is_ocean: False`)
  - `16`: `open_lake_with_ice` (`is_ocean: False`)
- **Scientific Attribution:** Every response includes `product_type: "Level-4 (L4) Blended Foundation SST Analysis (Analyzed gridded product, not a single sensor measurement)"` to prevent misrepresentation as raw satellite radiometer observations.

#### 4. Automated & Live Verification Results
Verified via automated test suite [test_erddap.py](file:///C:/Users/User/Videos/EarthSonic-main/test_erddap.py):
1. **Unit Validation Functions:** Coordinate clamping, string conversion, and date checks passed.
2. **Offshore Durban (Mocked):** Verified `GET` and `POST` return HTTP 200, SST `22.858°C`, error `0.400°C`, `is_ocean: True`.
3. **Land Coordinate (Mocked):** Verified Durban Harbor coordinates return `mask: 2` (`land`), `is_ocean: False`, SST `null`, and land warning.
4. **Invalid Coordinates:** Out-of-range and non-numeric coordinates return HTTP 400 `ValidationError`.
5. **Invalid Dates:** Format errors and dates before 2002 return HTTP 400 `ValidationError`.
6. **Fill Value Handling:** Missing and fill values cleanly parse to `null` without throwing exceptions.
7. **Simulated Upstream Errors:** Timeouts return HTTP 504; ERDDAP 503/500 returns HTTP 502 with upstream message.
8. **Real Live Network Request:** Live HTTP query to NOAA CoastWatch ERDDAP for Durban waters ($-29.85^\circ\text{S}, +31.06^\circ\text{E}$) returned HTTP 200, SST **$22.858^\circ\text{C}$** ($\pm 0.40^\circ\text{C}$).

### 5.8 Frontend Numerical MUR Data Integration (Milestone 8)
Implemented in Milestone 8 via [templates/ocean_temperature.html](file:///C:/Users/User/Videos/EarthSonic-main/templates/ocean_temperature.html), [static/app.js](file:///C:/Users/User/Videos/EarthSonic-main/static/app.js), and [static/style.css](file:///C:/Users/User/Videos/EarthSonic-main/static/style.css):

#### 1. Dual-Product Workspace Architecture
The Sea Surface Temperature workspace now renders two distinct, clearly labeled scientific data products side-by-side in the controls panel:
- **Product 1 (Colormap Temperature Analysis):**  
  Derived from local OpenCV CIE L\*a\*b\* nearest-gradient inversion of the NASA SVS 5101 visualization graphic. Provides interactive spatial statistics (mean, min, max, std dev, 5-zone thermal distribution) across user-dragged Regions of Interest (ROI).
- **Product 2 (Authentic Numerical MUR Data):**  
  Retrieved asynchronously via `POST /api/mur-sst` from NOAA CoastWatch ERDDAP (`jplMURSST41`). Provides genuine gridded foundation SST, formal $1\sigma$ observation uncertainty, dataset timestamp, and surface mask classifications directly from the Jet Propulsion Laboratory Level-4 analysis.

#### 2. Scientific Comparison & Integrity Policy
- **Independent Presentation:** The two products are displayed in separate panels with distinct headings, descriptions, and provenance footers.
- **Suppression of Synthetic $\Delta T$:** EarthSonic intentionally refrains from computing an automated difference ($\Delta T$) between the visualization estimate and the numerical MUR data. The NASA SVS 5101 static print graphic represents an unspecified composite frame, whereas the ERDDAP query represents a precise daily 0.01° grid analysis on a specific calendar date. Because their temporal frames and spatial sampling differ, presenting a mathematical delta would be scientifically invalid and misleading.
- **Zero Invented Confidence Metrics:** Only authentic scientific uncertainty ($1\sigma$ analysis error from ERDDAP, $\Delta E$ color distance from OpenCV) is displayed.

#### 3. Interaction & Dynamic Synchronization
- **Accessible Form Controls:** Users can manually input latitude ($-89.99^\circ \dots 89.99^\circ$), longitude ($-179.99^\circ \dots 180.00^\circ$), and observation date ($\ge 2002-06-01$).
- **Canvas Synchronization (`syncCoordinatesFromCanvas`):** Clicking "Use Map Selection", dragging a bounding box, sampling a single pixel, or clicking any preset region automatically translates the canvas coordinates into geographic degrees and updates the ERDDAP form inputs.
- **Asynchronous State Machine:**
  - *Loading State (`#mur-loading`):* Displays a high-contrast CSS spinner and status text while ERDDAP is queried.
  - *Success State (`#mur-results`):* Displays the primary temperature in Celsius, classification pill, observation uncertainty ($\pm 0.40^\circ\text{C}$), dataset timestamp, and surface classification. If land is queried (`mask = 2`), ocean temperature is suppressed and a land warning is displayed.
  - *Error State (`#mur-error`):* Displays human-readable service notices if coordinates are out of bounds, dates are invalid, or ERDDAP is temporarily unreachable.
  - *Accessibility Announcements:* Screen-reader announcements are dispatched to `#accessibility-announcer` (`aria-live="polite"`).

#### 4. Automated Verification Results
Verified via automated test suite [test_milestone8.py](file:///C:/Users/User/Videos/EarthSonic-main/test_milestone8.py):
1. **Template Inspection:** Verified DOM elements for Product 1 and Product 2, form inputs, labels, and zero emojis $\to$ **`PASSED`**.
2. **Live Offshore Durban Request:** Real ERDDAP HTTP 200 returning $22.858^\circ\text{C}$ ($\pm 0.40^\circ\text{C}$) $\to$ **`PASSED`**.
3. **Land Coordinate Masking:** Durban Harbor coordinates returned `mask = 2`, SST `null`, and land warning $\to$ **`PASSED`**.
4. **Invalid Coordinates:** Out-of-range and non-numeric coordinates returned HTTP 400 $\to$ **`PASSED`**.
5. **Invalid Dates:** Pre-2002 dates and calendar errors returned HTTP 400 $\to$ **`PASSED`**.
6. **Network Failure Simulation:** Timeouts returned HTTP 504; ERDDAP 503 returned HTTP 502 with message $\to$ **`PASSED`**.
7. **OpenCV Image Analysis Regression:** ROI analysis ($28.89^\circ\text{C}$) and pixel sampling ($23.0^\circ\text{C}$) confirmed operational $\to$ **`PASSED`**.
8. **Upload Workflow Regression:** User image/video upload confirmed operational $\to$ **`PASSED`**.
9. **Dashboard Navigation Regression:** All module links and return navigation confirmed operational $\to$ **`PASSED`**.

---

## 6. Sonification

Sonification is the translation of data into non-speech audio. In EarthSonic, sound parameters communicate specific physical and statistical properties rather than functioning as ambient background music.

```
SCIENTIFIC DATA PROPERTY                  WEB AUDIO SYNTHESIZER
Mean Ocean Temperature (-5°C to 35°C) ---> Master Oscillator Pitch (160 Hz to 880 Hz)
Thermal Variance / StdDev (0°C to 6°C) -> LFO Tremolo Pulse Rate (0.5 Hz to 6.0 Hz)
Continental Land / Polar Ice Mask ------> Low Muted Alert Tone (110 Hz Sine Wave)
```

### 6.1 Audio Engine Architecture
Implemented in [static/app.js](file:///C:/Users/User/Videos/EarthSonic-main/static/app.js) via the Web Audio API:
- **Master Oscillator (`masterOsc`):** Generates a smooth `sine` wave tone.
- **Low-Frequency Oscillator (`lfoOsc`):** Generates a sub-audible sine wave controlling tremolo/pulse amplitude modulation.
- **Gain Nodes (`masterGain`, `lfoGain`):** Regulates volume and modulation depth.
- **Audio Routing:** `lfoOsc -> lfoGain -> masterGain.gain` (amplitude modulation), `masterOsc -> masterGain -> audioCtx.destination`.

### 6.2 Data-to-Sound Mapping Parameters
1. **Pitch (Frequency):**
   - Scaled from $-5^\circ\text{C}$ to $+35^\circ\text{C}$ across 160 Hz (Deep Bass D#3) to 880 Hz (Treble A5):
     $$f = 160 + \left(\frac{T - (-5.0)}{40.0}\right) \times 720 \text{ Hz}$$
   - Smoothed via exponential ramp: `setTargetAtTime(targetFreq, audioCtx.currentTime, 0.08)`.
2. **Thermal Variance (LFO Tremolo Texture):**
   - Regions with uniform temperature ($\sigma \approx 0^\circ\text{C}$) produce a pure, steady tone.
   - Regions with strong thermal gradients or mixing zones ($\sigma > 2^\circ\text{C}$) produce an audible pulsing tremolo ($0.5\text{–}6.0\text{ Hz}$), conveying spatial thermal variance to blind users.
3. **Land / Mask Alert:**
   - When land is selected, the audio shifts to a low, non-alarming 110 Hz tone with slow pulse, signaling that ocean temperature cannot be sampled.

### 6.3 Authentic Numerical MUR Sonification (Milestone 9)
Implemented in Milestone 9 via [static/app.js](file:///C:/Users/User/Videos/EarthSonic-main/static/app.js) (`calculateMurFrequency`, `startMurAudio`, `stopMurAudio`) and dedicated UI controls in [templates/ocean_temperature.html](file:///C:/Users/User/Videos/EarthSonic-main/templates/ocean_temperature.html):

#### 1. Linear Temperature-to-Frequency Relationship
The numerical sonification engine translates authentic gridded Sea Surface Temperature observations ($T$ in °C) directly into acoustic pitch ($f$ in Hz) using a continuous, strictly monotonic linear function:

$$f = f_{\min} + \left(\frac{T - T_{\min}}{T_{\max} - T_{\min}}\right) \times (f_{\max} - f_{\min})$$

Where:
- $T_{\min} = -5.0^\circ\text{C}$
- $T_{\max} = +35.0^\circ\text{C}$
- $f_{\min} = 160.0\text{ Hz}$
- $f_{\max} = 880.0\text{ Hz}$

Substituting the constants gives the operational relationship:

$$f = 160.0 + \left(\frac{T - (-5.0)}{35.0 - (-5.0)}\right) \times (880.0 - 160.0) = 160.0 + \left(\frac{T + 5.0}{40.0}\right) \times 720.0$$

#### 2. Range Justification & Acoustic Sensitivity
- **Thermal Physical Range ($-5.0^\circ\text{C} \dots +35.0^\circ\text{C}$):** Matches the published GHRSST Level-4 MUR dataset bounds and the NASA SVS 5101 colormap. While typical seawater freezes at $\approx -1.8^\circ\text{C}$, the $-5.0^\circ\text{C}$ lower bound accommodates polar sea-ice margins and sub-zero surface anomalies, while $+35.0^\circ\text{C}$ represents Earth's warmest tropical warm pools (e.g., Persian Gulf, Western Pacific).
- **Acoustic Frequency Limits ($160.0\text{ Hz} \dots 880.0\text{ Hz}$):** The lower bound of $160\text{ Hz}$ (musical pitch D#3) produces a warm, audible bass tone that reproduces reliably on laptop and mobile device speakers without requiring external subwoofers. The upper bound of $880\text{ Hz}$ (musical pitch A5) provides clear, brilliant treble perception without reaching piercing or listener-fatiguing frequencies ($>2000\text{ Hz}$).
- **Linear Pitch Sensitivity:** The total frequency span of $720.0\text{ Hz}$ across a $40.0^\circ\text{C}$ thermal span yields a consistent rate of change:
  $$\frac{\Delta f}{\Delta T} = \frac{720.0\text{ Hz}}{40.0^\circ\text{C}} = 18.0\text{ Hz per }^\circ\text{C}$$
  Because human frequency discrimination ($\text{JND}$) in this register is approximately $1\text{–}3\text{ Hz}$, listeners can discern fractions of a degree Celsius without cognitive overload.
- **Boundary Clamping:** Input values outside $[-5.0^\circ\text{C}, +35.0^\circ\text{C}]$ are clamped safely prior to frequency calculation:
  $$T_{\text{clamped}} = \max(-5.0, \min(35.0, T))$$

#### 3. Representative Thermal-to-Acoustic Mappings
| Sea Surface Temperature ($T$) | Frequency ($f$) | Musical Pitch Equivalent | Oceanographic Context |
| :---: | :---: | :---: | :--- |
| **$-5.00^\circ\text{C}$** | **$160.00\text{ Hz}$** | D#3 / Eb3 | Polar freezing anomaly / lower scale boundary |
| **$0.00^\circ\text{C}$** | **$250.00\text{ Hz}$** | B3 | Seawater freezing transition zone |
| **$2.50^\circ\text{C}$** | **$295.00\text{ Hz}$** | D4 | Subpolar polar waters |
| **$10.00^\circ\text{C}$** | **$430.00\text{ Hz}$** | A4 | Cold temperate open ocean |
| **$15.00^\circ\text{C}$** | **$520.00\text{ Hz}$** | C5 | Temperate transition water |
| **$20.00^\circ\text{C}$** | **$610.00\text{ Hz}$** | D5 | Subtropical ocean basin |
| **$22.86^\circ\text{C}$** | **$661.44\text{ Hz}$** | E5 | Durban offshore waters (Verified empirical sample) |
| **$30.00^\circ\text{C}$** | **$790.00\text{ Hz}$** | G5 | Equatorial warm pool |
| **$35.00^\circ\text{C}$** | **$880.00\text{ Hz}$** | A5 | Extreme tropical SST / upper scale boundary |

#### 4. Web Audio Routing & Conflict Prevention
- **Isolated Node Graph:** Operates via a dedicated sine oscillator (`murOsc`) and gain envelope (`murGain`) routing to `audioCtx.destination`.
- **Decoupled Playback:** The image-based spatial synthesizer (with LFO tremolo) and the numerical point synthesizer (pure pitch) are strictly independent. Triggering one immediately silences the other to eliminate acoustic interference.
- **Explicit User Activation:** Audio playback is strictly user-initiated via `#btn-play-mur`. Data loading NEVER automatically triggers sound.
- **Safeguards for Land & Missing Data:** Non-ocean surfaces (`mask = 2` land, `mask = 4` lake, missing data) disable the audio playback controls and update status text to explain that sonification is suppressed over continental terrain.
- **Scientific Caveat:** In accordance with scientific integrity guidelines, ERDDAP's formal $1\sigma$ `analysis_error` is reported as statistical variational uncertainty, not guaranteed sensor accuracy, and is not used to modulate timbre in this milestone.

### 6.4 Future Sonification Research
- **Polyphony / Harmonic Chords:** Representing $T_{\min}$ and $T_{\max}$ as lower and upper intervals in a harmonic triad.
- **Multi-Track Timbre Layers:** Mapping wind vectors or ocean currents to filtered white noise or stereo panning.
- **Temporal Rhythm:** Accelerating beat frequency during video playback when the rate of change ($dT/dt$) increases.

---

## 7. Accessibility

### 7.1 Existing Accessibility Implementations
- **Screen-Reader ARIA Live Region:** An element (`#accessibility-announcer`) with `aria-live="polite"` and `aria-atomic="true"` announces state changes in natural language (e.g. *"Selected Equatorial Pacific. Region mean temperature is 28.89 degrees Celsius. Tropical Warm Waters. Ocean coverage 98.4 percent."*).
- **Keyboard Shortcuts:**
  - `Space`: Toggles Play / Pause for the sonification engine.
  - `Key S`: Stops audio and resets pitch.
- **Skip Links:** Top of page includes `<a href="#main-workspace" class="skip-link">` allowing screen-reader users to bypass top navigation.
- **High-Contrast Focus Indicators:** All interactive elements feature prominent `outline: 2px solid #38bdf8` focus rings.
- **Monochrome Vector Graphics:** Zero emojis; all iconography consists of scalable, high-contrast, monochrome SVGs with `aria-hidden="true"`.
- **Accessible Bounding Box Presets:** Users who cannot drag a mouse can click named regional buttons to trigger comprehensive ROI analysis.

### 7.2 Remaining Accessibility Work
- Native Web Speech API synthetic voice readouts.
- Braille-display tactile layout optimizations.
- Formal WCAG 2.2 AAA accessibility audit.

---

## 8. Completed Development Milestones

```
+-------------------------------------------------------------------------------------------------+
|                                 EARTHSONIC PROGRESSION TIMELINE                                 |
+-------------------------------------------------------------------------------------------------+
| Milestone 0 (Initial Prototype):                                                                |
| - Flask upload handler + single-pixel canvas click.                                             |
| - Naive 2-point linear RGB interpolation (mathematically invalid for non-linear legends).      |
|                                                                                                 |
| Milestone 1 (Environment & OpenCV Integration):                                                 |
| - Established isolated Python 3.14 virtual environment (.venv).                                 |
| - Installed precompiled opencv-python==5.0.0.93 and numpy==2.5.4 wheels.                        |
|                                                                                                 |
| Milestone 2 (NASA SVS 5101 Legend Calibration):                                                 |
| - Extracted continuous 722-point gradient from sst_mur_colorbar.png (-5°C to +35°C).           |
| - Replaced RGB projection with perceptual CIE L*a*b* Euclidean distance matching (Delta E).    |
|                                                                                                 |
| Milestone 3 (Region of Interest & Statistical Analysis):                                        |
| - Created modular vision_engine.py with vectorized ROI distance matrix computation.             |
| - Implemented automated land/sea-ice masking (Chroma < 8.5).                                   |
| - REST API endpoints: /api/analyze-region, /api/sample-pixel, /api/dataset-info.                |
|                                                                                                 |
| Milestone 4 (Accessible Dual-Parameter Sonification):                                           |
| - Dual-oscillator Web Audio engine: Pitch = Mean Temp, LFO Pulse = Spatial Variance (StdDev).   |
| - ARIA live screen-reader announcements and keyboard controls.                                  |
|                                                                                                 |
| Milestone 5 (Modular Landing Dashboard):                                                        |
| - Created landing page (/) presenting 4 scientific exploration module cards.                   |
| - Dedicated Ocean Temperature workspace (/ocean-temperature) with return navigation.            |
|                                                                                                 |
| Milestone 6 (Minimalist Scientific Refinement):                                                 |
| - Removed all decorative emojis across landing page and module cards.                           |
| - Introduced clean, monochrome SVG vector iconography.                                         |
|                                                                                                 |
| Milestone 7 (Live MUR ERDDAP Numerical Integration):                                            |
| - Created erddap_client.py connecting to NOAA CoastWatch ERDDAP (jplMURSST41).                 |
| - Implemented dedicated REST endpoint GET, POST /api/mur-sst.                                  |
| - Added rigorous coordinate & date validation, categorical mask decoding, and fill values.     |
| - Automated test suite test_erddap.py verified 7 test cases + live network query (22.858°C).   |
|                                                                                                 |
| Milestone 8 (Frontend Numerical MUR Data Integration):                                          |
| - Integrated /api/mur-sst into Ocean Temperature dashboard (ocean_temperature.html, app.js).    |
| - Created dual-product presentation: Product 1 (Colormap Estimate) and Product 2 (MUR Data).    |
| - Dynamic canvas coordinate synchronization (Use Map Selection button, mouseup, presets).       |
| - Rigorous scientific separation: no artificial ΔT calculation across disparate temporal frames. |
| - Automated test suite test_milestone8.py passed all 9 test scenarios cleanly.                   |
|                                                                                                 |
| Milestone 9 (First Numerical Data Sonification):                                                |
| - Linear temperature-to-frequency mapping: f = 160 + ((T - (-5)) / 40) * 720 Hz (18 Hz/°C).    |
| - Dedicated MUR audio controls: #btn-play-mur, #btn-stop-mur, #mur-audio-pill, #mur-audio-desc. |
| - Web Audio routing with independent sine oscillator and exponential gain envelopes.            |
| - Strict conflict prevention between image and numerical audio engines.                         |
| - Automated test suite test_milestone9.py verified 6 test scenarios cleanly.                   |
+-------------------------------------------------------------------------------------------------+
```

---

## 9. Known Limitations and Outstanding Work

1. **Usability Testing Required for Comprehension Claims:**  
   While the linear mapping from $-5.0^\circ\text{C}$ to $+35.0^\circ\text{C}$ across $160\text{–}880\text{ Hz}$ ($18.0\text{ Hz/}^\circ\text{C}$) is mathematically continuous, monotonic, and acoustically validated in automated testing, empirical comprehension and interpretability claims must not be asserted without formal multi-sensory usability trials involving blind and low-vision users.
2. **Multi-Parameter Acoustic Uncertainty Modulation Pending:**  
   The formal $1\sigma$ observational uncertainty (`analysis_error_c`) is currently reported as structured text and not yet routed into harmonic dissonance, detuning, or overtone textures.
3. **JPEG Compression Chroma Noise:**  
   In lossy JPEG images, edge ringing can cause a handful of rogue pixels near coastlines to exhibit chroma deviations.
4. **Single Active Scientific Module:**  
   Ocean Temperature is fully functional; *Ocean Currents* and *Weather & Atmosphere* cards are currently placeholders badged as *Coming Soon*.

---

## 10. Next Development Milestone

### Recommended Next Milestone: **Milestone 10 — Multi-Sensory Usability Testing & Audio Parameter Refinement**
- **Objective:** Design an interactive evaluation protocol and refine multi-sensory feedback across both sonification modes.
- **Mechanism:**
  - Introduce synthetic voice readout option for frequency and temperature values.
  - Explore mapping `analysis_error_c` to an acoustic confidence overtone or harmonic clarity dimension.
  - Validate keyboard navigation flows and screen-reader status announcements across assistive technology screen readers (NVDA, JAWS, VoiceOver).

---

## 11. Development Changelog

### Commit `117ceab` — 2026-11-14
- **Purpose:** Baseline project commit before technical advancement.
- **Files Affected:** `app.py`, `static/app.js`, `static/style.css`, `templates/index.html`, `requirements.txt`, `README.txt`, `.gitignore`.
- **Verification:** Prototype ran on Python 3.14 / Flask 3.0.0; confirmed single-pixel upload functionality.

### Commit `7264fe4` — 2026-11-14
- **Purpose:** NASA SVS 5101 SST integration, OpenCV CIE L\*a\*b\* calibration, ROI analysis, and accessible UI.
- **Files Affected:** `vision_engine.py`, `static/nasa/colorbar_cropped.png`, `app.py`, `templates/index.html`, `static/style.css`, `static/app.js`, `requirements.txt`.
- **Verification:** Automated unit test confirmed 10,000-pixel ROI processed in 44 ms; land masking excluded Sahara with warning; Web Audio dual-oscillator modulated pitch and pulse cleanly.

### Commit `5b3f9f5` — 2026-11-14
- **Purpose:** Modular landing dashboard with scientific exploration module cards and dedicated SST workspace.
- **Files Affected:** `templates/landing.html`, `templates/ocean_temperature.html`, `templates/index.html`, `app.py`, `static/style.css`, `test_modular.py`.
- **Verification:** `test_modular.py` passed all 6 test cases: landing page HTTP 200, 3 Coming Soon cards cleanly disabled with zero broken links, return navigation verified, API endpoints verified.

### Commit `c7fd4d9` — 2026-11-14
- **Purpose:** Interface refinement removing all emojis from landing page and module cards; replaced with monochrome SVG vector icons.
- **Files Affected:** `templates/landing.html`, `static/style.css`.
- **Verification:** Regex scan across codebase confirmed zero emojis remain; live server test confirmed SVG icons render cleanly with HTTP 200.

### Commit `a7c400f` — 2026-11-14
- **Purpose:** Document empirical validation of the NASA/JPL MUR numerical dataset via NOAA CoastWatch ERDDAP (`jplMURSST41`).
- **Files Affected:** `PROJECT_CONTEXT.md` (documentation-only change; zero application code modified).
- **Verification:** Live HTTP queries to `jplMURSST41.json` confirmed metadata, land mask filtering (`mask=2`), open ocean temperatures (`22.86°C`), and observation error bounds ($\pm 0.4^\circ\text{C}$).

### Commit `2e6210c` — 2026-11-14
- **Purpose:** Live MUR numerical data integration via NOAA CoastWatch ERDDAP (`jplMURSST41`).
- **Files Affected:** `erddap_client.py` (new), `app.py`, `vision_engine.py`, `test_erddap.py` (new), `PROJECT_CONTEXT.md`.
- **Verification:** Comprehensive test suite `test_erddap.py` passed 7 test scenarios (validation, offshore Durban, Durban land mask, invalid coords, invalid dates, fill values, simulated timeouts/503s); live ERDDAP network query verified with HTTP 200 ($22.858^\circ\text{C} \pm 0.4^\circ\text{C}$). Existing test suite `test_modular.py` confirmed 100% backward compatibility.

### Commit `d4382b7` — 2026-11-14
- **Purpose:** Frontend numerical MUR data integration in Ocean Temperature workspace (Milestone 8).
- **Files Affected:** `templates/ocean_temperature.html`, `static/app.js`, `static/style.css`, `test_milestone8.py` (new), `PROJECT_CONTEXT.md`.
- **Verification:** Comprehensive test suite `test_milestone8.py` passed 9 test scenarios (DOM inspection, zero emojis, live offshore Durban ERDDAP request, Durban port land mask, invalid coordinates, invalid dates, network timeout/503 handling, OpenCV ROI/pixel regressions, upload workflow regression, and dashboard navigation regression). All existing test suites `test_erddap.py` and `test_modular.py` confirmed 100% pass.

### Commit `feat-mur-sonification` — 2026-11-14
- **Purpose:** First numerical data sonification mode using authentic MUR SST via Web Audio API (Milestone 9).
- **Files Affected:** `templates/ocean_temperature.html`, `static/app.js`, `static/style.css`, `test_milestone9.py` (new), `PROJECT_CONTEXT.md`.
- **Verification:** Comprehensive test suite `test_milestone9.py` passed 6 test scenarios (mathematical linear mapping, monotonicity/ordering, DOM audio controls, JavaScript audio graph contracts, land/missing data safeguards, and live ERDDAP Durban frequency calculation of $661.44\text{ Hz}$). All regression suites `test_milestone8.py`, `test_erddap.py`, and `test_modular.py` confirmed 100% pass.
