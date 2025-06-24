import sys
import os

# 프로젝트 루트 디렉토리를 sys.path에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(project_root) == 'central_server':
    project_root = os.path.dirname(project_root)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask
from central_server.routes import auth, user, detect_log, video, event_change, dashboard, notification

def create_app():
    app = Flask(__name__)

    # 블루프린트 등록
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(detect_log.bp)
    app.register_blueprint(video.bp)
    app.register_blueprint(event_change.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(notification.bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=6006, debug=True) 