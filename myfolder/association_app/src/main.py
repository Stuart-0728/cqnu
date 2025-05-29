import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

# 定义项目根目录（当前文件所在目录）
basedir = os.path.abspath(os.path.dirname(__file__))

# 确保 logs 目录存在（如果不存在则创建）
log_dir = os.path.join(basedir, 'logs')
os.makedirs(log_dir, exist_ok=True)

app = Flask(__name__)

# 加载配置文件（如有），示例使用 basedir
# config_path = os.path.join(basedir, 'config.cfg')
# if os.path.exists(config_path):
#     app.config.from_pyfile(config_path)

# 日志配置：创建日志文件处理器
file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'app.log'),
    maxBytes=10 * 1024 * 1024,  # 最大10MB
    backupCount=5
)
file_handler.setLevel(logging.INFO)
# 设置日志格式
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
file_handler.setFormatter(formatter)
# 将处理器添加到 Flask 应用的 logger
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Application startup')

# 定义路由或注册蓝图
@app.route('/')
def index():
    return 'Hello, World!'

# 将 Flask 应用实例赋值给 Gunicorn 等 WSGI 服务器的入口变量
application = app

if __name__ == '__main__':
    # 使用 Render 提供的 PORT 环境变量（默认5000），并监听所有接口
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
