from src.models.user import db, User
from src.models.activity import Activity, Registration

# 初始化数据库模型
def init_db(app):
    """初始化数据库并创建所有表"""
    with app.app_context():
        db.init_app(app)
        db.create_all()
        
        # 检查是否需要创建初始管理员账户
        if User.query.filter_by(role='admin').first() is None:
            create_default_admin()
        
def create_default_admin():
    """创建默认管理员账户"""
    import os
    default_admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    admin = User(
        username='admin',
        email='admin@cqnu.edu.cn',
        password=default_admin_password,  # 从环境变量获取密码，默认值仅用于开发环境
        full_name='系统管理员',
        role='admin',
        force_password_change=True  # 标记为首次登录需要修改密码
    )
    db.session.add(admin)
    db.session.commit()
