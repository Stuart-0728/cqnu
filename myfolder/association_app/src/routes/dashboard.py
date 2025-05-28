from flask import Blueprint, request, jsonify
from datetime import datetime

from src.models import db
from src.models.user import User
from src.models.activity import Activity
from src.models.registration import Registration
from src.routes.auth import admin_required

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """获取管理员仪表盘统计数据"""
    total_users = User.query.count()
    student_users = User.query.filter_by(role='student').count()
    admin_users = User.query.filter_by(role='admin').count()

    total_activities = Activity.query.count()
    active_activities = Activity.query.filter_by(status='active').count()
    completed_activities = Activity.query.filter_by(status='completed').count()
    cancelled_activities = Activity.query.filter_by(status='cancelled').count()

    total_reg = Registration.query.count()
    active_reg = Registration.query.filter_by(status='registered').count()
    cancelled_reg = Registration.query.filter_by(status='cancelled').count()

    recent_acts = Activity.query.order_by(Activity.created_at.desc()).limit(5).all()
    upcoming_acts = Activity.query.filter(
        Activity.start_time > datetime.utcnow(),
        Activity.status == 'active'
    ).order_by(Activity.start_time).limit(5).all()

    return jsonify({
        'success': True,
        'stats': {
            'users': {'total': total_users, 'students': student_users, 'admins': admin_users},
            'activities': {'total': total_activities, 'active': active_activities,
                           'completed': completed_activities, 'cancelled': cancelled_activities},
            'registrations': {'total': total_reg, 'active': active_reg, 'cancelled': cancelled_reg}
        },
        'recent_activities': [act.to_dict() for act in recent_acts],
        'upcoming_activities': [act.to_dict() for act in upcoming_acts]
    }), 200

@dashboard_bp.route('/activities', methods=['GET'])
@admin_required
def get_dashboard_activities():
    """获取仪表盘活动列表，包含报名统计"""
    status = request.args.get('status', 'all')
    query = Activity.query
    if status != 'all':
        query = query.filter_by(status=status)
    acts = query.order_by(Activity.created_at.desc()).all()
    result = []
    for act in acts:
        ad = act.to_dict()
        total = Registration.query.filter_by(activity_id=act.id).count()
        active = Registration.query.filter_by(activity_id=act.id, status='registered').count()
        ad['registration_stats'] = {'total': total, 'active': active}
        result.append(ad)
    return jsonify({'success': True, 'activities': result}), 200

@dashboard_bp.route('/users', methods=['GET'])
@admin_required
def get_dashboard_users():
    """获取仪表盘用户列表，包含报名统计"""
    role = request.args.get('role', 'all')
    query = User.query
    if role != 'all':
        query = query.filter_by(role=role)
    users = query.order_by(User.created_at.desc()).all()
    result = []
    for u in users:
        ud = u.to_dict()
        total = Registration.query.filter_by(user_id=u.id).count()
        active = Registration.query.filter_by(user_id=u.id, status='registered').count()
        ud['registration_stats'] = {'total': total, 'active': active}
        result.append(ud)
    return jsonify({'success': True, 'users': result}), 200

@dashboard_bp.route('/export/participants/<int:activity_id>', methods=['GET'])
@admin_required
def export_participants(activity_id):
    """导出活动参与者 CSV 数据"""
    act = Activity.query.get(activity_id)
    if not act:
        return jsonify({'success': False, 'message': '活动不存在'}), 404
    regs = Registration.query.filter_by(activity_id=activity_id).all()
    csv = '序号,用户名,姓名,学号,院系,专业,电话,邮箱,报名时间,状态,备注\n'
    for i, r in enumerate(regs, 1):
        u = User.query.get(r.user_id)
        row = [str(i), u.username, u.full_name, u.student_id or '', u.department or '',
               u.major or '', u.phone or '', u.email, r.registration_time.strftime('%Y-%m-%d %H:%M:%S'),
               r.status, r.notes or '']
        # 处理双引号和逗号
        row = ['"'+f.replace('"','""')+'"' if ',' in f or '"' in f else f for f in row]
        csv += ','.join(row) + '\n'
    filename = f"participants_{activity_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
    return jsonify({'success': True, 'activity': act.to_dict(), 'filename': filename, 'csv_data': csv}), 200

@dashboard_bp.route('/registrations/update-status', methods=['POST'])
@admin_required
def update_registration_status():
    """批量更新报名状态"""
    data = request.get_json() or {}
    ids = data.get('registrations', [])
    new_status = data.get('status')
    if not isinstance(ids, list) or new_status not in ['registered','cancelled','attended']:
        return jsonify({'success': False, 'message': '无效请求'}), 400
    updated = 0
    for rid in ids:
        r = Registration.query.get(rid)
        if r:
            r.status = new_status
            updated += 1
    db.session.commit()
    return jsonify({'success': True, 'updated_count': updated}), 200
