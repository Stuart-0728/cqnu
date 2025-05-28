# 文件路径：association_app/src/models/__init__.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 导入模型
from src.models.user import User
from src.models.activity import Activity
from src.models.registration import Registration

def create_default_admin():
    """创建默认管理员"""
    import os
    from src.models.user import User as U
    from src.models.user import db as _db

    default_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    if not U.query.filter_by(username='admin').first():
        admin = U(
            username='admin',
            email='admin@cqnu.edu.cn',
            password=default_password,
            full_name='系统管理员',
            role='admin'
        )
        _db.session.add(admin)
        _db.session.commit()

def init_db(app):
    """初始化数据库并创建表和默认管理员"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        create_default_admin()
