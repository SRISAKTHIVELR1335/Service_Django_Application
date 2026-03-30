from app import db
from datetime import datetime


class Log(db.Model):
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    vin = db.Column(db.String(50))
    status = db.Column(db.String(20), nullable=False)
    log_text = db.Column(db.Text)
    client_version = db.Column(db.String(20))
    client_platform = db.Column(db.String(20))
    execution_time = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_email': self.user.email if self.user else None,
            'vehicle_id': self.vehicle_id,
            'vehicle_name': self.vehicle.name if self.vehicle else None,
            'test_id': self.test_id,
            'test_name': self.test.name if self.test else None,
            'vin': self.vin,
            'status': self.status,
            'log_text': self.log_text,
            'client_version': self.client_version,
            'client_platform': self.client_platform,
            'execution_time': self.execution_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Log {self.id} - {self.status}>'
