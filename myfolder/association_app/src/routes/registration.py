from flask import Blueprint, request, jsonify, session
from datetime import datetime

from src.models import db
from src.models.activity import Activity
from src.models.registration import Registration
from src.models.user import User
from src.routes.auth import login_required

registration_bp = Blueprint('registration', name)

@registration_bp.route('/activities/int:activity_id/register', methods=['POST'])
@login_required
def register_activity(activity_id):
"""用户报名活动"""
user_id = session['user_id']
user = User.query.get(user_id)
if not user:
return jsonify({'success': False, 'message': '用户不存在'}), 404
activity = Activity.query.get(activity_id)
if not activity:
    return jsonify({'success': False, 'message': '活动不存在'}), 404

if not activity.is_registration_open():
    return jsonify({'success': False, 'message': '活动报名已截止或已取消'}), 400

if activity.is_full():
    return jsonify({'success': False, 'message': '活动名额已满'}), 400

existing = Registration.query.filter_by(user_id=user_id, activity_id=activity_id).first()
if existing:
    return jsonify({'success': False, 'message': '您已报名此活动'}), 400

data = request.get_json() or {}
notes = data.get('notes', '')

reg = Registration(user_id=user_id, activity_id=activity_id, notes=notes)
try:
    db.session.add(reg)
    db.session.commit()
    return jsonify({'success': True, 'message': '报名成功', 'registration': reg.to_dict()}), 201
except Exception as e:
    db.session.rollback()
    return jsonify({'success': False, 'message': f'报名失败: {e}'}), 500
    @registration_bp.route('/activities/int:activity_id/cancel', methods=['POST'])
@login_required
def cancel_registration(activity_id):
"""用户取消报名"""
user_id = session['user_id']
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
    @registration_bp.route('/my-registrations', methods=['GET'])
@login_required
def get_my_registrations():
"""获取当前用户的所有报名记录"""
user_id = session['user_id']
status = request.args.get('status', 'all')
query = Registration.query.filter_by(user_id=user_id)
if status != 'all':
query = query.filter_by(status=status)
regs = query.order_by(Registration.registration_time.desc()).all()
result = []
for r in regs:
act = Activity.query.get(r.activity_id)
if act:
result.append({'registration': r.to_dict(), 'activity': act.to_dict()})
return jsonify({'success': True, 'registrations': result}), 200

@registration_bp.route('/activities/int:activity_id/registration-status', methods=['GET'])
@login_required
def check_registration_status(activity_id):
"""检查当前用户对指定活动的报名状态"""
user_id = session['user_id']
activity = Activity.query.get(activity_id)
if not activity:
return jsonify({'success': False, 'message': '活动不存在'}), 404
reg = Registration.query.filter_by(user_id=user_id, activity_id=activity_id).first()
if not reg:
return jsonify({'success': True, 'is_registered': False, 'activity': activity.to_dict()}), 200
return jsonify({'success': True, 'is_registered': True, 'registration': reg.to_dict(), 'activity': activity.to_dict()}), 200
