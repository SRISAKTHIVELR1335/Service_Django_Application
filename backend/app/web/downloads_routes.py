from flask import render_template
from flask_login import login_required

from app.web import web_bp
from app.models.build import Build
from app.models.bundle import Bundle
from app.models.vehicle import Vehicle


@web_bp.route("/downloads")
@login_required
def downloads():
    """
    Downloads page.

    - Shows latest Windows EXE and Android APK builds (if present).
    - Shows latest active bundle per vehicle.
    - Shows helpful links for CAN driver installations.
    """
    # Latest Windows EXE
    windows_build = (
        Build.query.filter_by(
            platform="windows",
            is_latest=True,
            is_active=True,
        )
        .order_by(Build.created_at.desc())
        .first()
    )

    # Latest Android APK
    android_build = (
        Build.query.filter_by(
            platform="android",
            is_latest=True,
            is_active=True,
        )
        .order_by(Build.created_at.desc())
        .first()
    )

    # Latest active bundle per active vehicle
    vehicles = (
        Vehicle.query.filter_by(is_active=True)
        .order_by(Vehicle.name)
        .all()
    )

    bundles = []
    for vehicle in vehicles:
        latest_bundle = (
            Bundle.query.filter_by(
                vehicle_id=vehicle.id,
                is_active=True,
            )
            .order_by(Bundle.created_at.desc())
            .first()
        )
        if latest_bundle:
            bundles.append(latest_bundle)

    # CAN driver download info for technicians
    can_drivers = [
        {
            "name": "PCAN",
            "vendor": "PEAK-System",
            "url": "https://www.peak-system.com/PCAN-USB.199.0.html",
            "description": "PEAK CAN USB Interface Driver (PCAN-USB).",
        },
        {
            "name": "Kvaser",
            "vendor": "Kvaser",
            "url": "https://www.kvaser.com/downloads/",
            "description": "Kvaser CAN Interface Drivers & SDK.",
        },
        {
            "name": "Vector",
            "vendor": "Vector Informatik",
            "url": "https://www.vector.com/int/en/products/products-a-z/software/xl-driver-library/",
            "description": "Vector XL Driver Library for Vector CAN hardware.",
        },
    ]

    return render_template(
        "downloads.html",
        windows_build=windows_build,
        android_build=android_build,
        bundles=bundles,
        can_drivers=can_drivers,
    )
