from flask import Flask, session, g, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'cqnu_association_secret_key')

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 生产环境配置
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 会话有效期为1天
app.config['SESSION_COOKIE_SECURE'] = True  # 仅通过HTTPS发送cookie
app.config['SESSION_COOKIE_HTTPONLY'] = True  # 防止JavaScript访问cookie
app.config['PREFERRED_URL_SCHEME'] = 'https'  # 优先使用HTTPS

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
