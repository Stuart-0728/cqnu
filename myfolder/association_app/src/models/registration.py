# 文件路径：association_app/src/models/registration.py

from datetime import datetime
from src.models.user import db, User
from src.models.activity import Activity

class Registration(db.Model):
    __tablename__ = 'registration'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey(Activity.id), nullable=False)
    status = db.Column(db.String(20), default='pending')         # 报名状态：pending/approved/rejected
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # 报名时间

    # ORM 关系，方便查询
    user = db.relationship('User', backref='registrations')
    activity = db.relationship('Activity', backref='registrations')
