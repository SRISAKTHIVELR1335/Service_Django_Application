import os
from flask import Blueprint, send_from_directory, abort, current_app

assets_bp = Blueprint("assets", __name__, url_prefix="/assets")

# Static directory — all images + test programs live here now
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))

def secure_path(directory, filename):
    requested = os.path.abspath(os.path.join(directory, filename))
    if not requested.startswith(directory):
        abort(403)
    return requested

@assets_bp.route("/<path:filename>")
def serve_static_asset(filename):
    """
    Serve any file inside backend/app/static through:
    /assets/<filename>
    """
    full_path = secure_path(STATIC_DIR, filename)

    if not os.path.exists(full_path):
        abort(404)

    directory = os.path.dirname(full_path)
    file_only = os.path.basename(full_path)

    return send_from_directory(directory, file_only)
