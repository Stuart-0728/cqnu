from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os, uuid

upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')

ALLOWED_EXT = {'png','jpg','jpeg','gif'}

def allowed_file(fn): return '.' in fn and fn.rsplit('.',1)[1].lower() in ALLOWED_EXT

@upload_bp.route('/image', methods=['POST'])
def upload_image():
    """上传图片"""
    file = request.files.get('file')
    if not file or file.filename=='':
        return jsonify({'success':False,'message':'未选择文件'}),400
    if not allowed_file(file.filename):
        return jsonify({'success':False,'message':'不支持的文件类型'}),400
    fn = secure_filename(file.filename)
    unique = f"{uuid.uuid4().hex}_{fn}"
    folder = os.path.join(current_app.static_folder,'uploads')
    os.makedirs(folder,exist_ok=True)
    path = os.path.join(folder,unique)
    file.save(path)
    url = f"/static/uploads/{unique}"
    return jsonify({'success':True,'file_url':url}),200
