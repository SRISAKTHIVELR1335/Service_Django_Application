import os

from flask import request, jsonify, send_file
from app.api import api_bp
from app import db
from app.models.build import Build
from app.api.auth import token_required


@api_bp.route("/versions", methods=["GET"])
@token_required
def get_versions(current_user):
    """
    List active builds, optionally filtered by platform.
    Example: GET /api/versions?platform=windows
    """
    platform = request.args.get("platform")

    query = Build.query.filter_by(is_active=True)

    if platform:
        query = query.filter_by(platform=platform)

    builds = query.order_by(Build.created_at.desc()).all()

    return jsonify({"builds": [b.to_dict() for b in builds]})


@api_bp.route("/versions/latest", methods=["GET"])
@token_required
def get_latest_version(current_user):
    """
    Get latest build for a platform.
    Example: GET /api/versions/latest?platform=windows
    """
    platform = request.args.get("platform")
    if not platform:
        return jsonify({"error": "platform query parameter is required"}), 400

    latest = (
        Build.query.filter_by(
            platform=platform,
            is_active=True,
            is_latest=True,
        )
        .order_by(Build.created_at.desc())
        .first()
    )

    if not latest:
        return jsonify({"error": "No build found for this platform"}), 404

    return jsonify({"build": latest.to_dict()})


@api_bp.route("/versions/download/<int:build_id>", methods=["GET"])
def download_build(build_id: int):
    """
    Download a specific build (EXE or APK).

    Used by:
    - Web Downloads page (EXE / APK buttons)
    - Potentially by clients for auto-update.
    """
    build = Build.query.get_or_404(build_id)

    if not build.file_path or not os.path.exists(build.file_path):
        return jsonify({"error": "Build file not found on server"}), 404

    if build.platform == "windows":
        ext = ".exe"
    elif build.platform == "android":
        ext = ".apk"
    else:
        ext = ""

    download_name = f"Nirix_{build.platform}_v{build.version}{ext}"

    return send_file(
        build.file_path,
        as_attachment=True,
        download_name=download_name,
    )


@api_bp.route("/versions", methods=["POST"])
@token_required
def create_build(current_user):
    """
    Create a new build entry.
    Typically used by internal tooling / admin only.
    """
    # Optional: allow only admins
    if current_user.role.name != "Admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json() or {}

    required = ["platform", "version", "file_path"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    build = Build(
        platform=data["platform"],
        version=data["version"],
        file_path=data["file_path"],
        file_size=data.get("file_size"),
        checksum=data.get("checksum"),
        release_notes=data.get("release_notes"),
        is_latest=data.get("is_latest", False),
        is_active=data.get("is_active", True),
    )

    db.session.add(build)

    # If marked as latest, clear others for this platform
    if build.is_latest:
        (
            Build.query.filter(
                Build.platform == build.platform,
                Build.id != build.id,
            )
            .update({"is_latest": False})
        )

    db.session.commit()

    return jsonify(
        {
            "message": "Build created successfully",
            "build": build.to_dict(),
        }
    ), 201
