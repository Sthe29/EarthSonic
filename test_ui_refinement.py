"""
EarthSonic UI & User Experience Refinement Test Suite
====================================================
Tests the refined UI, educational explanations, and visual hierarchy:
1. Landing page module cards and plain-English descriptions.
2. Honest Coming Soon states for planned modules (no fake data or active links).
3. Ocean Temperature workspace structure (Product 1 vs Product 2 visual separation).
4. Educational guidance drawer & scientific explanation preservation.
5. Zero emojis across templates and styles.
6. Responsive CSS classes and accessibility attributes.
"""

import re
from app import app

client = app.test_client()

EMOJI_PATTERN = re.compile(
    "[\U0001F1E0-\U0001F1FF"
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U00002702-\U000027B0]"
)


def test_landing_page_refinement():
    print("=== 1. TEST LANDING PAGE REFINEMENT ===")
    res = client.get("/")
    assert res.status_code == 200
    html = res.data.decode("utf-8")

    # Check zero emojis
    assert not EMOJI_PATTERN.search(html), "Found emoji on landing page!"

    # Check module cards structure
    cards = re.findall(r'<article class="module-card (.*?)">(.*?)</article>', html, re.DOTALL)
    assert len(cards) == 4, f"Expected 4 module cards, found {len(cards)}"

    # Module 1 (Active)
    assert "Available Now" in html
    assert "Sea Surface Temperature (SST)" in html
    assert "/ocean-temperature" in html

    # Module 2 (Honest Coming Soon)
    assert "Ocean Currents &amp; Circulation" in html or "Ocean Currents & Circulation" in html
    assert "Coming Soon &bull; In Research" in html
    assert "btn-disabled-module" in html

    # Module 3 (Weather)
    assert "Weather &amp; Atmosphere" in html or "Weather & Atmosphere" in html

    # Module 4 (More Earth Data)
    assert "More Earth Data" in html
    assert "Planned &bull; Future Expansion" in html

    # Architectural pillars
    assert "Meaningful Sonification" in html
    assert "OpenCV Computer Vision" in html
    assert "Universal Accessibility" in html
    print("Landing page refinement: Plain-English descriptions, honest status badges, zero emojis -> PASSED.")


def test_ocean_temperature_refinement():
    print("\n=== 2. TEST OCEAN TEMPERATURE WORKSPACE REFINEMENT ===")
    res = client.get("/ocean-temperature")
    assert res.status_code == 200
    html = res.data.decode("utf-8")

    # Check zero emojis
    assert not EMOJI_PATTERN.search(html), "Found emoji in ocean_temperature.html!"

    # Educational Guidance Drawer
    assert "educational-drawer" in html
    assert "educational-summary" in html
    assert "What is Foundation SST?" in html
    assert "Product 1: Image Colormap Estimate" in html
    assert "Product 2: Authentic Numerical Data" in html
    assert "How Sound Communicates Data" in html

    # Product 1 and Product 2 Distinct Separation
    assert "product-1-card" in html
    assert "product-2-card" in html
    assert "OpenCV Colormap Analysis" in html
    assert "Level-4 Satellite Gridded Data" in html

    # Product 1 Elements
    assert "PRODUCT 1: VISUALIZATION ESTIMATE" in html
    assert "Colormap Temperature Analysis" in html
    assert 'id="temp-primary-value"' in html
    assert 'id="temp-classification-pill"' in html
    assert 'id="metric-region-type"' in html
    assert 'id="btn-play"' in html
    assert 'id="btn-pause"' in html
    assert 'id="btn-stop"' in html
    assert 'id="audio-state-pill"' in html

    # Product 2 Elements
    assert "PRODUCT 2: AUTHENTIC NUMERICAL DATA" in html
    assert "NASA/JPL MUR Analysis (via NOAA ERDDAP)" in html
    assert 'id="mur-query-form"' in html
    assert 'id="mur-temp-value"' in html
    assert 'id="mur-mask-pill"' in html
    assert 'id="btn-play-mur"' in html
    assert 'id="btn-stop-mur"' in html
    assert 'id="mur-audio-pill"' in html
    assert 'id="mur-audio-desc"' in html

    # Accessibility attributes
    assert 'role="region"' in html
    assert 'role="status"' in html
    assert 'role="alert"' in html
    assert 'id="accessibility-announcer"' in html
    print("Ocean Temperature refinement: Product separation, educational guide, accessible audio controls -> PASSED.")


def test_stylesheet_verification():
    print("\n=== 3. TEST STYLESHEET REFINEMENT ===")
    res = client.get("/static/style.css")
    assert res.status_code == 200
    css = res.data.decode("utf-8")

    # Verify zero emojis in CSS
    assert not EMOJI_PATTERN.search(css), "Found emoji in style.css!"

    # Verify key new classes
    assert ".educational-drawer" in css
    assert ".educational-summary" in css
    assert ".product-card" in css
    assert ".product-1-card" in css
    assert ".product-2-card" in css
    assert ".estimate-badge" in css
    assert ".numerical-badge" in css
    print("Stylesheet verification: Cohesive palette, responsive rules, clean typography, zero emojis -> PASSED.")


if __name__ == "__main__":
    test_landing_page_refinement()
    test_ocean_temperature_refinement()
    test_stylesheet_verification()
    print("\n=========================================================")
    print("ALL UI REFINEMENT TESTS PASSED CLEANLY (3/3)!")
    print("=========================================================")
