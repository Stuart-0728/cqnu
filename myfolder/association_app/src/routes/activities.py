# 文件：src/routes/activities.py

from flask import Blueprint, request, jsonify, current_app
from src.models.activity import Activity
from datetime import datetime

activity_bp = Blueprint('activities', __name__)

@activity_bp.route('/', methods=['GET'])
def get_activities():
    try:
        status   = request.args.get('status', 'all')
        page     = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # 不再使用 is_deleted 过滤
        query = Activity.query

        if status != 'all':
            query = query.filter_by(status=status)

        pagination = query.order_by(Activity.created_at.desc()) \
                          .paginate(page=page, per_page=per_page, error_out=False)
        activities = [a.to_dict() for a in pagination.items]

        return jsonify({
            'success': True,
            'activities': activities,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages
        }), 200

    except Exception as e:
        current_app.logger.error(f'get_activities error: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'activities': [],
            'message': '服务暂不可用，请稍后再试'
        }), 200

@activity_bp.route('/<int:activity_id>', methods=['GET'])
def get_activity(activity_id):
    try:
        activity = Activity.query.get_or_404(activity_id, description='活动不存在')
        return jsonify({'success': True, 'activity': activity.to_dict()}), 200
    except Exception as e:
        current_app.logger.error(f'get_activity error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': '活动获取失败'}), 404

# 其余创建/更新/删除接口保持不变
