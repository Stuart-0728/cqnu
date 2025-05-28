# 文件路径：association_app/src/main.py

import os
import sys
from dotenv import load_dotenv
from flask import Flask
from logging.handlers import RotatingFileHandler
import logging

# —— 环境变量加载 ——  
# 本地有 .env 时加载；线上 Render 上不存在 .env，就忽略
load_dotenv()

# —— 将项目根目录加入 PYTHONPATH，保证 src 包能被找到 ——  
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# —— Flask 应用初始化 ——  
app = Flask(__name__, static_folder='static', template_folder='templates')

# —— 环境 & 安全检查 ——  
ENV = os.getenv('FLASK_ENV', 'production')
IS_PRODUCTION = ENV == 'production'

if IS_PRODUCTION and not os.getenv('SECRET_KEY'):
    raise RuntimeError('生产环境必须设置 SECRET_KEY 环境变量')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = int(os.getenv('SESSION_LIFETIME', 86400))

# —— 日志配置 ——  
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/application.log', maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('应用启动')

# —— 数据库初始化 ——  
from src.models import init_db
init_db(app)

# —— 注册蓝图 ——  
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

# —— 前端路由 ——  
# 所有未匹配 /api 路径的请求都返回 index.html 让 Vue Router 处理
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return app.send_static_file('index.html')

if __name__ == '__main__':
    # 本地开发时使用
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(ENV != 'production'))
