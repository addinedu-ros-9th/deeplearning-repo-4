import json
from flask import Blueprint, request, send_file, Response
import os
from central_server.services import video_service
from central_server.services.video_service import get_video_path, delete_video_file, delete_checked_videos, update_video_favorite


bp = Blueprint('video', __name__)

@bp.route('/load/video', methods=['GET'])
def load_video():
    """IF-04: 영상 실행"""
    video_url = request.args.get('video_url')

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

@bp.route('/delete/checked_video', methods=['POST'])
def delete_checked_video():
    """IF-10: 영상 선택 삭제"""
    data = request.get_json()
    user_id = data.get('user_id')
    video_urls = data.get('video_urls', [])
    
    if not user_id or not video_urls:
        return Response(json.dumps({"status_code": 400, "message": "user_id와 video_urls가 필요합니다"}, ensure_ascii=False), status=400, mimetype='application/json')
    
    success = delete_checked_videos(user_id, video_urls)
    if success:
        return Response(json.dumps({"status_code": 200}, ensure_ascii=False), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({"status_code": 500, "message": "영상 삭제 실패"}, ensure_ascii=False), status=500, mimetype='application/json')

@bp.route('/favorite/video', methods=['POST'])
def favorite_video():
    """IF-11: 영상 즐겨찾기 기능"""
    data = request.get_json()
    user_id = data.get('user_id')
    video_url = data.get('video_url')
    favorite = data.get('favorite')
    
    if not user_id or not video_url or favorite is None:
        return Response(json.dumps({"status_code": 400, "message": "user_id, video_url, favorite가 필요합니다"}, ensure_ascii=False), status=400, mimetype='application/json')
    
    if favorite not in [0, 1]:
        return Response(json.dumps({"status_code": 400, "message": "favorite는 0 또는 1이어야 합니다"}, ensure_ascii=False), status=400, mimetype='application/json')
    
    success = update_video_favorite(user_id, video_url, favorite)
    if success:
        return Response(json.dumps({"status_code": 200}, ensure_ascii=False), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({"status_code": 500, "message": "즐겨찾기 업데이트 실패"}, ensure_ascii=False), status=500, mimetype='application/json') 

