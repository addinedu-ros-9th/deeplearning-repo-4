import json
from flask import Blueprint, request, send_file, Response
import os
from central_server.services import video_service
from central_server.services.video_service import get_video_path, delete_video_file


bp = Blueprint('video', __name__)

@bp.route('/load/video', methods=['POST'])
def load_video():
    """IF-04: 영상 실행"""
    data = request.get_json()
    video_url = data.get('video_url')

    video_path = get_video_path(video_url)

    if not video_path or not os.path.exists(video_path):
        return Response(json.dumps({"message": "Video not found"}, ensure_ascii=False), status=404, mimetype='application/json')

    return send_file(
        video_path,
        mimetype='video/mp4',
        as_attachment=False,
        download_name=video_url
    )

@bp.route('/delete/video', methods=['POST'])
def delete_video():
    """IF-08: 영상 삭제"""
    data = request.get_json()
    video_url = data.get('video_url')

    deleted_path = delete_video_file(video_url)
    if deleted_path:
        return Response(json.dumps({"message": f"Video {video_url} deleted", "path": deleted_path}, ensure_ascii=False), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({"message": "삭제 실패 또는 해당 영상 없음"}, ensure_ascii=False), status=404, mimetype='application/json') 

