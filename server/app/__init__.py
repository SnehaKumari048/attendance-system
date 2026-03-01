from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from .config import Config

db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)

    from app.models.user import User
    from app.models.student import Student
    from app.models.course import Course
    from app.models.attendance import Attendance

    from app.routes.auth_routes import auth_bp
    from app.routes.student_routes import student_bp
    from app.routes.course_routes import course_bp   
    from app.routes.attendance_routes import attendance_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(attendance_bp)

    @app.route("/")
    def home():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Socket Test</title>
            <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
        </head>
        <body>
            <h2>Socket Test Page</h2>
            <script>
                var socket = io();

            socket.on("attendance_update", function(data) {
                console.log("Live Update:", data);
                alert("Attendance Update: " + JSON.stringify(data));
            });
        </script>
    </body>
    </html>
    """

    return app