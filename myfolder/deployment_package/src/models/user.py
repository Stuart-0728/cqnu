from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """用户模型，包含管理员和普通学生用户"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=True)  # 学号，管理员可为空
    phone = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(100), nullable=True)  # 院系
    major = db.Column(db.String(100), nullable=True)  # 专业
    role = db.Column(db.String(20), default='student')  # 角色: admin, student
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # 活动报名关系
    registrations = db.relationship('Registration', backref='participant', lazy=True)
    
    def __init__(self, username, email, password, full_name, role='student', 
                 student_id=None, phone=None, department=None, major=None):
        self.username = username
        self.email = email
        self.set_password(password)
        self.full_name = full_name
        self.role = role
        self.student_id = student_id
        self.phone = phone
        self.department = department
        self.major = major
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """检查用户是否为管理员"""
        return self.role == 'admin'
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """将用户信息转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'student_id': self.student_id,
            'phone': self.phone,
            'department': self.department,
            'major': self.major,
            'role': self.role,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None
        }
