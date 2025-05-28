from src.models.user import db, User
from src.models.activity import Activity
from src.models.registration import Registration

def init_db(app):
    """初始化数据库"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        create_default_admin()

def create_default_admin():
    """创建默认管理员账户"""
    import os
    default_admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    admin = User(
        username='admin',
        email='admin@cqnu.edu.cn',
        password=default_admin_password,  # 从环境变量获取密码，默认值便于开发环境
        full_name='系统管理员',
        role='admin'
        # 移除 force_password_change=True 参数，因为User模型不接受此参数
    )
    db.session.add(admin)
    db.session.commit()
