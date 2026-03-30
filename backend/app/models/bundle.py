from app import db
from datetime import datetime


class Bundle(db.Model):
    __tablename__ = 'bundles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(20), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    file_path = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    checksum = db.Column(db.String(64))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'vehicle_id': self.vehicle_id,
            'vehicle_name': self.vehicle.name if self.vehicle else None,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'checksum': self.checksum,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Bundle {self.name} v{self.version}>'
