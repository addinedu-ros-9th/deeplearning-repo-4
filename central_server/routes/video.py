from flask import Blueprint, request, jsonify, send_file
import os

bp = Blueprint('video', __name__)

@bp.route('/load/video', methods=['POST'])
def load_video():
    """IF-04: 영상 실행"""
    data = request.get_json()
    video_url = data.get('video_url')
    
    # TODO: video_url의 보안 검사 및 실제 비디오 경로 찾기
    video_path = f"path/to/videos/{video_url}" 

    if os.path.exists(video_path):
        return send_file(video_path, mimetype='video/mp4')
    else:
        return jsonify({"message": "Video not found"}), 404

@bp.route('/delete/video', methods=['POST'])
def delete_video():
    """IF-08: 영상 삭제"""
    data = request.get_json()
    video_url = data.get('video_url')

    # TODO: Service를 통해 DB 및 파일 시스템에서 영상 삭제
    print(f"영상 삭제 요청: {video_url}")
    return jsonify({"message": f"Video {video_url} deleted"}), 200 