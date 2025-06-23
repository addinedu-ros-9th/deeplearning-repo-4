from flask import Blueprint, request, jsonify

bp = Blueprint('event_change', __name__, url_prefix='/change')

@bp.route('/event_type', methods=['POST'])
def change_event_type():
    """IF-06: 불법행위 종류 변경"""
    data = request.get_json()
    # TODO: Service를 통해 DB에서 event_type 업데이트
    print(f"종류 변경 요청: {data}")
    return jsonify({"message": "Event type updated"}), 200

@bp.route('/is_checked', methods=['POST'])
def change_is_checked():
    """IF-07: 불법 확정"""
    data = request.get_json()
    # TODO: Service를 통해 DB에서 is_checked 업데이트
    print(f"확정 변경 요청: {data}")
    return jsonify({"message": "is_checked updated"}), 200 