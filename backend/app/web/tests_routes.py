import os
import importlib.util
import traceback

from flask import render_template, request, jsonify
from flask_login import login_required

from app.web import web_bp
from app.models.vehicle import Vehicle

# Path to static Test_Programs directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEST_PROGRAMS_DIR = os.path.join(STATIC_DIR, "Test_Programs")


# ---------------------------------------------------------
# Helper: Load a Python test script as a module
# ---------------------------------------------------------
def load_test_module(file_path):
    spec = importlib.util.spec_from_file_location("dynamic_test_module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------
# PAGE ROUTE: /tests   (GET)
# Shows vehicle dropdown + available test files
# ---------------------------------------------------------
@web_bp.route("/tests", methods=["GET"])
@login_required
def tests_page():

    vehicle_id = request.args.get("vehicle_id")
    selected_vehicle = None
    available_tests = []
    test_folder_exists = False

    # All active vehicles for dropdown
    vehicles = Vehicle.query.filter_by(is_active=True).order_by(Vehicle.name).all()

    # If a vehicle is selected, load its test folder
    if vehicle_id:
        selected_vehicle = Vehicle.query.get(vehicle_id)

        if selected_vehicle:
            folder_path = os.path.join(TEST_PROGRAMS_DIR, selected_vehicle.test_folder)
            if os.path.isdir(folder_path):
                test_folder_exists = True
                available_tests = [
                    f for f in os.listdir(folder_path)
                    if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(".py")
                ]

    return render_template(
        "tests.html",
        vehicles=vehicles,
        selected_vehicle=selected_vehicle,
        available_tests=available_tests,
        test_folder_exists=test_folder_exists,
    )


# ---------------------------------------------------------
# API ROUTE: /test   (POST)
# Executes a single test file
# ---------------------------------------------------------
@web_bp.route("/tests", methods=["POST"])
@login_required
def tests():
    data = request.get_json()
    vehicle_id = data.get("vehicle_id")
    test_file = data.get("test_file")

    # Validate vehicle
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    # Build test file path
    folder_path = os.path.join(TEST_PROGRAMS_DIR, vehicle.test_folder)
    file_path = os.path.join(folder_path, test_file)

    if not os.path.isfile(file_path):
        return jsonify({"error": "Test file missing"}), 404

    try:
        # Load test Python module dynamically
        module = load_test_module(file_path)

        # Test function must exist
        if not hasattr(module, "run_test"):
            return jsonify({
                "test": test_file,
                "action": "Missing run_test()",
                "output": "Test file must define run_test()",
                "status": "FAIL"
            })

        # Execute the test
        result = module.run_test()

        return jsonify({
            "test": test_file,
            "action": result.get("action", "Unknown"),
            "output": result.get("output", ""),
            "status": result.get("status", "FAIL")
        })

    except Exception as e:
        return jsonify({
            "test": test_file,
            "action": "Execution error",
            "output": traceback.format_exc(),
            "status": "FAIL"
        })
