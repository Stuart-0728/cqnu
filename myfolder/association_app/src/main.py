from flask import Flask, session, render_template, request, jsonify, redirect, url_for
import os
import sys
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# 加载环境变量
load_dotenv()

# 创建Flask应用
def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_for_development')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 配置日志
    if not app.debug:
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
    
    # 主路由，返回前端SPA
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        # 传递空的currentUser变量以避免Jinja2错误
        return render_template('index.html', currentUser={'username': ''}, toastTitle='', toastMessage='')
    
    return app

# 从models导入必要的模块
from src.models import db, User, init_db

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')
