from pathlib import Path  # Import Path to build safe file locations
from flask import Flask, render_template, request, redirect, url_for, flash  # Import Flask tools for pages, uploads and messages
from werkzeug.utils import secure_filename  # Import secure_filename to clean uploaded filenames
import uuid  # Import uuid to create unique upload names

BASE_DIR = Path(__file__).resolve().parent  # Find the folder containing this application
UPLOAD_DIR = BASE_DIR / "uploads"  # Store uploaded media in an uploads folder
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff", "mp4", "mov", "avi", "mkv", "m4v"}  # List supported image and video extensions
MAX_UPLOAD_MB = 250  # Set the maximum upload size in megabytes

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Create the uploads folder if it does not exist

app = Flask(__name__)  # Create the Flask web application
app.secret_key = "change-this-local-development-key"  # Set a development secret for flash messages
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)  # Tell Flask where uploaded files should be stored
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024  # Limit upload size to protect the local app

def allowed_file(filename):  # Check whether the uploaded file has an allowed extension
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS  # Return True only for supported extensions

@app.route("/", methods=["GET", "POST"])  # Display the dashboard and accept uploads
def index():  # Handle the main dashboard page
    uploaded_url = None  # Start with no uploaded media
    uploaded_name = None  # Start with no uploaded filename
    media_type = None  # Start with no detected media type

    if request.method == "POST":  # Run this block when the user submits the upload form
        media = request.files.get("media")  # Read the uploaded file from the form

        if media is None or media.filename == "":  # Check whether the user selected a file
            flash("Choose an image or video before uploading.", "error")  # Show a helpful error message
            return redirect(url_for("index"))  # Return to the dashboard

        if not allowed_file(media.filename):  # Reject file types outside the allow-list
            flash("That file type is not supported. Choose an image or video.", "error")  # Explain the file type problem
            return redirect(url_for("index"))  # Return to the dashboard

        original_name = secure_filename(media.filename)  # Remove unsafe characters from the filename
        extension = Path(original_name).suffix.lower()  # Read the safe file extension
        saved_name = f"{uuid.uuid4().hex}{extension}"  # Create a unique name to avoid overwriting another upload
        save_path = UPLOAD_DIR / saved_name  # Build the destination path inside the uploads folder
        media.save(save_path)  # Save the uploaded file to disk

        uploaded_url = url_for("uploaded_file", filename=saved_name)  # Build a browser URL for the uploaded file
        uploaded_name = original_name  # Keep the cleaned original name for display
        media_type = "video" if extension in {".mp4", ".mov", ".avi", ".mkv", ".m4v"} else "image"  # Detect whether the file is a video or image

    return render_template("index.html", uploaded_url=uploaded_url, uploaded_name=uploaded_name, media_type=media_type)  # Render the dashboard with upload details

@app.route("/uploads/<path:filename>")  # Serve files from the dedicated upload folder
def uploaded_file(filename):  # Return the uploaded file to the browser
    from flask import send_from_directory  # Import the safe directory-serving helper
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)  # Serve only from the configured uploads directory

@app.errorhandler(413)  # Handle files that exceed the configured upload size
def too_large(error):  # Display a friendly upload-size error
    flash(f"File is too large. The limit is {MAX_UPLOAD_MB} MB.", "error")  # Explain the upload limit
    return redirect(url_for("index"))  # Return to the dashboard

if __name__ == "__main__":  # Check whether this file is being run directly
    app.run(debug=True)  # Start the local development server
