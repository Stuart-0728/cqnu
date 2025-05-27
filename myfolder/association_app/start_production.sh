#!/bin/bash

# 生产环境启动脚本
echo "正在启动重庆师范大学师能素质协会活动报名系统..."

# 确保工作目录正确
cd "$(dirname "$0")"

# 激活虚拟环境
source venv/bin/activate

# 确保依赖已安装
pip install -r requirements.txt

# 确保上传目录存在
mkdir -p src/static/uploads

# 设置正确的文件权限
chmod -R 755 src/static
chmod -R 777 src/static/uploads

# 使用gunicorn启动应用
gunicorn -w 4 -b 0.0.0.0:5000 "src.main:app"
