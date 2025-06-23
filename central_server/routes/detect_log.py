import json
from flask import Blueprint, request, Response
from central_server.services import detect_service

bp = Blueprint('detect_log', __name__, url_prefix='/load/detect_log')

@bp.route('/week', methods=['POST'])
def get_detect_log_week():
    """IF-03: detect log 일주일"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        error_response = {"status": "error", "message": "user_id is required"}
        return Response(json.dumps(error_response, ensure_ascii=False), mimetype='application/json'), 404
        
    logs = detect_service.get_weekly_logs(user_id)
    return Response(json.dumps(logs, ensure_ascii=False, default=str), mimetype='application/json'), 200

@bp.route('/filter', methods=['POST'])
def get_detect_log_filter():
    """IF-05: detect log 조회"""
    data = request.get_json()
    logs = detect_service.get_filtered_logs(data)
    return Response(json.dumps(logs, ensure_ascii=False, default=str), mimetype='application/json'), 200 