import json
from flask import Blueprint, request, Response
from central_server.services import notification_service

bp = Blueprint('notification', __name__, url_prefix='/load/notification')

@bp.route('/', methods=['POST'])
def get_notification():
    """IF-03: 알림 조회"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        error_response = {"status": "error", "message": "user_id is required"}
        return Response(json.dumps(error_response, ensure_ascii=False), mimetype='application/json'), 404
        
    logs = notification_service.get_24h_logs(user_id)
    return Response(json.dumps(logs, ensure_ascii=False, default=str), mimetype='application/json'), 200