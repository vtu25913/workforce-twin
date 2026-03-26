from flask import Flask
from flask_cors import CORS
from database import db, init_db
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.personas import personas_bp
from routes.simulate import simulate_bp
from routes.insights import insights_bp
from routes.admin import admin_bp
import os


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "workforce-twin-secret-2024")

    # Fix Railway proxy stripping Authorization header
    app.config["PROPAGATE_EXCEPTIONS"] = True
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    db_url = os.environ.get("DATABASE_URL", "sqlite:///workforce_twin.db")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_EXPIRY_HOURS"] = 8

    CORS(app,
         resources={r"/api/*": {"origins": "*"}},
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
         expose_headers=["Authorization"])

    db.init_app(app)

    app.register_blueprint(auth_bp,      url_prefix="/api/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(personas_bp,  url_prefix="/api/personas")
    app.register_blueprint(simulate_bp,  url_prefix="/api/simulate")
    app.register_blueprint(insights_bp,  url_prefix="/api/insights")
    app.register_blueprint(admin_bp,     url_prefix="/api/admin")

    with app.app_context():
        init_db()

    from flask import send_from_directory

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        return send_from_directory("static", "index.html")

    return app


# gunicorn entry point
flask_app = create_app()

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))