from flask import Blueprint, request, jsonify, session
from src.models.activitie import activity, Registration, db
from src.routes.auth import login_required, admin_required
from datetime import datetime

activity_bp = Blueprint('activity', __name__)

@activity_bp.route('/', methods=['GET'])
def get_activitie():
    """获取所有活动列表"""
    # 获取查询参数
    status = request.args.get('status', 'all')
    
    # 构建查询
    query = activity.query
    
    # 根据状态筛选
    if status != 'all':
        query = query.filter_by(status=status)
    
    # 按创建时间倒序排列
    activity = query.order_by(activity.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'activity': [activity.to_dict() for activitiein activitie]
    }), 200

@activity_bp.route('/<int:activity_id>', methods=['GET'])
def get_activitie(activity_id):
    """获取指定活动详情"""
    activity = activity.query.get(activity_id)
    if not activity:
        return jsonify({'success': False, 'message': '活动不存在'}), 404
    
    return jsonify({
        'success': True,
        'activity': activity.to_dict()
    }), 200

@activity_bp.route('/', methods=['POST'])
@admin_required
def create_activity():
    """创建新活动（仅管理员）"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['title', 'description', 'location', 'start_time', 'end_time', 'registration_deadline']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400
    
    # 解析日期时间字符串
    try:
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        registration_deadline = datetime.fromisoformat(data['registration_deadline'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'success': False, 'message': '日期格式无效'}), 400
    
    # 验证日期逻辑
    now = datetime.utcnow()
    if start_time > end_time:
        return jsonify({'success': False, 'message': '活动开始时间不能晚于结束时间'}), 400
    
    if registration_deadline > start_time:
        return jsonify({'success': False, 'message': '报名截止时间应早于活动开始时间'}), 400
    
    # 创建新活动
    try:
        new_activity = activity(
            title=data['title'],
            description=data['description'],
            location=data['location'],
            start_time=start_time,
            end_time=end_time,
            registration_deadline=registration_deadline,
            created_by=session['user_id'],
            max_participants=data.get('max_participants'),
            image_url=data.get('image_url')
        )
        
        db.session.add(new_activity)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '活动创建成功',
            'activity': new_activity.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500

@activity_bp.route('/<int:activity_id>', methods=['PUT'])
@admin_required
def update_activity(activity_id):
    """更新活动信息（仅管理员）"""
    activity = activity.query.get(activity_id)
    if not activity:
        return jsonify({'success': False, 'message': '活动不存在'}), 404
    
    data = request.get_json()
    
    # 更新基本字段
    updatable_fields = ['title', 'description', 'location', 'max_participants', 'status', 'image_url']
    for field in updatable_fields:
        if field in data:
            setattr(activity, field, data[field])
    
    # 更新日期时间字段（需要解析）
    date_fields = {
        'start_time': 'start_time',
        'end_time': 'end_time',
        'registration_deadline': 'registration_deadline'
    }
    
    for json_field, model_field in date_fields.items():
        if json_field in data and data[json_field]:
            try:
                parsed_date = datetime.fromisoformat(data[json_field].replace('Z', '+00:00'))
                setattr(activity, model_field, parsed_date)
            except ValueError:
                return jsonify({'success': False, 'message': f'{json_field} 日期格式无效'}), 400
    
    # 验证日期逻辑
    if activity.start_time > activity.end_time:
        return jsonify({'success': False, 'message': '活动开始时间不能晚于结束时间'}), 400
    
    if activity.registration_deadline > activity.start_time:
        return jsonify({'success': False, 'message': '报名截止时间应早于活动开始时间'}), 400
    
    # 更新活动
    try:
        activity.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '活动已更新',
            'activity': activity.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@activity_bp.route('/<int:activity_id>', methods=['DELETE'])
@admin_required
def delete_activity(activity_id):
    """删除活动（仅管理员）"""
    activity = activity.query.get(activity_id)
    if not activity:
        return jsonify({'success': False, 'message': '活动不存在'}), 404
    
    try:
        db.session.delete(activity)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '活动已删除'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

@activity_bp.route('/<int:activity_id>/status', methods=['PUT'])
@admin_required
def update_activity_status(activity_id):
    """更新活动状态（仅管理员）"""
    activity = activity.query.get(activity_id)
    if not activity:
        return jsonify({'success': False, 'message': '活动不存在'}), 404
    
    data = request.get_json()
    if 'status' not in data or data['status'] not in ['active', 'cancelled', 'completed']:
        return jsonify({'success': False, 'message': '无效的状态值'}), 400
    
    activity.status = data['status']
    
    try:
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '活动状态已更新',
            'activity': activity.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@activity_bp.route('/<int:activity_id>/participants', methods=['GET'])
@admin_required
def get_activity_participants(activity_id):
    """获取活动参与者列表（仅管理员）"""
    activity = activity.query.get(activity_id)
    if not activity:
        return jsonify({'success': False, 'message': '活动不存在'}), 404
    
    # 获取所有报名记录及用户信息
    registrations = Registration.query.filter_by(activity_id=activity_id).all()
    
    participants = []
    for reg in registrations:
        user = reg.participant
        participants.append({
            'registration_id': reg.id,
            'registration_time': reg.registration_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': reg.status,
            'notes': reg.notes,
            'user_id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'email': user.email,
            'student_id': user.student_id,
            'phone': user.phone,
            'department': user.department,
            'major': user.major
        })
    
    return jsonify({
        'success': True,
        'activity': activity.to_dict(),
        'participants': participants,
        'total_count': len(participants)
    }), 200
