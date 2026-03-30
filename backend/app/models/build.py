from app import db
from datetime import datetime


class Build(db.Model):
    __tablename__ = 'builds'
    
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(20), nullable=False)
    version = db.Column(db.String(20), nullable=False)
    file_path = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    checksum = db.Column(db.String(64))
    release_notes = db.Column(db.Text)
    is_latest = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'platform': self.platform,
            'version': self.version,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'checksum': self.checksum,
            'release_notes': self.release_notes,
            'is_latest': self.is_latest,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Build {self.platform} v{self.version}>'
