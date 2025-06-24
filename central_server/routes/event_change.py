from flask import Blueprint, request, jsonify
from central_server.services.event_change_service import update_event_type, update_is_checked

bp = Blueprint('event_change', __name__, url_prefix='/change')

@bp.route('/event_type', methods=['POST'])
def change_event_type():
    """IF-06: 불법행위 종류 변경"""
    data = request.get_json()
    user_id = data.get('user_id')
    store_name = data.get('store_name')
    date = data.get('date')
    event_type = data.get('event_type')
    if not all([user_id, store_name, date, event_type]):
        return jsonify({"message": "필수 파라미터 누락"}), 404
    success = update_event_type(user_id, store_name, date, event_type)
    if success:
        return jsonify({"message": "Event type updated"}), 200
    else:
        return jsonify({"message": "업데이트 실패"}), 500

@bp.route('/is_checked', methods=['POST'])
def change_is_checked():
    """IF-07: 불법 확정"""
    data = request.get_json()
    user_id = data.get('user_id')
    store_name = data.get('store_name')
    date = data.get('date')
    is_checked = data.get('is_checked')
    if not all([user_id, store_name, date]) or is_checked is None:
        return jsonify({"message": "필수 파라미터 누락"}), 404
    success = update_is_checked(user_id, store_name, date, is_checked)
    if success:
        return jsonify({"message": "is_checked updated"}), 200
    else:
        return jsonify({"message": "업데이트 실패"}), 500 