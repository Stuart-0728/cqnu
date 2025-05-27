from flask import Flask, session, render_template, request, jsonify, redirect, url_for, send_from_directory
import os
import sys
import json
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# 确保正确的导入路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 导入数据库模型
from src.models import db, User, Activity, Registration

# 创建Flask应用
app = Flask(__name__)

# 配置应用
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cqnu_association_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化数据库
db.init_app(app)

# 导入路由
from src.routes.auth import auth_bp
from src.routes.activity import activity_bp
from src.routes.registration import registration_bp
from src.routes.dashboard import dashboard_bp
from src.routes.upload import upload_bp

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(activity_bp, url_prefix='/api/activities')
app.register_blueprint(registration_bp, url_prefix='/api/registrations')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(upload_bp, url_prefix='/api/upload')

# 创建数据库表
with app.app_context():
    db.create_all()
    
    # 检查是否需要创建默认管理员账户
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@cqnu.edu.cn',
            password=generate_password_hash('admin123'),
            full_name='管理员',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

# 前端路由处理
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')

# 静态文件处理
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# 错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 200

@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'message': '服务器内部错误'}), 500

# 启动应用
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
