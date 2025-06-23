import json
from flask import Blueprint, request, Response
from central_server.services import user_service

bp = Blueprint('load', __name__, url_prefix='/load')

@bp.route('/private_information', methods=['POST'])
def get_private_information():
    """IF-02: 사용자 개인정보 조회"""
    data = request.get_json()
    if not data or 'user_id' not in data:
        error_response = {"status": "error", "message": "user_id is required"}
        return Response(json.dumps(error_response, ensure_ascii=False), mimetype='application/json'), 404

    user_id = data.get('user_id')
    user_info = user_service.get_user_private_info(user_id)

    if user_info:
        response = {
            "status": "success",
            "message": "Success",
            "data": user_info
        }
        return Response(json.dumps(response, ensure_ascii=False), mimetype='application/json'), 200
    else:
        error_response = {"status": "error", "message": "User not found"}
        return Response(json.dumps(error_response, ensure_ascii=False), mimetype='application/json'), 401 