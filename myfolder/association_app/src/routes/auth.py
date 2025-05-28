from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import User, db
from datetime import datetime
import functools

auth_bp = Blueprint('auth', __name__)

# 装饰器：检查用户是否已登录
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

# 装饰器：检查用户是否为管理员
def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin():
            return jsonify({'success': False, 'message': '需要管理员权限'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['username', 'email', 'password', 'full_name']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': '邮箱已被注册'}), 400
    
    # 创建新用户
    try:
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            full_name=data['full_name'],
            role='student',  # 默认为学生角色
            student_id=data.get('student_id'),
            phone=data.get('phone'),
            department=data.get('department'),
            major=data.get('major')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': '注册成功',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'full_name': new_user.full_name,
                'role': new_user.role
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.get_json()
    
    # 验证必填字段
    if not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    # 查找用户
    user = User.query.filter_by(username=data['username']).first()
    
    # 验证用户和密码
    if not user or not user.check_password(data['password']):
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    
    # 更新最后登录时间
    user.update_last_login()
    
    # 设置会话
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    session.permanent = True  # 使会话持久化
    
    return jsonify({
        'success': True,
        'message': '登录成功',
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'role': user.role
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出接口"""
    session.clear()
    return jsonify({'success': True, 'message': '已成功登出'}), 200

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """获取当前用户信息"""
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新用户信息"""
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    data = request.get_json()
    
    # 更新可修改的字段
    updatable_fields = ['full_name', 'phone', 'department', 'major']
    for field in updatable_fields:
        if field in data:
            setattr(user, field, data[field])
    
    # 更新密码（如果提供）
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '个人信息已更新',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@auth_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """管理员获取所有用户列表"""
    users = User.query.all()
    return jsonify({
        'success': True,
        'users': [user.to_dict() for user in users]
    }), 200

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """管理员获取指定用户信息"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(user_id):
    """管理员更新用户角色"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    data = request.get_json()
    if 'role' not in data or data['role'] not in ['admin', 'student']:
        return jsonify({'success': False, 'message': '无效的角色值'}), 400
    
    user.role = data['role']
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '用户角色已更新',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500
