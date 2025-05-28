from datetime import datetime
from src.models import db
from src.models.user import User

class Activity(db.Model):
    """活动模型，用于存储社团活动信息"""
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    registration_deadline = db.Column(db.DateTime, nullable=False)
    max_participants = db.Column(db.Integer, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='active')
    image_url = db.Column(db.String(255), nullable=True)

    # 关系
    creator = db.relationship('User', backref='created_activities')
    registrations = db.relationship('Registration', backref='activity', lazy=True, cascade='all, delete-orphan')

    def __init__(self, title, description, location, start_time, end_time,
                 registration_deadline, created_by, max_participants=None, image_url=None):
        self.title = title
        self.description = description
        self.location = location
        self.start_time = start_time
        self.end_time = end_time
        self.registration_deadline = registration_deadline
        self.created_by = created_by
        self.max_participants = max_participants
        self.image_url = image_url

    def is_registration_open(self):
        """检查活动是否开放报名"""
        now = datetime.utcnow()
        return now <= self.registration_deadline and self.status == 'active'

    def is_full(self):
        """检查活动是否已满员"""
        if self.max_participants is None:
            return False
        return len(self.registrations) >= self.max_participants

    def get_registered_count(self):
        """获取已报名人数"""
        return len(self.registrations)

    def to_dict(self):
        """将活动信息转换为字典格式"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'registration_deadline': self.registration_deadline.strftime('%Y-%m-%d %H:%M:%S'),
            'max_participants': self.max_participants,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status,
            'registered_count': self.get_registered_count(),
            'image_url': self.image_url
        }
