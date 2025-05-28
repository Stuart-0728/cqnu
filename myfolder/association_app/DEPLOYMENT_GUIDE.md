# 重庆师范大学师能素质协会活动报名系统部署指南

本文档提供了详细的部署步骤，帮助技术团队将活动报名系统部署到生产环境中。

## 系统要求

### 硬件要求
- CPU: 双核或更高
- 内存: 至少2GB RAM
- 存储: 至少10GB可用空间

### 软件要求
- 操作系统: Linux (推荐Ubuntu 20.04或更高版本)
- Python: 3.8或更高版本
- MySQL: 5.7或更高版本
- Web服务器: Nginx或Apache (用于生产环境)

## 部署步骤

### 1. 准备环境

#### 安装Python和依赖工具
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv mysql-server nginx
```

#### 创建虚拟环境
```bash
mkdir -p /opt/cqnu_association
cd /opt/cqnu_association
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装项目

#### 复制项目文件
将项目文件复制到服务器上的部署目录：
```bash
# 假设项目文件已上传到服务器
cp -r /path/to/uploaded/project/* /opt/cqnu_association/
```

#### 安装依赖
```bash
cd /opt/cqnu_association
pip install -r requirements.txt
```

### 3. 配置数据库

#### 创建数据库和用户
```bash
sudo mysql -u root -p
```

在MySQL命令行中执行：
```sql
CREATE DATABASE association_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'association_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON association_db.* TO 'association_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 配置数据库连接
创建环境变量文件：
```bash
cd /opt/cqnu_association
cat > .env << EOF
DB_USERNAME=association_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=association_db
SECRET_KEY=your_secure_secret_key
EOF
```

### 4. 初始化应用

#### 修改主程序配置
编辑`src/main.py`文件，确保从环境变量加载配置：
```python
# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 其他配置保持不变
```

#### 初始化数据库
```bash
cd /opt/cqnu_association
source venv/bin/activate
python -c "from src.models import init_db; from src.main import app; init_db(app)"
```

### 5. 配置Web服务器

#### 使用Gunicorn作为WSGI服务器
安装Gunicorn：
```bash
pip install gunicorn
```

创建启动脚本：
```bash
cat > /opt/cqnu_association/start.sh << EOF
#!/bin/bash
cd /opt/cqnu_association
source venv/bin/activate
export FLASK_APP=src.main
export FLASK_ENV=production
gunicorn --workers 3 --bind 0.0.0.0:5000 src.main:app
EOF

chmod +x /opt/cqnu_association/start.sh
```

#### 配置Nginx
创建Nginx配置文件：
```bash
sudo nano /etc/nginx/sites-available/association
```

添加以下内容：
```
server {
    listen 80;
    server_name your_domain.com;  # 替换为您的域名

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/cqnu_association/src/static;
        expires 30d;
    }
}
```

启用站点并重启Nginx：
```bash
sudo ln -s /etc/nginx/sites-available/association /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. 设置系统服务

创建systemd服务文件：
```bash
sudo nano /etc/systemd/system/association.service
```

添加以下内容：
```
[Unit]
Description=CQNU Association Activity Registration System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/cqnu_association
Environment="PATH=/opt/cqnu_association/venv/bin"
ExecStart=/opt/cqnu_association/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 src.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启用并启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable association
sudo systemctl start association
```

### 7. 安全配置

#### 设置防火墙
```bash
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

#### 配置HTTPS (推荐)
使用Let's Encrypt获取SSL证书：
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

### 8. 验证部署

访问您的域名或服务器IP地址，确认系统正常运行。

默认管理员账号：
- 用户名: admin
- 密码: admin123

**重要提示**: 首次登录后请立即修改默认管理员密码！

## 维护指南

### 备份数据库
定期备份数据库：
```bash
mysqldump -u association_user -p association_db > backup_$(date +%Y%m%d).sql
```

### 更新应用
更新应用代码：
```bash
cd /opt/cqnu_association
source venv/bin/activate
git pull  # 如果使用Git管理代码
pip install -r requirements.txt  # 更新依赖
sudo systemctl restart association  # 重启服务
```

### 日志查看
查看应用日志：
```bash
sudo journalctl -u association
```

## 故障排除

### 应用无法启动
- 检查日志: `sudo journalctl -u association`
- 验证数据库连接: `mysql -u association_user -p association_db`
- 确认环境变量已正确加载

### 无法访问网站
- 检查Nginx状态: `sudo systemctl status nginx`
- 验证防火墙设置: `sudo ufw status`
- 确认域名DNS解析正确

### 数据库连接错误
- 验证MySQL服务状态: `sudo systemctl status mysql`
- 检查数据库用户权限
- 确认连接参数正确

## 联系支持

如有任何部署或使用问题，请联系系统开发团队获取支持。
