import os
import sys
from dotenv import load_dotenv
from flask import Flask
from logging.handlers import RotatingFileHandler
import logging

# 加载环境变量
load_dotenv()
# 确保能导入 src 包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, static_folder='static', template_folder='templates')

# 环境配置
ENV = os.getenv('FLASK_ENV', 'production')
IS_PRODUCTION = ENV == 'production'
if IS_PRODUCTION and not os.getenv('SECRET_KEY'):
    raise RuntimeError('生产环境必须设置 SECRET_KEY')

app.config.update({
    'SECRET_KEY': os.getenv('SECRET_KEY'),
    'SQLALCHEMY_DATABASE_URI': os.getenv('DATABASE_URL'),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SESSION_PERMANENT': True,
    'PERMANENT_SESSION_LIFETIME': int(os.getenv('SESSION_LIFETIME', 86400))
})

# 日志配置
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    fh = RotatingFileHandler('logs/app.log', maxBytes=10*1024*1024, backupCount=5)
    fh.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    fh.setLevel(logging.INFO)
    app.logger.addHandler(fh)
    app.logger.setLevel(logging.INFO)
    app.logger.info('应用启动')

# 初始化数据库
from src.models import init_db, db
from src.models.user import User
init_db(app)

# 首次请求时创建管理员
@app.before_first_request
def ensure_admin():
    from os import getenv
    pwd = getenv('ADMIN_PASSWORD', 'admin123')
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@cqnu.edu.cn',
            password=pwd,
            full_name='系统管理员',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        app.logger.info('管理员账号 [admin] 已创建')

# 注册路由蓝图
from src.routes.auth import auth_bp
from src.routes.activity import activity_bp
from src.routes.registration import registration_bp
from src.routes.dashboard import dashboard_bp
from src.routes.upload import upload_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(activity_bp, url_prefix='/api/activity')
app.register_blueprint(registration_bp, url_prefix='/api/registration')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(upload_bp, url_prefix='/api/upload')

# 前端路由回退
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return app.send_static_file('index.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(ENV!='production'))
