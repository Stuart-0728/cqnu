import os

class Config:
    """生产和开发环境配置"""

    # 基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'cqnu_association_secret')
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
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
    PERMANENT_SESSION_LIFETIME = int(os.getenv('SESSION_LIFETIME', 86400))  # 默认 1 天

    # Cookie 安全配置
    SESSION_COOKIE_SECURE = os.getenv('RENDER', 'false') == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
