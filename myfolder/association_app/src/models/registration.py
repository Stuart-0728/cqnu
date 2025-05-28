from datetime import datetime
from src.models import db

class Registration(db.Model):
    """活动报名模型，记录用户报名活动的信息"""
    __tablename__ = 'registrations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    registration_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='registered')
    notes = db.Column(db.Text, nullable=True)

    def __init__(self, user_id, activity_id, notes=None):
        self.user_id = user_id
        self.activity_id = activity_id
        self.notes = notes

    def to_dict(self):
        """将报名信息转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_id': self.activity_id,
            'registration_time': self.registration_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status,
            'notes': self.notes
        }
