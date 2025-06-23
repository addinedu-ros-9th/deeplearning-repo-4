from flask import jsonify

def success_response(data=None, message="Success", status_code=200):
    """성공적인 API 응답을 생성합니다."""
    response = {
        "status": "success",
        "message": message,
        "data": data
    }
    return jsonify(response), status_code

def error_response(message="Error", status_code=400):
    """오류 API 응답을 생성합니다."""
    response = {
        "status": "error",
        "message": message
    }
    return jsonify(response), status_code 