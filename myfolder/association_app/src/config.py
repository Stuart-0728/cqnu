import os
from dotenv import load_dotenv

#加载环境变量

load_dotenv()

class Config:
"""生产和开发环境配置"""
SECRET_KEY = os.getenv('SECRET_KEY', 'cqnu_association_secret')
DEBUG = os.getenv('FLASK_ENV', 'production') != 'production'
TESTING = False
# 数据库配置
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///database.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 文件上传配置
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

# 会话配置
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = True
SESSION_USE_SIGNER = True
PERMANENT_SESSION_LIFETIME = int(os.getenv('SESSION_LIFETIME', 86400))  # 秒

# Cookie 安全配置
SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
