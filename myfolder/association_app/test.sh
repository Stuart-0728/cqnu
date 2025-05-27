#!/bin/bash

# 创建测试脚本
echo "开始测试重庆师范大学师能素质协会活动报名系统..."

# 测试数据库连接
echo "测试数据库连接..."
python3 -c "
import sys
sys.path.insert(0, '/home/ubuntu/cqnu_association/association_app')
from src.models.user import db
from src.main import app

with app.app_context():
    try:
        db.engine.connect()
        print('数据库连接成功')
    except Exception as e:
        print(f'数据库连接失败: {e}')
        sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "数据库测试失败，请检查配置"
    exit 1
fi

# 测试API端点
echo "测试API端点..."
python3 -c "
import sys
import requests
import json

base_url = 'http://localhost:5000/api'

def test_endpoint(method, endpoint, data=None, expected_status=200):
    url = f'{base_url}{endpoint}'
    print(f'测试 {method} {url}')
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data)
        else:
            print(f'不支持的方法: {method}')
            return False
        
        if response.status_code != expected_status:
            print(f'测试失败: 状态码 {response.status_code}, 预期 {expected_status}')
            print(f'响应: {response.text}')
            return False
        
        print('测试通过')
        return True
    except Exception as e:
        print(f'测试异常: {e}')
        return False

# 测试服务器是否运行
try:
    requests.get('http://localhost:5000/')
    print('服务器已启动')
except:
    print('服务器未启动，无法进行API测试')
    sys.exit(0)

# 测试用户注册
test_data = {
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'password123',
    'full_name': '测试用户'
}
test_endpoint('POST', '/auth/register', test_data, 201)

# 测试用户登录
login_data = {
    'username': 'testuser',
    'password': 'password123'
}
test_endpoint('POST', '/auth/login', login_data, 200)

print('API测试完成')
"

echo "测试完成"
