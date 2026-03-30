from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    vin = Column(String(64), nullable=True)

    vehicle_key = Column(String(128), index=True, nullable=True)
    category = Column(String(128), nullable=True)
    vin_pattern = Column(String(255), nullable=True)
    image_filename = Column(String(255), nullable=True)
    test_folder = Column(String(255), nullable=True)

    is_active = Column(Integer, default=1)  # <-- THE FIX

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "vin": self.vin,
            "vehicle_key": self.vehicle_key,
            "category": self.category,
            "vin_pattern": self.vin_pattern,
            "image_filename": self.image_filename,
            "test_folder": self.test_folder,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
