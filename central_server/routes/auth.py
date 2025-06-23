import json
import traceback
from flask import Blueprint, request, Response
from central_server.services import auth_service

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['POST'])
def login():
    """IF-01: 로그인"""
    data = request.get_json()
    user_id = data.get('user_id')
    password = data.get('passwd')

    if not user_id or not password:
        error_response = {"status": "error", "message": "user_id and passwd are required"}
        return Response(json.dumps(error_response, ensure_ascii=False), mimetype='application/json'), 404

    try:
        result, status_code = auth_service.login_user(user_id, password)
        return Response(json.dumps(result, ensure_ascii=False), mimetype='application/json'), status_code
    except Exception as e:
        print("로그인 중 예외 발생:", e)
        traceback.print_exc()
        error_response = {"message": "서버 오류 발생"}
        return Response(json.dumps(error_response, ensure_ascii=False), mimetype='application/json'), 500 