# 生产环境配置文件
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础配置
SECRET_KEY = os.environ.get('SECRET_KEY', 'cqnu_association_production_secret_key')
DEBUG = False
TESTING = False

# 数据库配置
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 文件上传配置
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

# 会话配置
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = True
SESSION_USE_SIGNER = True
PERMANENT_SESSION_LIFETIME = 86400  # 24小时

# 安全配置
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
