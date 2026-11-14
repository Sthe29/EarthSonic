// ============================================================
// EARTHSONIC — ACCESSIBLE NASA SST SONIFICATION ENGINE
// NASA Space Apps Challenge 2026 — The Earth Information Jukebox
// ============================================================

(function () {
    "use strict";

    // Application Configuration
    const config = window.EARTHSONIC_CONFIG || {
        mediaSource: "nasa",
        uploadedFilename: null,
        mediaType: "image",
        defaultNasaImage: "/static/nasa/sst_mur_print.jpg"
    };

    // DOM Elements
    const canvasContainer = document.getElementById("canvas-container");
    const canvas = document.getElementById("analysis-canvas");
    const mediaImage = document.getElementById("media-image");
    const selectionBox = document.getElementById("selection-box");
    const tooltip = document.getElementById("canvas-tooltip");

    // Mode Buttons
    const btnModeRoi = document.getElementById("btn-mode-roi");
    const btnModePixel = document.getElementById("btn-mode-pixel");

    // Audio Elements
    const btnPlay = document.getElementById("btn-play");
    const btnPause = document.getElementById("btn-pause");
    const btnStop = document.getElementById("btn-stop");
    const volumeControl = document.getElementById("volume-control");
    const volumeReadout = document.getElementById("volume-readout");
    const audioStatePill = document.getElementById("audio-state-pill");

    // Measurement Readouts
    const tempPrimaryValue = document.getElementById("temp-primary-value");
    const tempClassificationPill = document.getElementById("temp-classification-pill");
    const measurementStatusText = document.getElementById("measurement-status-text");
    const metricRegionType = document.getElementById("metric-region-type");
    const metricOceanPct = document.getElementById("metric-ocean-pct");
    const metricMinMax = document.getElementById("metric-minmax");
    const metricStdDev = document.getElementById("metric-stddev");
    const metricCoords = document.getElementById("metric-coords");
    const metricConfidence = document.getElementById("metric-confidence");
    const announcer = document.getElementById("accessibility-announcer");

    // Thermal Zone Distribution Bars
    const barPolar = document.getElementById("bar-polar");
    const barSubpolar = document.getElementById("bar-subpolar");
    const barTemperate = document.getElementById("bar-temperate");
    const barSubtropical = document.getElementById("bar-subtropical");
    const barTropical = document.getElementById("bar-tropical");

    // Numerical MUR Data Elements (NOAA ERDDAP)
    const murQueryForm = document.getElementById("mur-query-form");
    const murInputLat = document.getElementById("mur-input-lat");
    const murInputLon = document.getElementById("mur-input-lon");
    const murInputDate = document.getElementById("mur-input-date");
    const btnFetchMur = document.getElementById("btn-fetch-mur");
    const btnSyncCanvasCoords = document.getElementById("btn-sync-canvas-coords");
    const murLoading = document.getElementById("mur-loading");
    const murError = document.getElementById("mur-error");
    const murErrorMessage = document.getElementById("mur-error-message");
    const murResults = document.getElementById("mur-results");
    const murTempValue = document.getElementById("mur-temp-value");
    const murMaskPill = document.getElementById("mur-mask-pill");
    const murStatusText = document.getElementById("mur-status-text");
    const murErrorVal = document.getElementById("mur-error-val");
    const murCoordsVal = document.getElementById("mur-coords-val");
    const murTimeVal = document.getElementById("mur-time-val");
    const murClassificationVal = document.getElementById("mur-classification-val");
    const murProviderVal = document.getElementById("mur-provider-val");
    const murProductVal = document.getElementById("mur-product-val");

    // Numerical MUR Sonification Elements
    const btnPlayMur = document.getElementById("btn-play-mur");
    const btnStopMur = document.getElementById("btn-stop-mur");
    const murAudioPill = document.getElementById("mur-audio-pill");
    const murAudioFreq = document.getElementById("mur-audio-freq");
    const murAudioDesc = document.getElementById("mur-audio-desc");

    // State Variables
    let selectionMode = "roi"; // "roi" or "pixel"
    let currentSelection = { x: 150, y: 210, width: 120, height: 90 }; // Default: Equatorial Pacific
    let isDragging = false;
    let dragStart = { x: 0, y: 0 };
    let currentTempC = 28.98;
    let currentStdDev = 1.84;
    let isOceanValid = true;

    // Web Audio Engine State (Image-Based Colormap Sonification)
    let audioCtx = null;
    let masterOsc = null;
    let lfoOsc = null;
    let lfoGain = null;
    let masterGain = null;
    let isAudioPlaying = false;

    // Web Audio Engine State (Authentic Numerical MUR Sonification)
    let murOsc = null;
    let murGain = null;
    let isMurAudioPlaying = false;
    let currentMurSstC = 22.86; // Default to initial Durban ocean value
    let isMurOceanValid = true;

    // Numerical Mapping Range (-5°C to +35°C mapped linearly to 160 Hz to 880 Hz)
    const MUR_MIN_TEMP = -5.0;
    const MUR_MAX_TEMP = 35.0;
    const MUR_MIN_FREQ = 160.0;
    const MUR_MAX_FREQ = 880.0;

    // ============================================================
    // CANVAS & IMAGE RENDERING
    // ============================================================

    function initCanvas() {
        if (!canvas || !mediaImage) return;

        function render() {
            canvas.width = mediaImage.naturalWidth || 1024;
            canvas.height = mediaImage.naturalHeight || 512;
            const ctx = canvas.getContext("2d");
            ctx.drawImage(mediaImage, 0, 0, canvas.width, canvas.height);
            drawOverlay();
        }

        if (mediaImage.complete && mediaImage.naturalWidth > 0) {
            render();
        } else {
            mediaImage.addEventListener("load", render);
        }
    }

    function drawOverlay() {
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(mediaImage, 0, 0, canvas.width, canvas.height);

        // Draw selected region or point
        if (selectionMode === "roi" && currentSelection) {
            const { x, y, width, height } = currentSelection;
            ctx.strokeStyle = "#38bdf8";
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, width, height);

            ctx.fillStyle = "rgba(56, 189, 248, 0.2)";
            ctx.fillRect(x, y, width, height);

            // Geographic boundary text tag
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 12px monospace";
            ctx.fillText(`ROI: ${width}x${height}px`, x + 4, y > 18 ? y - 4 : y + 14);
        } else if (selectionMode === "pixel" && currentSelection) {
            const { x, y } = currentSelection;
            ctx.beginPath();
            ctx.arc(x, y, 6, 0, Math.PI * 2);
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(x, y, 2, 0, Math.PI * 2);
            ctx.fillStyle = "#38bdf8";
            ctx.fill();
        }
    }

    // ============================================================
    // MOUSE & TOUCH INTERACTION ON CANVAS
    // ============================================================

    function getCanvasCoordinates(event) {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;

        const clientX = event.clientX || (event.touches && event.touches[0].clientX);
        const clientY = event.clientY || (event.touches && event.touches[0].clientY);

        const x = Math.max(0, Math.min(canvas.width - 1, Math.round((clientX - rect.left) * scaleX)));
        const y = Math.max(0, Math.min(canvas.height - 1, Math.round((clientY - rect.top) * scaleY)));

        return { x, y };
    }

    canvasContainer.addEventListener("mousedown", (e) => {
        if (e.button !== 0) return; // Left click only
        const coords = getCanvasCoordinates(e);
        isDragging = true;
        dragStart = coords;

        if (selectionMode === "pixel") {
            currentSelection = { x: coords.x, y: coords.y, width: 1, height: 1 };
            drawOverlay();
            requestPixelAnalysis(coords.x, coords.y);
            syncCoordinatesFromCanvas();
            isDragging = false;
        } else {
            currentSelection = { x: coords.x, y: coords.y, width: 0, height: 0 };
        }
    });

    window.addEventListener("mousemove", (e) => {
        if (!isDragging || selectionMode !== "roi") return;
        const coords = getCanvasCoordinates(e);

        const x = Math.min(dragStart.x, coords.x);
        const y = Math.min(dragStart.y, coords.y);
        const width = Math.max(4, Math.abs(coords.x - dragStart.x));
        const height = Math.max(4, Math.abs(coords.y - dragStart.y));

        currentSelection = { x, y, width, height };
        drawOverlay();
    });

    window.addEventListener("mouseup", () => {
        if (!isDragging) return;
        isDragging = false;

        if (selectionMode === "roi" && currentSelection && currentSelection.width > 2 && currentSelection.height > 2) {
            requestRoiAnalysis(currentSelection.x, currentSelection.y, currentSelection.width, currentSelection.height);
            syncCoordinatesFromCanvas();
        }
    });

    // Preset Region Buttons
    document.querySelectorAll(".preset-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const [x, y, w, h] = btn.getAttribute("data-roi").split(",").map(Number);
            selectionMode = "roi";
            updateModeButtons();
            currentSelection = { x, y, width: w, height: h };
            drawOverlay();
            requestRoiAnalysis(x, y, w, h);
            syncCoordinatesFromCanvas();
        });
    });

    // Tool Pills (ROI vs Pixel)
    btnModeRoi.addEventListener("click", () => {
        selectionMode = "roi";
        updateModeButtons();
    });

    btnModePixel.addEventListener("click", () => {
        selectionMode = "pixel";
        updateModeButtons();
    });

    function updateModeButtons() {
        btnModeRoi.classList.toggle("active", selectionMode === "roi");
        btnModeRoi.setAttribute("aria-checked", selectionMode === "roi");
        btnModePixel.classList.toggle("active", selectionMode === "pixel");
        btnModePixel.setAttribute("aria-checked", selectionMode === "pixel");
        drawOverlay();
    }

    // ============================================================
    // BACKEND API ANALYSIS CALLS
    // ============================================================

    async function requestRoiAnalysis(x, y, width, height) {
        measurementStatusText.textContent = "Analyzing region with OpenCV...";
        try {
            const response = await fetch("/api/analyze-region", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    media_source: config.mediaSource,
                    filename: config.uploadedFilename,
                    x, y, width, height
                })
            });

            if (!response.ok) throw new Error("Backend analysis failed");
            const data = await response.json();
            updateDashboardWithRoi(data);
        } catch (err) {
            console.error("ROI Analysis Error:", err);
            measurementStatusText.textContent = "Analysis error. Please retry.";
        }
    }

    async function requestPixelAnalysis(x, y) {
        measurementStatusText.textContent = "Sampling pixel with OpenCV...";
        try {
            const response = await fetch("/api/sample-pixel", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    media_source: config.mediaSource,
                    filename: config.uploadedFilename,
                    x, y
                })
            });

            if (!response.ok) throw new Error("Backend pixel analysis failed");
            const data = await response.json();
            updateDashboardWithPixel(data);
        } catch (err) {
            console.error("Pixel Analysis Error:", err);
            measurementStatusText.textContent = "Sampling error. Please retry.";
        }
    }

    // ============================================================
    // DASHBOARD READOUT UPDATES
    // ============================================================

    function updateDashboardWithRoi(data) {
        metricRegionType.textContent = `ROI (${data.roi.width}×${data.roi.height} px)`;
        metricOceanPct.textContent = `${data.ocean_coverage_pct}%`;
        metricCoords.textContent = data.geo_bbox ? data.geo_bbox.description : "Global Equirectangular";

        if (data.valid_pixel_count === 0) {
            isOceanValid = false;
            currentTempC = null;
            tempPrimaryValue.textContent = "—";
            tempClassificationPill.textContent = "Land / Ice Mask";
            tempClassificationPill.className = "classification-pill masked";
            measurementStatusText.textContent = data.warning || "Selected area is continental land or polar sea ice.";
            metricMinMax.textContent = "N/A (Masked)";
            metricStdDev.textContent = "N/A";
            metricConfidence.textContent = "Excluded";

            resetDistributionBars();
            announce("Selected region is over continental land or polar ice. No sea surface temperature is present.");
            if (isAudioPlaying) updateSoundTone(null, 0);
            return;
        }

        isOceanValid = true;
        currentTempC = data.mean_temp_c;
        currentStdDev = data.std_dev_c;

        tempPrimaryValue.textContent = `${data.mean_temp_c.toFixed(2)}°C`;
        tempClassificationPill.textContent = data.classification || "Temperate Waters";
        tempClassificationPill.className = `classification-pill ${getPillClass(data.mean_temp_c)}`;
        measurementStatusText.textContent = `Valid ocean pixels: ${data.valid_pixel_count.toLocaleString()} · ${data.confidence}`;

        metricMinMax.textContent = `${data.min_temp_c.toFixed(1)}°C – ${data.max_temp_c.toFixed(1)}°C`;
        metricStdDev.textContent = `± ${data.std_dev_c.toFixed(2)}°C`;
        metricConfidence.textContent = `ΔE = ${data.mean_delta_e} (High)`;

        updateDistributionBars(data.thermal_zones);

        const speechText = `Selected ocean region. Mean temperature ${data.mean_temp_c.toFixed(1)} degrees Celsius. ${data.classification}. Ocean coverage ${data.ocean_coverage_pct} percent.`;
        announce(speechText);

        if (isAudioPlaying) {
            updateSoundTone(currentTempC, currentStdDev);
        }
    }

    function updateDashboardWithPixel(data) {
        metricRegionType.textContent = `Single Pixel (${data.x}, ${data.y})`;
        metricOceanPct.textContent = data.is_ocean ? "100% (Ocean)" : "0% (Land Mask)";
        metricCoords.textContent = `${Math.abs(data.lat)}°${data.lat < 0 ? "S" : "N"}, ${Math.abs(data.lon)}°${data.lon < 0 ? "W" : "E"}`;

        if (!data.is_ocean) {
            isOceanValid = false;
            currentTempC = null;
            tempPrimaryValue.textContent = "—";
            tempClassificationPill.textContent = "Land Mask";
            tempClassificationPill.className = "classification-pill masked";
            measurementStatusText.textContent = "Sampled pixel is on continental land or sea-ice mask.";
            metricMinMax.textContent = "N/A";
            metricStdDev.textContent = "N/A";
            metricConfidence.textContent = "Excluded";
            resetDistributionBars();
            announce("Selected point is on continental land. No ocean temperature.");
            if (isAudioPlaying) updateSoundTone(null, 0);
            return;
        }

        isOceanValid = true;
        currentTempC = data.estimated_temp_c;
        currentStdDev = 0;

        tempPrimaryValue.textContent = `${data.estimated_temp_c.toFixed(1)}°C`;
        tempClassificationPill.textContent = data.classification;
        tempClassificationPill.className = `classification-pill ${getPillClass(data.estimated_temp_c)}`;
        measurementStatusText.textContent = `Pixel RGB: [${data.rgb.join(", ")}] · Confidence: ${data.confidence}`;

        metricMinMax.textContent = "Single Point";
        metricStdDev.textContent = "0.00°C (Point)";
        metricConfidence.textContent = `ΔE = ${data.delta_e} (${data.confidence})`;

        announce(`Sampled point at ${metricCoords.textContent}. Temperature ${data.estimated_temp_c} degrees Celsius. ${data.classification}.`);

        if (isAudioPlaying) {
            updateSoundTone(currentTempC, 0);
        }
    }

    function getPillClass(temp) {
        if (temp === null) return "masked";
        if (temp < 0) return "polar";
        if (temp < 18) return "temperate";
        return "warm";
    }

    function updateDistributionBars(zones) {
        if (!zones) return;
        barPolar.style.width = `${zones.polar_cold_below_0}%`;
        barSubpolar.style.width = `${zones.subpolar_0_to_10}%`;
        barTemperate.style.width = `${zones.temperate_10_to_20}%`;
        barSubtropical.style.width = `${zones.subtropical_20_to_26}%`;
        barTropical.style.width = `${zones.tropical_above_26}%`;
    }

    function resetDistributionBars() {
        barPolar.style.width = "0%";
        barSubpolar.style.width = "0%";
        barTemperate.style.width = "0%";
        barSubtropical.style.width = "0%";
        barTropical.style.width = "0%";
    }

    function announce(text) {
        if (announcer) {
            announcer.textContent = text;
        }
    }

    // ============================================================
    // WEB AUDIO SONIFICATION ENGINE
    // ============================================================

    function initAudioContext() {
        if (audioCtx) return;
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        audioCtx = new AudioContextClass();

        // Master Oscillator (Pitch represents Sea Surface Temperature)
        masterOsc = audioCtx.createOscillator();
        masterOsc.type = "sine";
        masterOsc.frequency.value = 440;

        // LFO (Tremolo / Pulse represents Thermal Variance / StdDev)
        lfoOsc = audioCtx.createOscillator();
        lfoOsc.type = "sine";
        lfoOsc.frequency.value = 1.0;

        lfoGain = audioCtx.createGain();
        lfoGain.gain.value = 0.0; // Depth of tremolo

        masterGain = audioCtx.createGain();
        masterGain.gain.value = 0.0; // Master volume

        // Audio Graph Routing:
        // LFO -> masterGain.gain (amplitude modulation)
        lfoOsc.connect(lfoGain);
        lfoGain.connect(masterGain.gain);

        masterOsc.connect(masterGain);
        masterGain.connect(audioCtx.destination);

        masterOsc.start();
        lfoOsc.start();
    }

    function tempToFrequency(temp) {
        // Temperature range: -5°C to +35°C (40°C total span)
        // Frequency range: 160 Hz (Deep Bass D#3) to 880 Hz (Treble A5)
        const clamped = Math.max(-5, Math.min(35, temp));
        const ratio = (clamped - (-5.0)) / 40.0;
        return 160 + ratio * 720;
    }

    function updateSoundTone(temp, stdDev) {
        if (!audioCtx || !masterOsc || !masterGain) return;

        if (temp === null || !isOceanValid) {
            // Land or invalid area: low muted frequency with slow pulse
            masterOsc.frequency.setTargetAtTime(110, audioCtx.currentTime, 0.08); // Low A2
            lfoOsc.frequency.setTargetAtTime(1.5, audioCtx.currentTime, 0.08);
            lfoGain.gain.setTargetAtTime(0.04, audioCtx.currentTime, 0.08);
            audioStatePill.textContent = "Land / Mask Alert Tone";
            audioStatePill.className = "status-pill idle";
            return;
        }

        const targetFreq = tempToFrequency(temp);
        masterOsc.frequency.setTargetAtTime(targetFreq, audioCtx.currentTime, 0.08);

        // Map spatial variance (StdDev 0 to 6°C) to LFO frequency (0.5 Hz to 6 Hz)
        const pulseRate = 0.5 + Math.min(6.0, stdDev || 0) * 0.9;
        const pulseDepth = Math.min(0.08, (stdDev || 0) * 0.02);

        lfoOsc.frequency.setTargetAtTime(pulseRate, audioCtx.currentTime, 0.08);
        lfoGain.gain.setTargetAtTime(pulseDepth, audioCtx.currentTime, 0.08);

        audioStatePill.textContent = `Playing ${temp.toFixed(1)}°C (${Math.round(targetFreq)} Hz)`;
        audioStatePill.className = "status-pill playing";
    }

    async function startAudio() {
        if (isMurAudioPlaying) {
            stopMurAudio();
        }

        initAudioContext();
        if (audioCtx.state === "suspended") {
            await audioCtx.resume();
        }

        const vol = parseFloat(volumeControl.value) || 0.2;
        masterGain.gain.setTargetAtTime(vol, audioCtx.currentTime, 0.05);
        isAudioPlaying = true;

        updateSoundTone(currentTempC, currentStdDev);
    }

    function pauseAudio() {
        if (!audioCtx || !masterGain) return;
        masterGain.gain.setTargetAtTime(0, audioCtx.currentTime, 0.05);
        isAudioPlaying = false;
        audioStatePill.textContent = "Audio Paused";
        audioStatePill.className = "status-pill idle";
    }

    function stopAudio() {
        if (!audioCtx || !masterGain) return;
        masterGain.gain.setTargetAtTime(0, audioCtx.currentTime, 0.05);
        isAudioPlaying = false;
        audioStatePill.textContent = "Audio Stopped";
        audioStatePill.className = "status-pill idle";
    }

    // Audio Button Listeners
    btnPlay.addEventListener("click", startAudio);
    btnPause.addEventListener("click", pauseAudio);
    btnStop.addEventListener("click", stopAudio);

    volumeControl.addEventListener("input", () => {
        const vol = parseFloat(volumeControl.value);
        volumeReadout.textContent = `${Math.round(vol * 100)}%`;
        if (audioCtx && isAudioPlaying && masterGain) {
            masterGain.gain.setTargetAtTime(vol, audioCtx.currentTime, 0.02);
        }
        if (audioCtx && isMurAudioPlaying && murGain) {
            murGain.gain.setTargetAtTime(vol, audioCtx.currentTime, 0.02);
        }
    });

    // Keyboard Shortcuts for Accessibility
    window.addEventListener("keydown", (e) => {
        if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;

        if (e.code === "Space") {
            e.preventDefault();
            if (isAudioPlaying) pauseAudio();
            else startAudio();
        } else if (e.code === "KeyS") {
            e.preventDefault();
            stopAudio();
            stopMurAudio();
        }
    });

    // ============================================================
    // NUMERICAL MUR DATA INTEGRATION (NOAA COASTWATCH ERDDAP)
    // ============================================================

    function syncCoordinatesFromCanvas() {
        if (!canvas || !currentSelection) return;
        const imgW = canvas.width || 1024;
        const imgH = canvas.height || 512;
        let lat, lon;

        if (selectionMode === "pixel") {
            lat = 90.0 - (currentSelection.y / imgH) * 180.0;
            lon = (currentSelection.x / imgW) * 360.0 - 180.0;
        } else {
            const cx = currentSelection.x + (currentSelection.width / 2.0);
            const cy = currentSelection.y + (currentSelection.height / 2.0);
            lat = 90.0 - (cy / imgH) * 180.0;
            lon = (cx / imgW) * 360.0 - 180.0;
        }

        lat = Math.max(-89.99, Math.min(89.99, lat));
        lon = Math.max(-179.99, Math.min(180.0, lon));

        if (murInputLat) murInputLat.value = lat.toFixed(2);
        if (murInputLon) murInputLon.value = lon.toFixed(2);

        announce(`Synchronized map coordinates: ${lat.toFixed(2)} latitude, ${lon.toFixed(2)} longitude.`);
    }

    // ============================================================
    // NUMERICAL MUR DATA SONIFICATION (NOAA ERDDAP L4 SST)
    // ============================================================

    function calculateMurFrequency(temp) {
        if (temp === null || temp === undefined || isNaN(temp)) return null;
        const clamped = Math.max(MUR_MIN_TEMP, Math.min(MUR_MAX_TEMP, parseFloat(temp)));
        // Linear relationship:
        // frequency = minFreq + ((temp - minTemp) / (maxTemp - minTemp)) * (maxFreq - minFreq)
        return MUR_MIN_FREQ + ((clamped - MUR_MIN_TEMP) / (MUR_MAX_TEMP - MUR_MIN_TEMP)) * (MUR_MAX_FREQ - MUR_MIN_FREQ);
    }

    async function startMurAudio() {
        if (!isMurOceanValid || currentMurSstC === null) return;

        // Stop image audio if playing so both do not conflict
        if (isAudioPlaying) {
            stopAudio();
        }

        initAudioContext();
        if (audioCtx.state === "suspended") {
            await audioCtx.resume();
        }

        // Clean up any lingering murOsc
        if (murOsc) {
            try { murOsc.stop(); murOsc.disconnect(); } catch (e) {}
            murOsc = null;
        }

        const targetFreq = calculateMurFrequency(currentMurSstC);
        if (targetFreq === null) return;

        murOsc = audioCtx.createOscillator();
        murOsc.type = "sine";
        murOsc.frequency.setValueAtTime(targetFreq, audioCtx.currentTime);

        murGain = audioCtx.createGain();
        murGain.gain.setValueAtTime(0.0001, audioCtx.currentTime);

        murOsc.connect(murGain);
        murGain.connect(audioCtx.destination);

        murOsc.start();
        const vol = parseFloat(volumeControl ? volumeControl.value : 0.2) || 0.2;
        murGain.gain.exponentialRampToValueAtTime(vol, audioCtx.currentTime + 0.05);

        isMurAudioPlaying = true;
        if (btnPlayMur) btnPlayMur.disabled = true;
        if (btnStopMur) btnStopMur.disabled = false;
        if (murAudioPill) {
            murAudioPill.textContent = `Playing ${currentMurSstC.toFixed(2)}°C (${Math.round(targetFreq)} Hz)`;
            murAudioPill.className = "status-pill playing";
        }

        announce(`Playing numerical MUR tone for ${currentMurSstC.toFixed(2)} degrees Celsius at ${Math.round(targetFreq)} Hertz.`);
    }

    function stopMurAudio() {
        if (murOsc && murGain && audioCtx) {
            try {
                murGain.gain.setValueAtTime(murGain.gain.value, audioCtx.currentTime);
                murGain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.04);
                const oscToStop = murOsc;
                setTimeout(() => {
                    try {
                        oscToStop.stop();
                        oscToStop.disconnect();
                    } catch (e) {}
                }, 50);
            } catch (e) {}
        }
        murOsc = null;
        isMurAudioPlaying = false;
        if (btnPlayMur) btnPlayMur.disabled = !isMurOceanValid;
        if (btnStopMur) btnStopMur.disabled = true;
        if (murAudioPill) {
            murAudioPill.textContent = "Audio Stopped";
            murAudioPill.className = "status-pill idle";
        }
        announce("Stopped numerical MUR tone.");
    }

    async function requestMurNumericalData(latVal, lonVal, dateVal) {
        if (isMurAudioPlaying) stopMurAudio();

        const lat = parseFloat(latVal);
        const lon = parseFloat(lonVal);

        if (isNaN(lat) || lat < -90.0 || lat > 90.0) {
            showMurError("Invalid latitude. Must be a numeric value between -90.0° and +90.0°.");
            return;
        }
        if (isNaN(lon) || lon < -180.0 || lon > 180.0) {
            showMurError("Invalid longitude. Must be a numeric value between -180.0° and +180.0°.");
            return;
        }
        if (!dateVal || !dateVal.trim()) {
            showMurError("Please select a valid observation date (YYYY-MM-DD).");
            return;
        }

        // Set UI loading state
        if (murLoading) murLoading.style.display = "flex";
        if (murError) murError.style.display = "none";
        if (murResults) murResults.style.display = "none";
        if (btnFetchMur) btnFetchMur.disabled = true;

        try {
            const response = await fetch("/api/mur-sst", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    latitude: lat,
                    longitude: lon,
                    date: dateVal.trim()
                })
            });

            const data = await response.json();

            if (!response.ok || data.status === "error") {
                const errMsg = data.message || `Upstream service notice (HTTP ${response.status}).`;
                showMurError(errMsg);
                return;
            }

            updateMurResults(data);
        } catch (err) {
            console.error("ERDDAP Network Error:", err);
            showMurError("Unable to connect to EarthSonic backend or NOAA CoastWatch ERDDAP service.");
        } finally {
            if (murLoading) murLoading.style.display = "none";
            if (btnFetchMur) btnFetchMur.disabled = false;
        }
    }

    function showMurError(message) {
        if (isMurAudioPlaying) stopMurAudio();
        isMurOceanValid = false;
        currentMurSstC = null;
        if (murLoading) murLoading.style.display = "none";
        if (murResults) murResults.style.display = "none";
        if (murError) {
            murError.style.display = "flex";
            if (murErrorMessage) murErrorMessage.textContent = message;
        }
        if (btnPlayMur) btnPlayMur.disabled = true;
        if (btnStopMur) btnStopMur.disabled = true;
        if (murAudioPill) {
            murAudioPill.textContent = "Unavailable";
            murAudioPill.className = "status-pill idle";
        }
        if (murAudioDesc) murAudioDesc.textContent = "Sonification unavailable due to service error.";
        announce(`Notice: ${message}`);
    }

    function updateMurResults(data) {
        if (isMurAudioPlaying) stopMurAudio();
        if (murError) murError.style.display = "none";
        if (murResults) murResults.style.display = "flex";

        currentMurSstC = data.analysed_sst_c;
        isMurOceanValid = data.is_ocean && data.analysed_sst_c !== null;

        if (isMurOceanValid) {
            if (murTempValue) murTempValue.textContent = `${data.analysed_sst_c.toFixed(2)}°C`;
            if (murMaskPill) {
                murMaskPill.textContent = "Open Sea (Ocean)";
                murMaskPill.className = `classification-pill ${getPillClass(data.analysed_sst_c)}`;
            }
            if (murStatusText) {
                murStatusText.textContent = "Foundation SST · NASA/JPL Multi-Resolution Variational Analysis (MRVA)";
            }
            if (murErrorVal) {
                murErrorVal.textContent = data.analysis_error_c !== null 
                    ? `± ${data.analysis_error_c.toFixed(2)}°C (1σ)` 
                    : "N/A";
            }

            // Update numerical audio controls
            const freq = calculateMurFrequency(currentMurSstC);
            if (murAudioFreq) murAudioFreq.textContent = `${Math.round(freq)} Hz`;
            if (murAudioDesc) {
                murAudioDesc.innerHTML = `Frequency: <strong id="mur-audio-freq">${Math.round(freq)} Hz</strong> (Linear scale: -5°C = 160 Hz, 35°C = 880 Hz).`;
            }
            if (btnPlayMur) btnPlayMur.disabled = false;
            if (btnStopMur) btnStopMur.disabled = true;
            if (murAudioPill) {
                murAudioPill.textContent = "Audio Idle";
                murAudioPill.className = "status-pill idle";
            }
        } else {
            if (murTempValue) murTempValue.textContent = "—";
            if (murMaskPill) {
                murMaskPill.textContent = (data.mask_classification || "MASKED").toUpperCase();
                murMaskPill.className = "classification-pill masked";
            }
            if (murStatusText) {
                murStatusText.textContent = data.warning || "Selected coordinates are over continental land or sea-ice mask. Ocean temperature is masked in MUR dataset.";
            }
            if (murErrorVal) murErrorVal.textContent = "N/A (Masked)";

            // Disable numerical audio controls for land/masked area
            if (murAudioFreq) murAudioFreq.textContent = "N/A (Masked)";
            if (murAudioDesc) {
                murAudioDesc.textContent = `Sonification disabled: Selected coordinates are over non-ocean surface (${data.mask_classification || 'masked'}).`;
            }
            if (btnPlayMur) btnPlayMur.disabled = true;
            if (btnStopMur) btnStopMur.disabled = true;
            if (murAudioPill) {
                murAudioPill.textContent = "Playback Disabled";
                murAudioPill.className = "status-pill idle";
            }
        }

        if (murCoordsVal && data.coordinates) {
            const lat = data.coordinates.grid_latitude;
            const lon = data.coordinates.grid_longitude;
            murCoordsVal.textContent = `${Math.abs(lat).toFixed(2)}°${lat < 0 ? 'S' : 'N'}, ${Math.abs(lon).toFixed(2)}°${lon < 0 ? 'W' : 'E'}`;
        }

        if (murTimeVal && data.time) {
            const ts = data.time.dataset_timestamp || data.time.requested_date;
            murTimeVal.textContent = ts.replace("T", " ").replace(":00Z", " UTC");
        }

        if (murClassificationVal) {
            murClassificationVal.textContent = `${data.mask_classification} (${data.mask_description || 'Surface mask'})`;
        }
        if (murProviderVal) murProviderVal.textContent = "NOAA CoastWatch ERDDAP";
        if (murProductVal) murProductVal.textContent = "Level-4 Foundation SST";

        const announcement = isMurOceanValid 
            ? `Retrieved MUR numerical data. Temperature is ${data.analysed_sst_c.toFixed(2)} degrees Celsius. Observation uncertainty plus minus ${data.analysis_error_c ? data.analysis_error_c.toFixed(2) : 0} degrees. Pitch is ${Math.round(calculateMurFrequency(currentMurSstC))} Hertz.`
            : `Retrieved MUR numerical data for coordinates. Area is classified as ${data.mask_classification}. Ocean temperature is masked.`;
        announce(announcement);
    }

    // Attach ERDDAP Form Listeners
    if (murQueryForm) {
        murQueryForm.addEventListener("submit", (e) => {
            e.preventDefault();
            requestMurNumericalData(murInputLat.value, murInputLon.value, murInputDate.value);
        });
    }

    if (btnFetchMur) {
        btnFetchMur.addEventListener("click", () => {
            requestMurNumericalData(murInputLat.value, murInputLon.value, murInputDate.value);
        });
    }

    if (btnSyncCanvasCoords) {
        btnSyncCanvasCoords.addEventListener("click", syncCoordinatesFromCanvas);
    }

    if (btnPlayMur) {
        btnPlayMur.addEventListener("click", startMurAudio);
    }

    if (btnStopMur) {
        btnStopMur.addEventListener("click", stopMurAudio);
    }

    // Expose for automated verification and test harnesses
    window.EarthSonic = {
        calculateMurFrequency,
        startMurAudio,
        stopMurAudio,
        MIN_TEMP: MUR_MIN_TEMP,
        MAX_TEMP: MUR_MAX_TEMP,
        MIN_FREQ: MUR_MIN_FREQ,
        MAX_FREQ: MUR_MAX_FREQ
    };

    // ============================================================
    // INITIALIZATION
    // ============================================================

    window.addEventListener("DOMContentLoaded", () => {
        initCanvas();
        // Load initial default region analysis
        requestRoiAnalysis(currentSelection.x, currentSelection.y, currentSelection.width, currentSelection.height);
    });
})();
