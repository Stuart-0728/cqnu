from flask_sqlalchemy import SQLAlchemy

# 全局 SQLAlchemy 实例

db = SQLAlchemy()

# 导入模型类，确保被 SQLAlchemy 识别
from src.models.user import User
from src.models.activity import Activity
from src.models.registration import Registration


def init_db(app):
    """初始化数据库，创建所有表"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
