from flask import Blueprint, request, jsonify
from central_server.services import user_service
from central_server.utils.response_utils import success_response, error_response


bp = Blueprint('load', __name__, url_prefix='/load')

@bp.route('/private_information', methods=['POST'])
def get_private_information():
    """IF-02: 사용자 개인정보 조회"""
    data = request.get_json()
    if not data or 'user_id' not in data:
        return error_response("user_id is required", 400)

    user_id = data.get('user_id')
    user_info = user_service.get_user_private_info(user_id)

    if user_info:
        return success_response(data=user_info)
    else:
        return error_response("User not found", 404) 