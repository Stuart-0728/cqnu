from flask import Blueprint, request, jsonify, session, abort
from datetime import datetime

from src.models import db
from src.models.activity import Activity
from src.models.registration import Registration
from src.models.user import User
from src.routes.auth import login_required

# 正确创建 Blueprint，名字和模块名对应
registration_bp = Blueprint('registration', __name__)

# 用户报名活动
@registration_bp.route('/activities/<int:activity_id>/register', methods=['POST'])
@login_required
def register_activity(activity_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404

    activity = Activity.query.get(activity_id)
    if not activity or activity.is_deleted:
        return jsonify({'success': False, 'message': '活动不存在'}), 404

    # 检查报名截止和活动状态
    if activity.registration_deadline < datetime.utcnow() or activity.status != 'active':
        return jsonify({'success': False, 'message': '活动报名已截止或已取消'}), 400

    # 检查是否已满
    if activity.max_participants and activity.registrations.count() >= activity.max_participants:
        return jsonify({'success': False, 'message': '活动名额已满'}), 400

    # 检查是否已报名
    existing = Registration.query.filter_by(user_id=user_id, activity_id=activity_id).first()
    if existing:
        return jsonify({'success': False, 'message': '您已报名此活动'}), 400

    data = request.get_json() or {}
    notes = data.get('notes', '')

    reg = Registration(
        user_id=user_id,
        activity_id=activity_id,
        registration_time=datetime.utcnow(),
        status='pending',
        notes=notes
    )
    try:
        db.session.add(reg)
        db.session.commit()
        return jsonify({'success': True, 'message': '报名成功', 'registration': reg.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'报名失败: {e}'}), 500

# 用户取消报名
@registration_bp.route('/activities/<int:activity_id>/cancel', methods=['POST'])
@login_required
def cancel_registration(activity_id):
    user_id = session.get('user_id')
    reg = Registration.query.filter_by(user_id=user_id, activity_id=activity_id).first()
    if not reg:
        return jsonify({'success': False, 'message': '您未报名此活动'}), 404

    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'success': False, 'message': '活动不存在'}), 404

    if datetime.utcnow() >= activity.start_time:
        return jsonify({'success': False, 'message': '活动已开始，无法取消报名'}), 400

    try:
        reg.status = 'cancelled'
        db.session.commit()
        return jsonify({'success': True, 'message': '已取消报名'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'取消报名失败: {e}'}), 500

# 获取当前用户的所有报名记录
@registration_bp.route('/my-registrations', methods=['GET'])
@login_required
def get_my_registrations():
    user_id = session.get('user_id')
    status = request.args.get('status', 'all')
    query = Registration.query.filter_by(user_id=user_id)
    if status != 'all':
        query = query.filter_by(status=status)
    regs = query.order_by(Registration.registration_time.desc()).all()

    result = []
    for r in regs:
        act = Activity.query.get(r.activity_id)
        if act:
            result.append({
                'registration': r.to_dict(),
                'activity': act.to_dict()
            })
    return jsonify({'success': True, 'registrations': result}), 200

# 检查当前用户对指定活动的报名状态
@registration_bp.route('/activities/<int:activity_id>/status', methods=['GET'])
@login_required
def check_registration_status(activity_id):
    user_id = session.get('user_id')
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'success': False, 'message': '活动不存在'}), 404

    reg = Registration.query.filter_by(user_id=user_id, activity_id=activity_id).first()
    if not reg:
        return jsonify({
            'success': True,
            'is_registered': False,
            'activity': activity.to_dict()
        }), 200

    return jsonify({
        'success': True,
        'is_registered': True,
        'registration': reg.to_dict(),
        'activity': activity.to_dict()
    }), 200
