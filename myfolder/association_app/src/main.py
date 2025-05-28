from flask import Flask, session, render_template, request, jsonify, redirect, url_for
import os
from src.models import init_db
from src.routes.auth import auth_bp
from src.routes.activities import activities_bp
from src.routes.admin import admin_bp
from src.routes.user import user_bp
from src.utils.config import Config

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 配置应用
    app.config.from_object(Config)
    
    # 初始化数据库
    init_db(app)  # 确保这行没有被注释掉
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    
    # 主路由 - 处理前端路由
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        """处理所有前端路由，返回主页面"""
        return render_template('index.html')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
