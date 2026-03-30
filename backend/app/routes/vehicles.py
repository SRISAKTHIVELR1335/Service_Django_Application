# backend/app/routes/vehicles.py
from flask import Blueprint, jsonify, request
from ..models.vehicle import Vehicle
from ..database import db_session  # adjust to your DB session
from ..utils.vehicle_assets import vehicle_image_url, VEHICLES as MASTER_VEHICLES

vehicles_bp = Blueprint("vehicles", __name__, url_prefix="/api/vehicles")

@vehicles_bp.route("/", methods=["GET"])
def list_vehicles():
    q = db_session.query(Vehicle).all()
    resp = []
    for v in q:
        # if vehicle_key missing, try to compute from name via master file
        vehicle_key = v.vehicle_key
        if not vehicle_key:
            # attempt to match using name
            key_guess = v.name.upper().replace(" ", "_")
            if key_guess in MASTER_VEHICLES:
                vehicle_key = key_guess
        # include image_url using utility
        image = vehicle_image_url(vehicle_key) if vehicle_key else vehicle_image_url(None)
        item = v.to_dict(include_image_url=True, image_url_func=vehicle_image_url)
        # override with url we computed
        item["image_url"] = image
        resp.append(item)
    return jsonify(resp), 200
