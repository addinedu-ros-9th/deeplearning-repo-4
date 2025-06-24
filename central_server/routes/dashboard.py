from flask import Blueprint, request, jsonify
from central_server.services.dashboard_service import get_status_data

bp = Blueprint('dashboard', __name__, url_prefix='/load')

@bp.route('/dashboard', methods=['POST'])
def get_dashboard_data():
    """IF-09: 통계 조회"""
    data = request.get_json()
    user_id = data.get('user_id')
    date = data.get('date')
    
    print(f"대시보드 요청: {user_id}, {date}")
    result = get_status_data(user_id, date)
    return jsonify(result), 200 