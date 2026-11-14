import io
import re
from app import app

client = app.test_client()

print("=== 1. TEST LANDING PAGE (GET /) ===")
res = client.get("/")
assert res.status_code == 200, f"Expected 200, got {res.status_code}"
assert b"Listen to Our Changing Planet" in res.data
assert b"Sea Surface Temperature (SST)" in res.data
assert b"Ocean Currents" in res.data
assert b"Weather" in res.data
assert b"More Earth Data" in res.data
assert b"Available Now" in res.data
assert b"Coming Soon" in res.data
assert b"/ocean-temperature" in res.data
print("Landing page loads and displays all 4 module cards correctly.")

print("=== 2. TEST COMING SOON CARDS (No broken links) ===")
html = res.data.decode("utf-8")
cards = re.findall(r'<article class="module-card (.*?)">(.*?)</article>', html, re.DOTALL)
assert len(cards) == 4, f"Expected 4 module cards, found {len(cards)}"
for class_name, card_body in cards:
    if "coming-soon" in class_name or "planned" in class_name:
        assert "<a href=" not in card_body, "Found active link in coming-soon or planned card!"
        assert "btn-disabled-module" in card_body
print("Coming Soon / Planned cards verified: zero broken links, clean disabled states.")

print("=== 3. TEST OCEAN TEMPERATURE WORKSPACE (GET /ocean-temperature) ===")
res_sst = client.get("/ocean-temperature")
assert res_sst.status_code == 200
assert b"Global Ocean Temperature Map" in res_sst.data
assert b"All Modules" in res_sst.data
assert b"btn-play" in res_sst.data
assert b"Calibrated Temperature Legend" in res_sst.data
print("Ocean Temperature workspace loads with all scientific controls.")

print("=== 4. TEST BACK LINK TO LANDING PAGE ===")
sst_html = res_sst.data.decode("utf-8")
match = re.search(r'class="nav-back-button"\s+href="(.*?)"', sst_html)
assert match is not None
back_href = match.group(1)
assert back_href == "/"
back_res = client.get(back_href)
assert back_res.status_code == 200
assert b"Listen to Our Changing Planet" in back_res.data
print("Return navigation to landing page verified.")

print("=== 5. TEST API ENDPOINTS (OpenCV backend functionality) ===")
roi_res = client.post("/api/analyze-region", json={
    "media_source": "nasa",
    "x": 150, "y": 210, "width": 120, "height": 90
})
assert roi_res.status_code == 200
roi_data = roi_res.get_json()
assert roi_data["ocean_coverage_pct"] > 95.0
assert roi_data["mean_temp_c"] > 25.0
print(f"ROI Analysis: {roi_data['mean_temp_c']}°C, Ocean Coverage: {roi_data['ocean_coverage_pct']}% -> PASSED")

pixel_res = client.post("/api/sample-pixel", json={
    "media_source": "nasa",
    "x": 420, "y": 160
})
assert pixel_res.status_code == 200
pixel_data = pixel_res.get_json()
assert pixel_data["is_ocean"] is True
assert 20.0 < pixel_data["estimated_temp_c"] < 26.0
print(f"Pixel Analysis: {pixel_data['estimated_temp_c']}°C ({pixel_data['classification']}) -> PASSED")

print("=== 6. TEST UPLOAD WORKFLOW ON /ocean-temperature ===")
fake_img = io.BytesIO(b"dummy-image-bytes-for-upload")
up_res = client.post("/ocean-temperature", data={"media": (fake_img, "sst_custom.png")}, content_type="multipart/form-data")
assert up_res.status_code == 200
assert b"sst_custom.png" in up_res.data
print("Upload workflow on /ocean-temperature -> PASSED")

print("=== ALL 6 TESTS PASSED CLEANLY! ===")
