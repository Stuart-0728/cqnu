from flask import Flask, session, render_template, request, jsonify, redirect, url_for
import os
import sys
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# 加载 .env 文件里的环境变量
load_dotenv()

def create_app():
    # 指定 static 和 template 目录
    base = os.path.dirname(__file__)
    app = Flask(
        __name__,
        static_folder=os.path.join(base, 'static'),
        template_folder=os.path.join(base, 'templates')
    )
    
    # 基础配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_for_development')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ==== 日志目录自动创建 ====
    project_root = os.path.abspath(os.path.join(base, os.pardir))
    log_dir = os.path.join(project_root, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    if not app.debug:
        handler = RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')

    # ==== 数据库初始化 ====
    from src.models import db, init_db
    db.init_app(app)
    init_db(app)

    # ==== 注册各模块蓝图 ====
    from src.routes.auth import auth_bp
    from src.routes.activities import activities_bp   # 正确的复数导入
    from src.routes.admin import admin_bp
    from src.routes.user import user_bp
    from src.routes.registration import registration_bp
    from src.routes.dashboard import dashboard_bp
    from src.routes.upload import upload_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(activities_bp)           # 复数
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(registration_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(upload_bp)
    
    # SPA 前端入口：所有路径返回 index.html
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return render_template(
            'index.html',
            currentUser={'username': ''},
            toastTitle='',
            toastMessage=''
        )
    
    # 调试路由：查看实际加载路径
    @app.route('/__debug__')
    def debug_info():
        cwd = os.getcwd()
        src_dir = os.path.abspath(base)
        return jsonify({
            "cwd": cwd,
            "files_in_cwd": os.listdir(cwd),
            "src_dir": src_dir,
            "files_in_src": os.listdir(src_dir),
        })

    return app

# WSGI 入口
from src.models import db, User, init_db
app = create_app()
application = app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
