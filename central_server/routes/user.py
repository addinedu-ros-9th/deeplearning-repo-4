from flask import Blueprint, request, jsonify

bp = Blueprint('user', __name__, url_prefix='/load')

@bp.route('/private_information', methods=['POST'])
def get_private_information():
    """IF-02: 사용자 개인정보"""
    data = request.get_json()
    user_id = data.get('user_id')

    # TODO: DB에서 사용자 정보 조회 (services 계층 호출)
    if user_id == "user01":
        mock_data = {
            "name": "최기가",
            "email": "user01@gmail.com",
            "store_name": "GS25 금천점"
        }
        return jsonify(mock_data), 200
    else:
        return jsonify({"message": "User not found"}), 404 