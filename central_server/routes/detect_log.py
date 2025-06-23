from flask import Blueprint, request, jsonify

bp = Blueprint('detect_log', __name__, url_prefix='/load/detect_log')

@bp.route('/week', methods=['POST'])
def get_detect_log_week():
    """IF-03: detect log 일주일"""
    data = request.get_json()
    user_id = data.get('user_id')
    # TODO: Service를 통해 일주일치 로그 데이터 조회
    print(f"일주일 로그 조회 요청: {user_id}")
    mock_data = {
      "broken": [{"time": "2025-06-23 11:39:00", "video_url": "video_1.mp4"}],
      "theft": [{"time": "2025-06-21 11:00:00", "video_url": "video_34.mp4"}]
    }
    return jsonify(mock_data), 200

@bp.route('/filter', methods=['POST'])
def get_detect_log_filter():
    """IF-05: detect log 조회"""
    data = request.get_json()
    # TODO: Service를 통해 필터링된 로그 데이터 조회
    print(f"필터 로그 조회 요청: {data}")
    mock_data = [
      {"store_name": "GS 금천점", "timestamp": "20250530 00:00:00", "event_type": "broken", "person_count": 2, "is_checked": 0, "video_url": "video_34.mp4"}
    ]
    return jsonify(mock_data), 200 