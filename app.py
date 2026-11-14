from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import uuid
import cv2
from vision_engine import engine, SST_MAP_PATH, COLORBAR_PATH

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
NASA_DIR = BASE_DIR / "static" / "nasa"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff", "mp4", "mov", "avi", "mkv", "m4v"}
MAX_UPLOAD_MB = 250

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.secret_key = "earthsonic-dev-key-2026"
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    uploaded_url = None
    uploaded_name = None
    media_type = None
    saved_filename = None

    if request.method == "POST":
        media = request.files.get("media")

        if media is None or media.filename == "":
            flash("Choose an image or video before uploading.", "error")
            return redirect(url_for("index"))

        if not allowed_file(media.filename):
            flash("That file type is not supported. Choose an image or video.", "error")
            return redirect(url_for("index"))

        original_name = secure_filename(media.filename)
        extension = Path(original_name).suffix.lower()
        saved_name = f"{uuid.uuid4().hex}{extension}"
        save_path = UPLOAD_DIR / saved_name
        media.save(save_path)

        uploaded_url = url_for("uploaded_file", filename=saved_name)
        uploaded_name = original_name
        saved_filename = saved_name
        media_type = "video" if extension in {".mp4", ".mov", ".avi", ".mkv", ".m4v"} else "image"

    nasa_image_url = url_for("static", filename="nasa/sst_mur_print.jpg")
    nasa_colorbar_url = url_for("static", filename="nasa/colorbar_cropped.png")

    return render_template(
        "index.html",
        uploaded_url=uploaded_url,
        uploaded_name=uploaded_name,
        saved_filename=saved_filename,
        media_type=media_type,
        nasa_image_url=nasa_image_url,
        nasa_colorbar_url=nasa_colorbar_url
    )

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/api/analyze-region", methods=["POST"])
def api_analyze_region():
    data = request.get_json() or {}
    source = data.get("media_source", "nasa")
    filename = data.get("filename")
    x = data.get("x", 0)
    y = data.get("y", 0)
    width = data.get("width", 100)
    height = data.get("height", 100)

    if source == "upload" and filename:
        img_path = UPLOAD_DIR / secure_filename(filename)
    else:
        img_path = SST_MAP_PATH

    if not img_path.exists():
        return jsonify({"error": f"Image file not found: {img_path.name}"}), 404

    image_bgr = cv2.imread(str(img_path))
    if image_bgr is None:
        return jsonify({"error": "Failed to decode image"}), 400

    results = engine.analyze_roi(image_bgr, x, y, width, height)
    return jsonify(results)

@app.route("/api/sample-pixel", methods=["POST"])
def api_sample_pixel():
    data = request.get_json() or {}
    source = data.get("media_source", "nasa")
    filename = data.get("filename")
    x = data.get("x", 0)
    y = data.get("y", 0)

    if source == "upload" and filename:
        img_path = UPLOAD_DIR / secure_filename(filename)
    else:
        img_path = SST_MAP_PATH

    if not img_path.exists():
        return jsonify({"error": f"Image file not found: {img_path.name}"}), 404

    image_bgr = cv2.imread(str(img_path))
    if image_bgr is None:
        return jsonify({"error": "Failed to decode image"}), 400

    result = engine.estimate_pixel(image_bgr, x, y)
    return jsonify(result)

@app.route("/api/dataset-info", methods=["GET"])
def api_dataset_info():
    return jsonify({
        "dataset_name": "Sea Surface Temperature (SST) — Near Real Time",
        "svs_id": "5101",
        "underlying_dataset": "JPL MUR Sea Surface Temperature Analysis (GHRSST Level 4 MUR Global Foundation SST v4.1)",
        "parameter": "Sea Surface Temperature (SST)",
        "scientific_distinction": "Sea Surface Temperature only. Not ocean currents, not atmospheric weather, and not a weather forecast.",
        "units": "Degrees Celsius (°C)",
        "calibrated_range": "-5°C to +35°C",
        "spatial_resolution": "0.01° (~1 km) global grid, displayed as 1024x512 equirectangular projection",
        "temporal_resolution": "Daily foundation SST analysis",
        "official_svs_url": "https://svs.gsfc.nasa.gov/5101/",
        "podaac_url": "https://podaac.jpl.nasa.gov/dataset/MUR-JPL-L4-GLOB-v4.1",
        "status": "Visualization-based experimental estimate calibrated via OpenCV CIE L*a*b* nearest-gradient lookup table."
    })

@app.errorhandler(413)
def too_large(error):
    flash(f"File is too large. The limit is {MAX_UPLOAD_MB} MB.", "error")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
