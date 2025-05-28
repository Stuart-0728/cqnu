# 文件：create_admin.py

import os
from src.models import db
from src.models.user import User
from flask import Flask
from dotenv import load_dotenv

# 加载 .env（本地开发或 Secret File）
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def main():
    with app.app_context():
        username = 'admin'
        password = os.getenv('ADMIN_PASSWORD', 'admin123')
        email = 'admin@cqnu.edu.cn'
        if not User.query.filter_by(username=username).first():
            admin = User(username=username, email=email, password=password, full_name='系统管理员', role='admin')
            db.session.add(admin)
            db.session.commit()
            print(f"管理员账户 '{username}' 已创建，密码：{password}")
        else:
            print(f"管理员账户 '{username}' 已存在。")

if __name__ == '__main__':
    main()
