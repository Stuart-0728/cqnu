from flask import Blueprint, request, jsonify, session
from src.models.activity import Activity, Registration, db
from src.models.user import User
from src.routes.auth import login_required
from datetime import datetime

registration_bp = Blueprint('registration', __name__)

@registration_bp.route('/activities/<int:activity_id>/register', methods=['POST'])
@login_required
def register_activity(activity_id):
    """用户报名活动"""
    # 获取当前用户
    user_id = session['user_id']
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    # 获取活动信息
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'success': False, 'message': '活动不存在'}), 404
    
    # 检查活动是否开放报名
    if not activity.is_registration_open():
        return jsonify({'success': False, 'message': '活动报名已截止或已取消'}), 400
    
    # 检查活动是否已满员
    if activity.is_full():
        return jsonify({'success': False, 'message': '活动名额已满'}), 400
    
    # 检查用户是否已报名
    existing_registration = Registration.query.filter_by(
        user_id=user_id, 
        activity_id=activity_id
    ).first()
    
    if existing_registration:
        return jsonify({'success': False, 'message': '您已报名此活动'}), 400
    
    # 获取报名备注
    data = request.get_json() or {}
    notes = data.get('notes', '')
    
    # 创建报名记录
    try:
        registration = Registration(
            user_id=user_id,
            activity_id=activity_id,
            notes=notes
        )
        
        db.session.add(registration)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '报名成功',
            'registration': registration.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'报名失败: {str(e)}'}), 500

@registration_bp.route('/activities/<int:activity_id>/cancel', methods=['POST'])
@login_required
def cancel_registration(activity_id):
    """用户取消报名"""
    # 获取当前用户
    user_id = session['user_id']
    
    # 查找报名记录
    registration = Registration.query.filter_by(
        user_id=user_id, 
        activity_id=activity_id
    ).first()
    
    if not registration:
        return jsonify({'success': False, 'message': '您未报名此活动'}), 404
    
    # 获取活动信息
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'success': False, 'message': '活动不存在'}), 404
    
    # 检查是否可以取消报名（活动未开始）
    if datetime.utcnow() >= activity.start_time:
        return jsonify({'success': False, 'message': '活动已开始，无法取消报名'}), 400
    
    # 取消报名
    try:
        registration.status = 'cancelled'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '已取消报名'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'取消报名失败: {str(e)}'}), 500

@registration_bp.route('/my-registrations', methods=['GET'])
@login_required
def get_my_registrations():
    """获取当前用户的所有报名记录"""
    # 获取当前用户
    user_id = session['user_id']
    
    # 获取查询参数
    status = request.args.get('status', 'all')
    
    # 构建查询
    query = Registration.query.filter_by(user_id=user_id)
    
    # 根据状态筛选
    if status != 'all':
        query = query.filter_by(status=status)
    
    # 按报名时间倒序排列
    registrations = query.order_by(Registration.registration_time.desc()).all()
    
    # 构建结果，包含活动详情
    result = []
    for reg in registrations:
        activity = Activity.query.get(reg.activity_id)
        if activity:
            result.append({
                'registration': reg.to_dict(),
                'activity': activity.to_dict()
            })
    
    return jsonify({
        'success': True,
        'registrations': result
    }), 200

@registration_bp.route('/activities/<int:activity_id>/registration-status', methods=['GET'])
@login_required
def check_registration_status(activity_id):
    """检查当前用户对指定活动的报名状态"""
    # 获取当前用户
    user_id = session['user_id']
    
    # 获取活动信息
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'success': False, 'message': '活动不存在'}), 404
    
    # 查找报名记录
    registration = Registration.query.filter_by(
        user_id=user_id, 
        activity_id=activity_id
    ).first()
    
    if not registration:
        return jsonify({
            'success': True,
            'is_registered': False,
            'activity': activity.to_dict()
        }), 200
    
    return jsonify({
        'success': True,
        'is_registered': True,
        'registration': registration.to_dict(),
        'activity': activity.to_dict()
    }), 200
