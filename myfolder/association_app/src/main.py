import os
import sys
from dotenv import load_dotenv
from flask import Flask, render_template
from logging.handlers import RotatingFileHandler
import logging

# 加载本地 .env，线上 Render 环境无 .env 也不会报错
load_dotenv()

# 确保能导入 src 包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Flask 工厂函数
from utils.config import Config
from src.models import init_db, db
from src.models.user import User

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    # 应用配置
    app.config.from_object(Config)

    # 日志配置，仅生产关闭 debug 时启用
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        handler = RotatingFileHandler('logs/app.log', maxBytes=10*1024*1024, backupCount=5)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('应用启动')

    # 初始化数据库并建表
    init_db(app)

    # 首次请求前创建默认管理员
    @app.before_first_request
    def ensure_admin():
        pwd = os.getenv('ADMIN_PASSWORD', 'admin123')
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

    # 注册蓝图
    from src.routes.auth import auth_bp
    from src.routes.activities import activities_bp
    from src.routes.admin import admin_bp
    from src.routes.user import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)

    # 前端路由回退
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return render_template('index.html')

    return app

# 全局 WSGI 应用
app = create_app()

if __name__ == '__main__':
    # 本地开发模式
    debug = os.getenv('FLASK_ENV', 'development') != 'production'
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=debug)
