# EarthSound Dashboard — first local prototype

## What this version does
- Provides a browser interface for uploading an image or video.
- Displays the uploaded media inside the dashboard.
- Lets you sample the low and high colours from a visible temperature legend.
- Lets you select one pixel/location on the map.
- Estimates a temperature from a **two-endpoint linear RGB calibration**.
- For video, updates the selected pixel estimate as the video plays.
- Generates a simple tone whose pitch rises with the estimated temperature.

## Important scientific limitation
This prototype does **not** discover Celsius values automatically. The user must enter the low and high temperatures printed on the visualization legend and sample the corresponding endpoint colours.

The current two-endpoint RGB interpolation is only an approximation for a simple, monotonic colour scale. It is not reliable for rainbow legends, multi-stop palettes, non-linear scales, overlays, labels, coastlines, or compression artefacts. Do not treat its output as authoritative scientific data. The next improvement should be multi-point legend calibration and region/map alignment.

The current selected point is a fixed pixel coordinate in the uploaded frame. It does not yet identify a named city or correct for map projection/geographic coordinates.

## Setup on Windows PowerShell
1. Extract this ZIP into your existing `OpenCv_projects` folder.
2. Activate your existing environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
3. Install Flask:
   ```powershell
   pip install -r requirements.txt
   ```
4. Start the dashboard:
   ```powershell
   python app.py
   ```
5. Open the local address printed by Flask, normally `http://127.0.0.1:5000`.

## How to test
1. Upload a NASA temperature image or video that has a visible legend.
2. Enter the minimum and maximum values printed on that legend.
3. Click **Sample low colour**, then click the low end of the legend on the preview.
4. Click **Sample high colour**, then click the high end of the legend.
5. Click **Select map point**, then click a location inside the mapped data area.
6. For a video, press play. The estimate and pitch update as frames change.
7. Press **Enable sound** to hear the tone.

## Notes
- This is a local development prototype, not a public production server.
- Uploads are saved in `uploads/`.
- The Flask development server uses debug mode; do not expose it to the public internet.
- The current version is separate from the legacy command-line `nasa_visualizer.py`, so it does not replace or delete that file.
