from flask import Blueprint, request, jsonify
from services import auth_service
from utils.response_utils import success_response, error_response

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['POST'])
def login():
    """IF-01: 로그인"""
    data = request.get_json()
    if not data or 'user_id' not in data:
        return error_response("user_id is required", 400)

    user_id = data.get('user_id')

    is_verified = auth_service.verify_user(user_id)

    if is_verified:
        # 성공 시
        return success_response("Login successful")
    else:
        # 실패 시
        return error_response("Invalid credentials", 404) 