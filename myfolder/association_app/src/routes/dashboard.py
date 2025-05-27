from flask import Blueprint, request, jsonify, session
from src.models.activity import Activity, Registration, db
from src.models.user import User
from src.routes.auth import admin_required
from datetime import datetime
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """获取管理员仪表盘统计数据"""
    # 获取用户统计
    total_users = User.query.count()
    student_users = User.query.filter_by(role='student').count()
    admin_users = User.query.filter_by(role='admin').count()
    
    # 获取活动统计
    total_activities = Activity.query.count()
    active_activities = Activity.query.filter_by(status='active').count()
    completed_activities = Activity.query.filter_by(status='completed').count()
    cancelled_activities = Activity.query.filter_by(status='cancelled').count()
    
    # 获取报名统计
    total_registrations = Registration.query.count()
    active_registrations = Registration.query.filter_by(status='registered').count()
    cancelled_registrations = Registration.query.filter_by(status='cancelled').count()
    
    # 获取最近活动
    recent_activities = Activity.query.order_by(Activity.created_at.desc()).limit(5).all()
    
    # 获取即将开始的活动
    upcoming_activities = Activity.query.filter(
        Activity.start_time > datetime.utcnow(),
        Activity.status == 'active'
    ).order_by(Activity.start_time).limit(5).all()
    
    return jsonify({
        'success': True,
        'stats': {
            'users': {
                'total': total_users,
                'students': student_users,
                'admins': admin_users
            },
            'activities': {
                'total': total_activities,
                'active': active_activities,
                'completed': completed_activities,
                'cancelled': cancelled_activities
            },
            'registrations': {
                'total': total_registrations,
                'active': active_registrations,
                'cancelled': cancelled_registrations
            }
        },
        'recent_activities': [activity.to_dict() for activity in recent_activities],
        'upcoming_activities': [activity.to_dict() for activity in upcoming_activities]
    }), 200

@dashboard_bp.route('/dashboard/activities', methods=['GET'])
@admin_required
def get_dashboard_activities():
    """获取管理员仪表盘活动列表（带报名统计）"""
    # 获取查询参数
    status = request.args.get('status', 'all')
    
    # 构建查询
    query = Activity.query
    
    # 根据状态筛选
    if status != 'all':
        query = query.filter_by(status=status)
    
    # 按创建时间倒序排列
    activities = query.order_by(Activity.created_at.desc()).all()
    
    # 构建结果，包含报名统计
    result = []
    for activity in activities:
        activity_dict = activity.to_dict()
        
        # 获取报名统计
        total_registrations = Registration.query.filter_by(activity_id=activity.id).count()
        active_registrations = Registration.query.filter_by(
            activity_id=activity.id, 
            status='registered'
        ).count()
        
        activity_dict['registration_stats'] = {
            'total': total_registrations,
            'active': active_registrations
        }
        
        result.append(activity_dict)
    
    return jsonify({
        'success': True,
        'activities': result
    }), 200

@dashboard_bp.route('/dashboard/users', methods=['GET'])
@admin_required
def get_dashboard_users():
    """获取管理员仪表盘用户列表（带报名统计）"""
    # 获取查询参数
    role = request.args.get('role', 'all')
    
    # 构建查询
    query = User.query
    
    # 根据角色筛选
    if role != 'all':
        query = query.filter_by(role=role)
    
    # 按创建时间倒序排列
    users = query.order_by(User.created_at.desc()).all()
    
    # 构建结果，包含报名统计
    result = []
    for user in users:
        user_dict = user.to_dict()
        
        # 获取报名统计
        total_registrations = Registration.query.filter_by(user_id=user.id).count()
        active_registrations = Registration.query.filter_by(
            user_id=user.id, 
            status='registered'
        ).count()
        
        user_dict['registration_stats'] = {
            'total': total_registrations,
            'active': active_registrations
        }
        
        result.append(user_dict)
    
    return jsonify({
        'success': True,
        'users': result
    }), 200

@dashboard_bp.route('/dashboard/export/participants/<int:activity_id>', methods=['GET'])
@admin_required
def export_participants(activity_id):
    """导出活动参与者信息（CSV格式）"""
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'success': False, 'message': '活动不存在'}), 404
    
    # 获取所有报名记录及用户信息
    registrations = Registration.query.filter_by(activity_id=activity_id).all()
    
    # 构建CSV数据
    csv_data = "序号,用户名,姓名,学号,院系,专业,电话,邮箱,报名时间,状态,备注\n"
    
    for i, reg in enumerate(registrations, 1):
        user = reg.participant
        # 格式化CSV行
        csv_row = [
            str(i),
            user.username,
            user.full_name,
            user.student_id or '',
            user.department or '',
            user.major or '',
            user.phone or '',
            user.email,
            reg.registration_time.strftime('%Y-%m-%d %H:%M:%S'),
            reg.status,
            reg.notes or ''
        ]
        # 处理CSV特殊字符
        csv_row = ['"' + field.replace('"', '""') + '"' if ',' in field or '"' in field else field for field in csv_row]
        csv_data += ",".join(csv_row) + "\n"
    
    return jsonify({
        'success': True,
        'activity': activity.to_dict(),
        'csv_data': csv_data,
        'filename': f"participants_{activity_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
    }), 200

@dashboard_bp.route('/dashboard/registrations/update-status', methods=['POST'])
@admin_required
def update_registration_status():
    """批量更新报名状态"""
    data = request.get_json()
    
    if not data or 'registrations' not in data or not isinstance(data['registrations'], list):
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400
    
    if 'status' not in data or data['status'] not in ['registered', 'cancelled', 'attended']:
        return jsonify({'success': False, 'message': '无效的状态值'}), 400
    
    # 获取要更新的报名ID列表
    registration_ids = data['registrations']
    new_status = data['status']
    
    try:
        # 批量更新状态
        updated_count = 0
        for reg_id in registration_ids:
            reg = Registration.query.get(reg_id)
            if reg:
                reg.status = new_status
                updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'已更新 {updated_count} 条报名记录的状态',
            'updated_count': updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500
