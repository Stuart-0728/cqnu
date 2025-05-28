# association_app/src/models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 导入模型
from src.models.user import User
from src.models.activity import Activity
from src.models.registration import Registration

def init_db(app):
    """仅初始化数据库并创建所有表"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
