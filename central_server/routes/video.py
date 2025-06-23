import json
from flask import Blueprint, request, send_file, Response
import os

bp = Blueprint('video', __name__)

@bp.route('/load/video', methods=['POST'])
def load_video():
    """IF-04: 영상 실행"""
    data = request.get_json()
    user_id = data.get('user_id')
    video_url = data.get('video_url')
    
    # TODO: video_url의 보안 검사 및 실제 비디오 경로 찾기
    video_path = f"path/to/videos/{video_url}" 

    if not os.path.exists(video_path):
        return Response(json.dumps({"message": "Video not found"}, ensure_ascii=False), status=404, mimetype='application/json')

    # 1. send_file을 사용한 간단 스트리밍 (브라우저/플레이어에서 바로 재생 가능)
    return send_file(
        video_path,
        mimetype='video/mp4',
        as_attachment=False,  # 다운로드가 아니라 바로 재생
        download_name=video_url
    )

@bp.route('/delete/video', methods=['POST'])
def delete_video():
    """IF-08: 영상 삭제"""
    data = request.get_json()
    video_url = data.get('video_url')

    # TODO: Service를 통해 DB 및 파일 시스템에서 영상 삭제
    print(f"영상 삭제 요청: {video_url}")
    return Response(json.dumps({"message": f"Video {video_url} deleted"}, ensure_ascii=False), status=200, mimetype='application/json') 