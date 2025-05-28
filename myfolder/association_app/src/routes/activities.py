from flask import Blueprint, request, jsonify, session, abort
from src.models.activity import Activity, Registration, db
from src.routes.auth import login_required, admin_required
from datetime import datetime

activity_bp = Blueprint('activity', __name__)


class ActivityStatus:
    ACTIVE = 'active'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    CHOICES = [ACTIVE, CANCELLED, COMPLETED]


def parse_datetime(value):
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None


def validate_activity_times(start, end, deadline):
    if start > end:
        return '活动开始时间不能晚于结束时间'
    if deadline > start:
        return '报名截止时间应早于活动开始时间'
    return None


def update_model_fields(instance, data, fields):
    for field in fields:
        if field in data:
            setattr(instance, field, data[field])


@activity_bp.route('/', methods=['GET'])
def get_activities():
    status = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Activity.query.filter_by(is_deleted=False)

    if status != 'all':
        query = query.filter_by(status=status)

    pagination = query.order_by(Activity.created_at.desc()).paginate(page, per_page, error_out=False)
    activities = [activity.to_dict() for activity in pagination.items]

    return jsonify({
        'success': True,
        'activities': activities,
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages
    }), 200


@activity_bp.route('/<int:activity_id>', methods=['GET'])
def get_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id, description='活动不存在')
    if activity.is_deleted:
        abort(404, description='活动不存在')
    return jsonify({'success': True, 'activity': activity.to_dict()}), 200


@activity_bp.route('/', methods=['POST'])
@admin_required
def create_activity():
    data = request.get_json()
    required_fields = ['title', 'description', 'location', 'start_time', 'end_time', 'registration_deadline']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400

    start_time = parse_datetime(data['start_time'])
    end_time = parse_datetime(data['end_time'])
    registration_deadline = parse_datetime(data['registration_deadline'])
    if not all([start_time, end_time, registration_deadline]):
        return jsonify({'success': False, 'message': '日期格式无效'}), 400

    msg = validate_activity_times(start_time, end_time, registration_deadline)
    if msg:
        return jsonify({'success': False, 'message': msg}), 400

    try:
        new_activity = Activity(
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

        return jsonify({'success': True, 'message': '活动创建成功', 'activity': new_activity.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500


@activity_bp.route('/<int:activity_id>', methods=['PUT'])
@admin_required
def update_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id, description='活动不存在')
    if activity.is_deleted:
        abort(404, description='活动不存在')

    data = request.get_json()
    update_model_fields(activity, data, ['title', 'description', 'location', 'max_participants', 'status', 'image_url'])

    for key in ['start_time', 'end_time', 'registration_deadline']:
        if key in data:
            dt = parse_datetime(data[key])
            if not dt:
                return jsonify({'success': False, 'message': f'{key} 日期格式无效'}), 400
            setattr(activity, key, dt)

    msg = validate_activity_times(activity.start_time, activity.end_time, activity.registration_deadline)
    if msg:
        return jsonify({'success': False, 'message': msg}), 400

    try:
        activity.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'message': '活动已更新', 'activity': activity.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@activity_bp.route('/<int:activity_id>', methods=['DELETE'])
@admin_required
def delete_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id, description='活动不存在')
    if activity.is_deleted:
        abort(404, description='活动不存在')

    try:
        activity.is_deleted = True
        db.session.commit()
        return jsonify({'success': True, 'message': '活动已删除'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


@activity_bp.route('/<int:activity_id>/status', methods=['PUT'])
@admin_required
def update_activity_status(activity_id):
    activity = Activity.query.get_or_404(activity_id, description='活动不存在')
    if activity.is_deleted:
        abort(404, description='活动不存在')

    data = request.get_json()
    status = data.get('status')
    if status not in ActivityStatus.CHOICES:
        return jsonify({'success': False, 'message': '无效的状态值'}), 400

    activity.status = status
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '活动状态已更新', 'activity': activity.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@activity_bp.route('/<int:activity_id>/participants', methods=['GET'])
@admin_required
def get_activity_participants(activity_id):
    activity = Activity.query.get_or_404(activity_id, description='活动不存在')
    if activity.is_deleted:
        abort(404, description='活动不存在')

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
