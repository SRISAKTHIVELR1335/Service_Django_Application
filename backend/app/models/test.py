from app import db
from datetime import datetime


class Test(db.Model):
    __tablename__ = 'tests'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    test_type = db.Column(db.String(20), nullable=False)
    module_name = db.Column(db.String(100), nullable=False)
    function_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    requires_mac = db.Column(db.Boolean, default=False)
    version = db.Column(db.String(20), default='1.0.0')
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    logs = db.relationship('Log', backref='test', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'test_type': self.test_type,
            'module_name': self.module_name,
            'function_name': self.function_name,
            'description': self.description,
            'requires_mac': self.requires_mac,
            'version': self.version,
            'vehicle_id': self.vehicle_id,
            'vehicle_name': self.vehicle.name if self.vehicle else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Test {self.name}>'
