from flask import Blueprint, request, jsonify
from central_server.services.dashboard_service import get_status_data

bp = Blueprint('dashboard', __name__, url_prefix='/load')

@bp.route('/dash_board', methods=['POST'])
def get_dashboard_data():
    """IF-09: 통계 조회"""
    data = request.get_json()
    user_id = data.get('user_id')
    date = data.get('date')
    
    print(f"대시보드 요청: {user_id}, {date}")
    mock_data = {
      "user_id": user_id,
      "event_types": ["파손", "유기", "절도", "전등 끔"],
      "monthly_stats": [
        {"month": "2025-04", "count": [10, 8, 5, 3], "ratio": [40, 30, 20, 10], "time_distribution": {"00-06": [1,1,1,1],"06-12":[2,2,2,0],"12-18":[3,3,1,1],"18-24":[4,2,1,1]}},
        {"month": "2025-05", "count": [20, 18, 10, 13], "ratio": [45, 27, 18, 10], "time_distribution": {"00-06": [1,2,3,4],"06-12":[1,2,3,4],"12-18":[1,2,3,4],"18-24":[1,2,3,4]}}
      ]
    }
    return jsonify(mock_data), 200 