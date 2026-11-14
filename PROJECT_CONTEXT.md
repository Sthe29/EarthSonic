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
├── app.py                              # Flask application controller & API routes (143 lines)
├── vision_engine.py                    # Modular OpenCV computer vision & calibration engine (274 lines)
├── requirements.txt                    # Project dependency manifest (Flask, opencv-python, numpy)
├── README.txt                          # Legacy developer notes from original prototype
├── test_modular.py                     # Automated integration test suite (6 test cases)
├── PROJECT_CONTEXT.md                  # This permanent project technical memory document
├── static/
│   ├── app.js                          # Client canvas interaction, API client, Web Audio engine (442 lines)
│   ├── style.css                       # Modern dark scientific dashboard & landing styles (1,257 lines)
│   └── nasa/
│       ├── sst_mur_print.jpg           # NASA SVS 5101 Equirectangular SST map (1024×512, JPEG)
│       ├── sst_mur_colorbar.png        # NASA master colorbar graphic (3840×2160, RGBA, 16-bit)
│       └── colorbar_cropped.png        # Cropped legend graphic displayed in the UI (3360×750, PNG)
├── templates/
│   ├── landing.html                    # Modular landing dashboard with 4 scientific exploration cards
│   ├── ocean_temperature.html          # Dedicated Ocean Temperature workspace
│   └── index.html                      # Backward-compatible template (includes ocean_temperature.html)
└── uploads/                            # Server directory storing user-uploaded media files
```

### Detailed File Responsibilities
- **[app.py](file:///C:/Users/User/Videos/EarthSonic-main/app.py):**  
  Entry point for Flask. Manages configuration, routes `/` and `/ocean-temperature`, upload file size limits (250 MB), static file serving from `uploads/`, and dispatches requests to `vision_engine`.
- **[vision_engine.py](file:///C:/Users/User/Videos/EarthSonic-main/vision_engine.py):**  
  Core computer vision module:
  - `VisionEngine._init_calibration()`: Reads `sst_mur_colorbar.png`, samples the horizontal gradient from $X=480$ ($-5^\circ\text{C}$) to $X=3365$ ($+35^\circ\text{C}$), converts to CIE L\*a\*b\*, and builds a 722-sample lookup table (`self.gradient_lab`, `self.temps`).
  - `VisionEngine.estimate_pixel(image_bgr, x, y)`: Maps single pixels to temperature and detects land masks.
  - `VisionEngine.analyze_roi(image_bgr, x, y, width, height)`: Vectorized region analysis computing mean, median, min, max, std dev ($\sigma$), ocean coverage %, and thermal zones.
  - `VisionEngine.pixel_to_geo()` & `roi_to_geo_bbox()`: Converts 1024×512 pixel coordinates to geographic latitude/longitude degrees.
- **[static/app.js](file:///C:/Users/User/Videos/EarthSonic-main/static/app.js):**  
  Client controller:
  - `initCanvas()`, `drawOverlay()`: Renders visualization onto canvas and draws ROI dashed box.
  - `requestRoiAnalysis()`, `requestPixelAnalysis()`: Asynchronous JSON fetch calls to Flask backend.
  - `updateDashboardWithRoi()`, `updateDashboardWithPixel()`: Updates DOM elements and thermal zone bars.
  - `initAudioContext()`, `updateSoundTone()`, `startAudio()`, `pauseAudio()`, `stopAudio()`: Web Audio API sound synthesis.
  - `announce()`: Pushes natural language status updates to `#accessibility-announcer` (`aria-live="polite"`).
- **[static/style.css](file:///C:/Users/User/Videos/EarthSonic-main/static/style.css):**  
  Custom CSS variables, high-contrast typography, responsive flex/grid layouts, dashed bounding box overlays, monochrome SVG icon styling, and accessible focus rings.

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

### 6.3 Future Sonification Research
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
+-------------------------------------------------------------------------------------------------+
```

---

## 9. Known Limitations and Outstanding Work

1. **No Direct Numerical Connection Yet:**  
   Currently, temperatures are derived from colorbar matching against `sst_mur_print.jpg`. They must be validated against the true 32-bit floating-point MUR NetCDF arrays.
2. **JPEG Compression Chroma Noise:**  
   In lossy JPEG images, edge ringing can cause a handful of rogue pixels near coastlines to exhibit chroma deviations.
3. **Single Active Scientific Module:**  
   Ocean Temperature is fully functional; *Ocean Currents* and *Weather & Atmosphere* cards are currently placeholders badged as *Coming Soon*.
4. **No Natural Language Voice Interaction Yet:**  
   User interaction is keyboard and mouse-driven; speech-command input has not yet been integrated.

---

## 10. Next Development Milestone

### Recommended Next Milestone: **Milestone 7 — NOAA ERDDAP Live Numerical Data Integration**
- **Objective:** Connect `vision_engine.py` to the public, unauthenticated NOAA CoastWatch ERDDAP mirror for JPL MUR SST (`jplMURSST41`).
- **Mechanism:** When a user selects a bounding box, the backend translates the pixel box into geographic coordinates `(lat_min, lat_max, lon_min, lon_max)` and requests a small NetCDF/CSV regional slice from ERDDAP:
  ```text
  https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41.nc?analysed_sst[(recent)][(lat_min):1:(lat_max)][(lon_min):1:(lon_max)]
  ```
- **Outcome:** The UI will display the **Visualization Colormap Estimate** and the **Authentic MUR Sensor Measurement** side-by-side, providing full scientific validation.

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
