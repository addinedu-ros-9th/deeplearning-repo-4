from flask import Blueprint, request, jsonify

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['POST'])
def login():
    """IF-01: 로그인"""
    data = request.get_json()
    user_id = data.get('user_id')

    # TODO: 사용자 인증 로직 구현 (services/auth_service.py 호출)
    if user_id:
        print(f"로그인 시도: {user_id}")
        # 성공 시
        return jsonify({"message": "Login successful"}), 200
    else:
        # 실패 시
        return jsonify({"message": "Invalid credentials"}), 401 