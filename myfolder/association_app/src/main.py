import os
from flask import Flask
from dotenv import load_dotenv

# 本地开发时才会加载 .env；线上 Render 环境不存在 .env，就什么也不做
load_dotenv()

app = Flask(__name__)

# 读取环境变量
ENV = os.getenv('FLASK_ENV', 'production')
IS_PRODUCTION = ENV == 'production'

if IS_PRODUCTION and not os.getenv('SECRET_KEY'):
    raise RuntimeError('生产环境必须设置 SECRET_KEY 环境变量')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = int(os.getenv('SESSION_LIFETIME', 86400))

# 如果你在代码里手动读取 PORT
port = int(os.getenv('PORT', 5000))

# 初始化数据库等
from src.models import init_db
init_db(app)

if __name__ == '__main__':
    # 本地开发：debug=True；线上请使用 Gunicorn 启动
    app.run(host='0.0.0.0', port=port, debug=(ENV != 'production'))
