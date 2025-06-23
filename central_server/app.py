from flask import Flask
from routes import auth, user, detect_log, video, event_change, dashboard

def create_app():
    app = Flask(__name__)

    # 블루프린트 등록
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(detect_log.bp)
    app.register_blueprint(video.bp)
    app.register_blueprint(event_change.bp)
    app.register_blueprint(dashboard.bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=6006, debug=True) 