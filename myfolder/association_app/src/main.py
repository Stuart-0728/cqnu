from flask import Flask, session, g, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 环境配置
ENV = os.getenv('FLASK_ENV', 'development')
IS_PRODUCTION = ENV == 'production'

# 创建Flask应用
app = Flask(__name__)

# 安全配置 - 生产环境必须设置环境变量
if IS_PRODUCTION and not os.getenv('SECRET_KEY'):
    raise RuntimeError('生产环境必须设置SECRET_KEY环境变量')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key_not_for_production')

# 配置数据库为SQLite（免费部署用）
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,  # 连接健康检查
    'pool_recycle': 300,    # 连接回收时间
}

# 会话配置
app.config['PERMANENT_SESSION_LIFETIME'] = int(os.getenv('SESSION_LIFETIME', 86400))  # 会话有效期，默认1天
app.config['SESSION_COOKIE_SECURE'] = IS_PRODUCTION  # 生产环境强制HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # 防止JavaScript访问cookie
app.config['PREFERRED_URL_SCHEME'] = 'https' if IS_PRODUCTION else 'http'

# 配置日志
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/application.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('应用启动')

# 初始化数据库
from src.models import init_db
init_db(app)

# 注册蓝图
from src.routes.auth import auth_bp
from src.routes.activity import activity_bp
from src.routes.registration import registration_bp
from src.routes.dashboard import dashboard_bp
from src.routes.upload import upload_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(activity_bp, url_prefix='/api/activities')
app.register_blueprint(registration_bp, url_prefix='/api/registrations')
app.register_blueprint(dashboard_bp, url_prefix='/api')
app.register_blueprint(upload_bp, url_prefix='/api')

# 前端路由处理
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')

# 错误处理
@app.errorhandler(404)
def not_found(e):
    return render_template('index.html')

@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'message': '服务器内部错误'}), 500

# 安全头部
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

if __name__ == '__main__':
    # 生产环境使用
    app.run(host='0.0.0.0', port=5000, debug=False)