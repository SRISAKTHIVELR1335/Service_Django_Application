from datetime import datetime

from flask_login import UserMixin

from app import db, bcrypt


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Login info
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Personal info
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    # Role (FK to roles.id) – relationship comes from Role.users backref="role"
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)

    # Status flags
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)

    # UI preferences
    theme_preference = db.Column(db.String(20), default="light")

    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def password(self):
        """Prevent direct reading of the password."""
        raise AttributeError("Password attribute is not readable.")

    @password.setter
    def password(self, raw_password: str):
        """Hash and set the password."""
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode(
            "utf-8"
        )

    def check_password(self, raw_password: str) -> bool:
        """Check a raw password against the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    def get_id(self) -> str:
        """Return ID as a string for Flask-Login."""
        return str(self.id)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def to_dict(self) -> dict:
        """Safe representation of user (no password)."""
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role.name if hasattr(self, "role") and self.role else None,
            "is_active": self.is_active,
            "is_approved": self.is_approved,
            "theme_preference": self.theme_preference,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<User {self.email}>"
