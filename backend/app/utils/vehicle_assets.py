# backend/app/utils/vehicle_assets.py
import os
from flask import current_app, url_for, send_from_directory
from werkzeug.utils import secure_filename

# Import master VEHICLES mapping. Adjust import path if you placed vehicle_models somewhere else.
try:
    # First try global assets path
    from ...assets.vehicle_models import VEHICLES, DEFAULT_IMAGE_FILENAME, get_assets_paths
except Exception:
    # Fallback if installed differently
    from assets.vehicle_models import VEHICLES, DEFAULT_IMAGE_FILENAME, get_assets_paths

ASSETS = get_assets_paths()
ASSETS_DIR = ASSETS.get("assets_dir")
TEST_PROGRAMS_DIR = ASSETS.get("test_programs_dir")

def ensure_absolute(filepath):
    return os.path.abspath(filepath)

def vehicle_image_path(vehicle_key):
    """Return absolute filesystem path for the image for vehicle_key. Fallback to default."""
    if not vehicle_key:
        return os.path.join(ASSETS_DIR, DEFAULT_IMAGE_FILENAME)
    meta = VEHICLES.get(vehicle_key)
    if not meta:
        # try to find by loose key
        meta = VEHICLES.get(vehicle_key.upper().replace(" ", "_"))
    if meta:
        image_name = meta.get("image") or DEFAULT_IMAGE_FILENAME
    else:
        image_name = DEFAULT_IMAGE_FILENAME
    image_path = os.path.join(ASSETS_DIR, secure_filename(image_name))
    if os.path.exists(image_path):
        return image_path
    # fallback
    default_path = os.path.join(ASSETS_DIR, DEFAULT_IMAGE_FILENAME)
    return default_path if os.path.exists(default_path) else image_path

def vehicle_image_url(vehicle_key):
    """Return a URL that the frontend can use to fetch the image.
    This assumes the backend has a static route '/assets/vehicles/<filename>' mapped to ASSETS_DIR.
    """
    meta = VEHICLES.get(vehicle_key)
    image_name = (meta.get("image") if meta else DEFAULT_IMAGE_FILENAME)
    # Use a static endpoint; ensure the asssets route exists in your Flask app
    return url_for("assets.serve_vehicle_image", filename=image_name, _external=False)

def test_program_folder(vehicle_key):
    """Return absolute path to the test program folder for given vehicle_key"""
    meta = VEHICLES.get(vehicle_key)
    if meta:
        folder = meta.get("test_folder")
        return os.path.join(TEST_PROGRAMS_DIR, secure_filename(folder))
    return None
