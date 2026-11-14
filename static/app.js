
 // ============================================================
 // EARTHSONIC - IMAGE AND VIDEO ANALYSIS
 // ============================================================

 // Find the canvas used internally for displaying and sampling pixels.
 const canvas = document.getElementById("analysis-canvas");

 // Find the uploaded image element.
 const image = document.getElementById("media-image");

 // Find the uploaded video element.
 const video = document.getElementById("media-video");

 // Find the temperature display.
 const temperatureValue = document.getElementById("temperature-value");

 // Find the temperature explanation.
 const temperatureStatus = document.getElementById("temperature-status");

 // Find the sampling instructions.
 const samplingStatus = document.getElementById("sampling-status");

 // Find the selected pixel display.
 const pixelReadout = document.getElementById("pixel-readout");

 // Find the video time display.
 const timeReadout = document.getElementById("time-readout");

 // Find the low temperature input.
 const lowInput = document.getElementById("low-temp");

 // Find the high temperature input.
 const highInput = document.getElementById("high-temp");

 // Find the sound button.
 const soundButton = document.getElementById("sound-toggle");

 // Find the volume slider.
 const volumeInput = document.getElementById("volume");

 // Find the upload input.
 const fileInput = document.getElementById("media-input");

 // Track the current sampling mode.
 let samplingMode = null;

 // Store the low legend colour.
 let lowColour = null;

 // Store the high legend colour.
 let highColour = null;

 // Store the selected pixel coordinates.
 let selectedPoint = null;

 // Store the active media element.
 let activeMedia = null;

 // Identify whether the uploaded resource is a video.
 let isVideoActive = false;

 // Store the animation frame request.
 let animationFrameId = null;

 // Store the audio engine.
 let audioContext = null;

 // Store the sound oscillator.
 let oscillator = null;

 // Store the volume controller.
 let gainNode = null;

 // Store the latest temperature estimate.
 let currentTemperature = null;


 // ============================================================
 // IDENTIFY THE UPLOADED RESOURCE
 // ============================================================

 // Check whether a media element has a source.
 function hasMediaSource(element) {
     if (!element) return false; // Stop if the element does not exist.
     return Boolean(element.getAttribute("src") || element.querySelector("source")?.getAttribute("src")); // Check direct and nested sources.
 }

 // Determine which uploaded resource is available.
 function identifyMedia() {
     if (hasMediaSource(video)) { // Check whether a video source exists.
         activeMedia = video; // Use the video as the active resource.
         isVideoActive = true; // Mark the resource as a video.
     } else if (hasMediaSource(image)) { // Otherwise check for an image.
         activeMedia = image; // Use the image as the active resource.
         isVideoActive = false; // Mark the resource as an image.
     } else { // Handle an empty media workspace.
         activeMedia = null; // Clear the active resource.
         isVideoActive = false; // Reset the media type.
     }
 }

 // Identify the resource when the page loads.
 identifyMedia();


 // ============================================================
 // FILE UPLOAD DISPLAY
 // ============================================================

 // React when the user selects a file.
 if (fileInput) {
     fileInput.addEventListener("change", () => {
         const file = fileInput.files[0]; // Read the selected file.
         const uploadName = document.querySelector(".upload-box strong"); // Find the filename display.
         if (file && uploadName) uploadName.textContent = file.name; // Display the selected filename.
     });
 }


 // ============================================================
 // CANVAS PREPARATION
 // ============================================================

 // Prepare the canvas after the uploaded resource becomes available.
 function setupCanvas() {
     if (!canvas || !activeMedia) return; // Stop if the canvas or resource is missing.

     let width; // Prepare a variable for the resource width.
     let height; // Prepare a variable for the resource height.

     if (isVideoActive) { // Check whether the resource is a video.
         if (video.readyState < 2) return; // Wait until a video frame is available.
         width = video.videoWidth; // Read the original video width.
         height = video.videoHeight; // Read the original video height.
         video.controls = true; // Enable video playback controls.
         video.preload = "auto"; // Ask the browser to load video data.
         video.style.display = "block"; // Keep the video visible.
         video.style.width = "100%"; // Fit the video to its container.
         video.style.height = "auto"; // Preserve the video proportions.
         video.style.objectFit = "contain"; // Prevent the video from being stretched.
         canvas.style.display = "none"; // Hide the analysis canvas visually.
         if (image) image.style.display = "none"; // Hide the unused image element.
     } else { // Handle an uploaded image.
         if (!image || !image.complete || !image.naturalWidth) return; // Wait until the image has loaded.
         width = image.naturalWidth; // Read the original image width.
         height = image.naturalHeight; // Read the original image height.
         image.style.display = "none"; // Hide the original image.
         if (video) video.style.display = "none"; // Hide the unused video element.
         canvas.style.display = "block"; // Display the image canvas.
         canvas.style.width = "100%"; // Fit the canvas to its container.
         canvas.style.height = "auto"; // Preserve the image proportions.
         canvas.style.cursor = "crosshair"; // Show that pixels can be selected.
     }

     canvas.width = width; // Match the canvas to the original resource width.
     canvas.height = height; // Match the canvas to the original resource height.

     drawCurrentFrame(); // Draw the available image or video frame.
 }


 // ============================================================
 // IMAGE LOADING
 // ============================================================

 // Listen for an uploaded image becoming available.
 if (image) {
     image.addEventListener("load", () => {
         identifyMedia(); // Identify the active resource.
         setupCanvas(); // Prepare the image analysis canvas.
     });
 }


 // ============================================================
 // VIDEO LOADING AND PLAYBACK
 // ============================================================

 // Listen for the video metadata becoming available.
 if (video) {
     video.addEventListener("loadedmetadata", () => {
         identifyMedia(); // Identify the uploaded video.
         video.controls = true; // Show playback controls.
         video.style.display = "block"; // Make the video visible.
         video.style.width = "100%"; // Fit the video to the workspace.
         video.style.height = "auto"; // Preserve the video proportions.
         if (timeReadout) timeReadout.textContent = formatTime(video.currentTime); // Display the starting time.
     });

     // Wait until the first actual video frame is ready.
     video.addEventListener("loadeddata", () => {
         identifyMedia(); // Confirm that the video is active.
         setupCanvas(); // Prepare the hidden analysis canvas.
         drawCurrentFrame(); // Draw the first available frame.
     });

     // Update the displayed playback time.
     video.addEventListener("timeupdate", () => {
         if (timeReadout) timeReadout.textContent = formatTime(video.currentTime); // Display the current time.
     });

     // Start analysing frames when playback begins.
     video.addEventListener("play", () => {
         startVideoLoop(); // Begin the frame analysis loop.
     });

     // Refresh the analysis when playback pauses.
     video.addEventListener("pause", () => {
         updateVideoFrame(); // Draw the paused frame.
     });

     // Refresh the analysis when the user changes playback position.
     video.addEventListener("seeked", () => {
         updateVideoFrame(); // Draw the newly selected frame.
     });

     // Report video loading problems.
     video.addEventListener("error", () => {
         if (samplingStatus) samplingStatus.textContent = "Video could not be loaded. Try another MP4 video."; // Display a readable error.
         console.error("EarthSonic video error:", video.error); // Print technical details.
     });
 }


 // ============================================================
 // VIDEO TIME FORMATTING
 // ============================================================

 // Convert seconds into a readable time format.
 function formatTime(seconds) {
     const minutes = Math.floor(seconds / 60); // Calculate whole minutes.
     const remaining = (seconds % 60).toFixed(1).padStart(4, "0"); // Calculate remaining seconds.
     return `${String(minutes).padStart(2, "0")}:${remaining}`; // Return the formatted time.
 }


 // ============================================================
 // DRAW AND ANALYSE THE CURRENT FRAME
 // ============================================================

 // Draw the current image or video frame into the analysis canvas.
 function drawCurrentFrame() {
     if (!canvas || !activeMedia) return; // Stop if no resource is available.

     const context = canvas.getContext("2d", { willReadFrequently: true }); // Get the pixel-analysis context.

     if (isVideoActive) { // Check whether the active resource is a video.
         if (video.readyState < 2 || !video.videoWidth) return; // Wait for a usable video frame.
         if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) { // Check whether dimensions changed.
             canvas.width = video.videoWidth; // Update the canvas width.
             canvas.height = video.videoHeight; // Update the canvas height.
         }
         context.drawImage(video, 0, 0, canvas.width, canvas.height); // Copy the current video frame.
     } else { // Handle an image.
         if (!image || !image.naturalWidth) return; // Stop if the image is unavailable.
         if (canvas.width !== image.naturalWidth || canvas.height !== image.naturalHeight) { // Check image dimensions.
             canvas.width = image.naturalWidth; // Update the canvas width.
             canvas.height = image.naturalHeight; // Update the canvas height.
         }
         context.drawImage(image, 0, 0, canvas.width, canvas.height); // Copy the image into the canvas.
     }

     if (selectedPoint) { // Check whether a pixel has been selected.
         context.beginPath(); // Start drawing the selection marker.
         context.arc(selectedPoint.x, selectedPoint.y, Math.max(5, canvas.width / 180), 0, Math.PI * 2); // Draw the marker.
         context.strokeStyle = "#ffffff"; // Set the marker colour.
         context.lineWidth = Math.max(2, canvas.width / 700); // Scale the marker thickness.
         context.stroke(); // Draw the marker.
     }

     if (selectedPoint && lowColour && highColour) sampleSelectedPoint(); // Update the selected pixel estimate.
 }


 // ============================================================
 // VIDEO FRAME UPDATES
 // ============================================================

 // Refresh the frame when playback is paused or changed.
 function updateVideoFrame() {
     if (isVideoActive) drawCurrentFrame(); // Draw the current video frame.
 }

 // Continuously analyse video frames during playback.
 function startVideoLoop() {
     if (!video || video.paused || video.ended) return; // Stop when the video is not playing.

     drawCurrentFrame(); // Analyse the current frame.

     animationFrameId = requestAnimationFrame(startVideoLoop); // Schedule the next frame.
 }


 // ============================================================
 // SELECT THE PIXEL SAMPLING MODE
 // ============================================================

 // Activate low-temperature legend sampling.
 document.getElementById("sample-low")?.addEventListener("click", () => {
     samplingMode = "low"; // Set the low-colour sampling mode.
     if (samplingStatus) samplingStatus.textContent = "Click the LOW end of the temperature legend."; // Explain the next action.
 });

 // Activate high-temperature legend sampling.
 document.getElementById("sample-high")?.addEventListener("click", () => {
     samplingMode = "high"; // Set the high-colour sampling mode.
     if (samplingStatus) samplingStatus.textContent = "Click the HIGH end of the temperature legend."; // Explain the next action.
 });

 // Activate map-point sampling.
 document.getElementById("sample-point")?.addEventListener("click", () => {
     samplingMode = "point"; // Set the map-point sampling mode.
     if (samplingStatus) samplingStatus.textContent = "Click the location you want to measure."; // Explain the next action.
 });


 // ============================================================
 // PIXEL SELECTION - CORRECTED FOR IMAGES AND VIDEOS
 // ============================================================

 // Handle clicks on the visible image or video.
 function handleMediaClick(event) {
     if (!canvas || !activeMedia || !samplingMode) return; // Stop if no resource or sampling action is active.

     const visibleElement = isVideoActive ? video : canvas; // Use the visible video or image canvas.
     const bounds = visibleElement.getBoundingClientRect(); // Get the dimensions of the visible element.

     if (!bounds.width || !bounds.height) return; // Stop if the visible element has no dimensions.

     const xPosition = (event.clientX - bounds.left) / bounds.width; // Calculate horizontal click position.
     const yPosition = (event.clientY - bounds.top) / bounds.height; // Calculate vertical click position.

     if (xPosition < 0 || xPosition > 1 || yPosition < 0 || yPosition > 1) return; // Reject clicks outside the media.

     const x = Math.min(canvas.width - 1, Math.floor(xPosition * canvas.width)); // Convert horizontal position to an image pixel.
     const y = Math.min(canvas.height - 1, Math.floor(yPosition * canvas.height)); // Convert vertical position to an image pixel.

     drawCurrentFrame(); // Ensure the canvas contains the latest image or video frame.

     const context = canvas.getContext("2d", { willReadFrequently: true }); // Get the pixel-reading context.
     const pixel = context.getImageData(x, y, 1, 1).data; // Read the selected pixel's colour.
     const colour = [pixel[0], pixel[1], pixel[2]]; // Extract the red, green and blue values.

     if (samplingMode === "low") { // Check whether the user is sampling the lowest legend colour.
         lowColour = colour; // Save the low-end colour.
         if (samplingStatus) samplingStatus.textContent = `Low colour captured: ${rgbText(colour)}.`; // Confirm the sample.
     } else if (samplingMode === "high") { // Check whether the user is sampling the highest legend colour.
         highColour = colour; // Save the high-end colour.
         if (samplingStatus) samplingStatus.textContent = `High colour captured: ${rgbText(colour)}.`; // Confirm the sample.
     } else if (samplingMode === "point") { // Check whether the user is selecting a map location.
         selectedPoint = { x, y }; // Save the selected pixel coordinates.
         if (pixelReadout) pixelReadout.textContent = `${x}, ${y}`; // Display the coordinates.
         if (samplingStatus) samplingStatus.textContent = "Map point selected. Calculating temperature..."; // Inform the user.
     }

     samplingMode = null; // Clear the active sampling mode.
     drawCurrentFrame(); // Refresh the display and calculate the temperature if calibrated.
 }

 // Attach sampling to the visible video.
 if (video) {
     video.addEventListener("click", (event) => {
         if (isVideoActive) handleMediaClick(event); // Sample the clicked video pixel.
     });
 }

 // Attach sampling to the visible canvas for images.
 if (canvas) {
     canvas.addEventListener("click", (event) => {
         if (!isVideoActive) handleMediaClick(event); // Sample the clicked image pixel.
     });
 }


 // ============================================================
 // RGB COLOUR FORMATTING
 // ============================================================

 // Format RGB components as readable text.
 function rgbText(colour) {
     return `RGB ${colour[0]}, ${colour[1]}, ${colour[2]}`; // Return the RGB values.
 }


 // ============================================================
 // TEMPERATURE ESTIMATION
 // ============================================================

 // Estimate temperature using the two sampled legend colours.
 function estimateTemperature(pixelColour) {
     if (!lowColour || !highColour) return null; // Require both calibration colours.

     const lowTemp = Number(lowInput?.value); // Read the low temperature.
     const highTemp = Number(highInput?.value); // Read the high temperature.

     if (!Number.isFinite(lowTemp) || !Number.isFinite(highTemp) || highTemp <= lowTemp) return null; // Validate the temperature range.

     const vector = highColour.map((value, index) => value - lowColour[index]); // Calculate the RGB colour direction.
     const denominator = vector.reduce((sum, value) => sum + value * value, 0); // Calculate the squared direction length.

     if (denominator === 0) return null; // Reject identical calibration colours.

     const numerator = pixelColour.reduce((sum, value, index) => sum + (value - lowColour[index]) * vector[index], 0); // Project the pixel onto the colour direction.
     const ratio = Math.max(0, Math.min(1, numerator / denominator)); // Restrict the result to the calibrated range.

     return lowTemp + ratio * (highTemp - lowTemp); // Calculate the estimated temperature.
 }


 // ============================================================
 // UPDATE THE SELECTED PIXEL
 // ============================================================

 // Read the selected location and calculate its current estimate.
 function sampleSelectedPoint() {
     if (!selectedPoint || !lowColour || !highColour || !canvas) return; // Wait for all required samples.

     const context = canvas.getContext("2d", { willReadFrequently: true }); // Get the pixel-reading context.
     const pixel = context.getImageData(selectedPoint.x, selectedPoint.y, 1, 1).data; // Read the selected pixel.
     const colour = [pixel[0], pixel[1], pixel[2]]; // Extract RGB values.
     const estimate = estimateTemperature(colour); // Calculate the estimate.

     if (pixelReadout) pixelReadout.textContent = `${selectedPoint.x}, ${selectedPoint.y} · ${rgbText(colour)}`; // Show pixel information.

     if (estimate === null) { // Check whether calibration is invalid.
         if (temperatureValue) temperatureValue.textContent = "—"; // Clear the temperature.
         if (temperatureStatus) temperatureStatus.textContent = "Check the low and high legend values."; // Explain the problem.
         return; // Stop processing.
     }

     currentTemperature = estimate; // Save the estimated temperature.

     if (temperatureValue) temperatureValue.textContent = `${estimate.toFixed(1)}°C`; // Display the estimated value.
     if (temperatureStatus) temperatureStatus.textContent = "Estimated from the selected pixel and legend calibration."; // Explain the estimate.

     updatePitch(estimate); // Update the sound pitch.
 }


 // ============================================================
 // SOUND GENERATION
 // ============================================================

 // Convert the estimated temperature into a sound frequency.
 function updatePitch(temperature) {
     if (!oscillator || !gainNode || !audioContext) return; // Wait until sound is enabled.

     const lowTemp = Number(lowInput?.value); // Read the low temperature.
     const highTemp = Number(highInput?.value); // Read the high temperature.

     if (highTemp <= lowTemp) return; // Prevent invalid frequency calculations.

     const ratio = Math.max(0, Math.min(1, (temperature - lowTemp) / (highTemp - lowTemp))); // Normalise the temperature.
     const frequency = 220 + ratio * 660; // Map temperature to a frequency between 220 and 880 Hz.

     oscillator.frequency.setTargetAtTime(frequency, audioContext.currentTime, 0.08); // Smoothly change the pitch.
 }


 // ============================================================
 // ENABLE AND DISABLE SOUND
 // ============================================================

 // Handle sound activation.
 soundButton?.addEventListener("click", async () => {
     if (!audioContext) { // Initialise the audio engine if needed.
         audioContext = new (window.AudioContext || window.webkitAudioContext)(); // Create the audio engine.
         oscillator = audioContext.createOscillator(); // Create the tone generator.
         gainNode = audioContext.createGain(); // Create the volume controller.

         oscillator.type = "sine"; // Choose a smooth sine wave.
         oscillator.frequency.value = 440; // Set the starting frequency.
         gainNode.gain.value = 0; // Start with the sound muted.

         oscillator.connect(gainNode); // Connect the oscillator to the volume controller.
         gainNode.connect(audioContext.destination); // Connect the volume controller to the speakers.
         oscillator.start(); // Start the oscillator.
     }

     if (audioContext.state === "running") { // Check whether sound is already enabled.
         await audioContext.suspend(); // Suspend audio playback.
         soundButton.textContent = "Enable sound"; // Update the button.
         return; // Finish disabling sound.
     }

     await audioContext.resume(); // Enable or resume audio playback.
     soundButton.textContent = "Disable sound"; // Update the button.

     gainNode.gain.setTargetAtTime(Number(volumeInput?.value ?? 0.1), audioContext.currentTime, 0.05); // Apply the selected volume.

     if (currentTemperature !== null) updatePitch(currentTemperature); // Restore the current pitch.
 });


 // ============================================================
 // VOLUME CONTROL
 // ============================================================

 // React when the volume slider changes.
 volumeInput?.addEventListener("input", () => {
     if (gainNode && audioContext && audioContext.state === "running") { // Check whether sound is active.
         gainNode.gain.setTargetAtTime(Number(volumeInput.value), audioContext.currentTime, 0.05); // Update the volume.
     }
 });


 // ============================================================
 // TEMPERATURE CALIBRATION INPUTS
 // ============================================================

 // Watch changes to the low and high temperature values.
 [lowInput, highInput].forEach((input) => {
     input?.addEventListener("change", () => {
         if (selectedPoint && lowColour && highColour) drawCurrentFrame(); // Recalculate the current estimate.
     });
 });


 // ============================================================
 // INITIALISE EARTHSONIC
 // ============================================================

 // Prepare any resource already loaded when the page opens.
 window.addEventListener("load", () => {
     identifyMedia(); // Identify the uploaded resource.

     if (isVideoActive && video.readyState >= 2) { // Check whether a video frame is ready.
         setupCanvas(); // Prepare the video analysis canvas.
     } else if (!isVideoActive && image?.complete && image.naturalWidth) { // Check whether an image is already loaded.
         setupCanvas(); // Prepare the image analysis canvas.
     }
 });
