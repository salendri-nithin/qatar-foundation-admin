"""
Qatar Foundation — Admin Portal Backend
Entry point: initializes the Flask app and wires all components together.
"""

import logging
import os

from flask import Flask, jsonify
from dotenv import load_dotenv

load_dotenv()

from config import active_config
from extensions import db, jwt, bcrypt, cors
from routes import auth_bp, opportunity_bp

# --------------------------------------------------------------------------- #
#  Logging                                                                      #
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
#  App factory                                                                  #
# --------------------------------------------------------------------------- #
def create_app(config=None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config or active_config)

    # --- Extensions --------------------------------------------------------- #
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config.get("FRONTEND_URL", "*")}},
        supports_credentials=True,
    )

    # --- Blueprints --------------------------------------------------------- #
    app.register_blueprint(auth_bp)
    app.register_blueprint(opportunity_bp)

    # --- Database ----------------------------------------------------------- #
    with app.app_context():
        # Import models so SQLAlchemy is aware of them before create_all()
        from models import Admin, Opportunity, PasswordResetToken  # noqa: F401
        db.create_all()
        logger.info("Database tables verified/created.")

    # --- Global error handlers ---------------------------------------------- #
    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"status": "error", "message": "Endpoint not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify({"status": "error", "message": "Method not allowed."}), 405

    @app.errorhandler(422)
    def unprocessable(_):
        return jsonify({"status": "error", "message": "Unprocessable request."}), 422

    @app.errorhandler(500)
    def internal_error(_):
        return jsonify({"status": "error", "message": "Internal server error."}), 500

    # --- JWT error handlers ------------------------------------------------- #
    @jwt.unauthorized_loader
    def missing_token_callback(reason):
        return (
            jsonify({"status": "error", "message": "Authentication token is missing."}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return (
            jsonify({"status": "error", "message": "Authentication token is invalid."}),
            401,
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"status": "error", "message": "Authentication token has expired. Please log in again."}),
            401,
        )

    # --- Health check ------------------------------------------------------- #
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "message": "Qatar Foundation Admin API is running."})

    return app


# --------------------------------------------------------------------------- #
#  Entry point                                                                  #
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    flask_app = create_app()
    port = int(os.getenv("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port, debug=bool(os.getenv("FLASK_DEBUG", True)))
