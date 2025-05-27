from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
import os
import uuid

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload/image', methods=['POST'])
def upload_image():
    """上传图片文件"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有文件'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        # 添加UUID前缀避免文件名冲突
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # 确保上传目录存在
        upload_folder = os.path.join(current_app.static_folder, 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # 保存文件
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # 返回可访问的URL
        file_url = f"/static/uploads/{unique_filename}"
        
        return jsonify({
            'success': True,
            'message': '文件上传成功',
            'file_url': file_url
        }), 200
    
    return jsonify({'success': False, 'message': '不支持的文件类型'}), 400

def allowed_file(filename):
    """检查文件类型是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
