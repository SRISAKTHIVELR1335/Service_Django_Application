import os

from app import create_app, db
from app.models.build import Build


def main():
    # Set DATABASE_URL if not already set
    os.environ.setdefault(
        "DATABASE_URL",
        "mysql+pymysql://nirix_user:YourPasswordHere@127.0.0.1:3306/nirix_diagnostics",
    )

    app = create_app()
    with app.app_context():
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        builds_dir = os.path.join(base_dir, "builds")

        win_path = os.path.join(builds_dir, "Nirix_Windows_v1.0.0.exe")
        android_path = os.path.join(builds_dir, "Nirix_Android_v1.0.0.apk")

        print("Windows path:", win_path, "exists?", os.path.exists(win_path))
        print("Android path:", android_path, "exists?", os.path.exists(android_path))

        if not os.path.exists(win_path) or not os.path.exists(android_path):
            print("ERROR: One or both build files do not exist. Aborting.")
            return

        win_build = Build(
            platform="windows",
            version="1.0.0",
            file_path=win_path,
            file_size=os.path.getsize(win_path),
            checksum=None,
            release_notes="First internal Windows diagnostic client.",
            is_latest=True,
            is_active=True,
        )

        android_build = Build(
            platform="android",
            version="1.0.0",
            file_path=android_path,
            file_size=os.path.getsize(android_path),
            checksum=None,
            release_notes="First internal Android support app.",
            is_latest=True,
            is_active=True,
        )

        db.session.add(win_build)
        db.session.add(android_build)
        db.session.commit()
        print("Seeded builds:", win_build.id, android_build.id)


if __name__ == "__main__":
    main()
