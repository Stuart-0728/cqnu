from flask import Flask, session, render_template, request, jsonify, redirect, url_for
import os
import sys
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# 加载 .env 文件里的环境变量
load_dotenv()

# 创建 Flask 应用工厂
def create_app():
    # 指定 static 和 template 目录
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), 'static'),
        template_folder=os.path.join(os.path.dirname(__file__), 'templates')
    )
    
    # 基础配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_for_development')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ==== 日志目录自动创建 ====
    # main.py 在 src/ 目录下，project_root 是 association_app/
    basedir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(basedir, os.pardir))
    log_dir = os.path.join(project_root, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # 日志配置：仅当非调试模式时启用文件日志
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
    from src.routes.activities import activities_bp
    from src.routes.admin import admin_bp
    from src.routes.user import user_bp
    from src.routes.registration import registration_bp
    from src.routes.dashboard import dashboard_bp
    from src.routes.upload import upload_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(registration_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(upload_bp)
    
    # 主路由：所有前端页面都返回 index.html（SPA）
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        # 传递一个空的 currentUser，避免 Jinja2 渲染时报错
        return render_template(
            'index.html',
            currentUser={'username': ''},
            toastTitle='',
            toastMessage=''
        )
    
    # ==== 调试路由：查看实际工作目录和 src 内容 ====
    @app.route('/__debug__')
    def debug_info():
        cwd = os.getcwd()
        src_dir = os.path.abspath(os.path.dirname(__file__))
        return jsonify({
            "cwd": cwd,
            "files_in_cwd": os.listdir(cwd),
            "src_dir": src_dir,
            "files_in_src": os.listdir(src_dir),
        })

    return app

# 下面两行保持不动，用于 Gunicorn 或 flask run
from src.models import db, User, init_db

app = create_app()
# Gunicorn 默认会寻找 application 或 app
application = app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
