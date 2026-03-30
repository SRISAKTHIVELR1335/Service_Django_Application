import os,sys
os.environ["DATABASE_URL"] = "mysql+pymysql://nirix_user:journey%40123%21@127.0.0.1:3306/nirix_diagnostics"

import threading
import webbrowser
import time
from sqlalchemy import text

# -------------------------------------------------------
# FIX PYTHONPATH SO BACKEND & ASSETS CAN BE IMPORTED
# -------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))          # backend/
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))   # Nirix_Diagnostics/
sys.path.insert(0, PROJECT_ROOT)

# Now imports work
from app import create_app
from app.database import db_session
from sqlalchemy.exc import OperationalError, ProgrammingError

# Create Flask application
app = create_app()


# -------------------------------------------------------
# UTILITIES
# -------------------------------------------------------
def safe_table_exists(table_name):
    """Check if a table exists safely."""
    try:
        db_session.execute(text(f"SELECT 1 FROM {table_name} LIMIT 1"))
        return True
    except Exception:
        return False


def safe_column_exists(table_name, column_name):
    """Check if a column exists in a table safely."""
    try:
        result = db_session.execute(
            text(f"SHOW COLUMNS FROM {table_name} LIKE :col"),
            {"col": column_name}
        ).fetchone()
        return result is not None
    except Exception:
        return False


# -------------------------------------------------------
# VEHICLE SEEDING
# -------------------------------------------------------
def seed_database():
    if not safe_table_exists("vehicles"):
        print("[SEED] Vehicles table does not exist — skipping vehicle seed.")
        return

    # minimum required columns
    if not safe_column_exists("vehicles", "name"):
        print("[SEED] 'vehicles' table missing required columns — skipping seed.")
        return

    try:
        count = db_session.execute(text("SELECT COUNT(*) FROM vehicles")).scalar()
    except Exception as e:
        print("[SEED] Error reading vehicles table:", e)
        return

    print(f"[SEED] Vehicles count = {count}")

    if count == 0:
        print("[SEED] Populating vehicles from vehicle_models.py...")

        # Import global mapping
        from app.static.vehicle_models import VEHICLES

        for key, meta in VEHICLES.items():
            db_session.execute(
                text("""
                    INSERT INTO vehicles
                    (name, vehicle_key, category, vin_pattern, image_filename, test_folder)
                    VALUES (:name, :vk, :cat, :vp, :img, :tf)
                """),
                {
                    "name": meta.get("name"),
                    "vk": key,
                    "cat": meta.get("category"),
                    "vp": meta.get("vin_pattern"),
                    "img": meta.get("image"),
                    "tf": meta.get("test_folder"),
                }
            )
        db_session.commit()
        print("[SEED] Vehicle seeding complete.")
    else:
        print("[SEED] Vehicles already exist — skipping insert.")


def seed_admin_user():
    from app.models.role import Role
    from app.models.user import User
    from app.database import db_session
    from flask_bcrypt import Bcrypt
    from sqlalchemy.exc import IntegrityError

    bcrypt = Bcrypt()

    # ----- Ensure required roles exist (get-or-create) -----
    required_roles = ["Admin", "User", "Viewer"]
    for role_name in required_roles:
        role = db_session.query(Role).filter_by(name=role_name).first()
        if not role:
            db_session.add(Role(name=role_name))
            print(f"[SEED] Created role: {role_name}")

    # Try to commit role inserts; handle race duplicates gracefully
    try:
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
        # Another process may have inserted a role concurrently.
        # Ensure each role exists now.
        for role_name in required_roles:
            if not db_session.query(Role).filter_by(name=role_name).first():
                try:
                    db_session.add(Role(name=role_name))
                    db_session.commit()
                    print(f"[SEED] Created role after retry: {role_name}")
                except IntegrityError:
                    db_session.rollback()
                    print(f"[SEED] Role already exists after retry: {role_name}")

    # ----- Get admin role -----
    admin_role = db_session.query(Role).filter_by(name="admin").first()
    if not admin_role:
        print("[SEED] Admin role not found — skipping admin user creation.")
        return

    # ----- Check if admin exists -----
    admin_user = db_session.query(User).filter_by(email="admin@nirix.com").first()
    if admin_user:
        print("[SEED] Admin user already exists.")
        return

    print("[SEED] Creating admin user with 4-digit PIN...")

    # ----- Create admin user -----
    new_admin = User(
        email="admin@nirix.com",
        first_name="Admin",
        last_name="User",
        role_id=admin_role.id,
        is_active=1,
        is_approved=1,
        theme_preference="light"
    )

    # ----- Set 4-digit PIN -----
    pin = "1234"   # CHANGE THIS IF YOU WANT A DIFFERENT PIN
    hashed_pin = bcrypt.generate_password_hash(pin).decode("utf-8")
    new_admin.password_hash = hashed_pin

    db_session.add(new_admin)
    try:
        db_session.commit()
        print("[SEED] Admin user created successfully with PIN:", pin)
    except IntegrityError as e:
        db_session.rollback()
        print("[SEED] Failed to create admin user (IntegrityError):", e)


# -------------------------------------------------------
# AUTO-OPEN WEB BROWSER
# -------------------------------------------------------
def open_browser():
    """Opens the dashboard automatically after Flask starts."""
    time.sleep(1.5)
    try:
        webbrowser.open("http://localhost:5000")
        print("[INFO] Browser opened automatically.")
    except Exception as e:
        print("[WARN] Could not open browser:", e)


# -------------------------------------------------------
# MAIN ENTRY POINT
# -------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        seed_database()
        seed_admin_user()

    # Only open the browser in the actual Flask process (prevents double-open)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Thread(target=open_browser, daemon=True).start()

    app.run(host="0.0.0.0", port=5000, debug=True)

