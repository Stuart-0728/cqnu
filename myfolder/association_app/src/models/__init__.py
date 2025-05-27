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
    admin = User(
        username='admin',
        email='admin@cqnu.edu.cn',
        password='admin123',  # 初始密码，应提示管理员首次登录后修改
        full_name='系统管理员',
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()
