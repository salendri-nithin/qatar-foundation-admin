import logging
from datetime import timedelta

from flask import Blueprint, request
from flask_jwt_extended import create_access_token

from config import active_config
from services import AuthService
from utils.validators import validate_signup_payload
from utils.responses import success_response, error_response

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# --------------------------------------------------------------------------- #
#  POST /api/auth/signup                                                        #
# --------------------------------------------------------------------------- #
@auth_bp.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json(silent=True) or {}

        error = validate_signup_payload(data)
        if error:
            return error_response(error, 422)

        admin = AuthService.register(
            full_name=data["full_name"],
            email=data["email"],
            password=data["password"],
        )
        return success_response(
            "Account created successfully. Please log in.",
            data=admin.to_dict(),
            status=201,
        )

    except ValueError as exc:
        return error_response(str(exc), 409)
    except Exception as exc:
        logger.exception("Unexpected error during signup")
        return error_response("An internal error occurred. Please try again.", 500)


# --------------------------------------------------------------------------- #
#  POST /api/auth/login                                                         #
# --------------------------------------------------------------------------- #
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(silent=True) or {}

        email = data.get("email", "").strip()
        password = data.get("password", "")
        remember_me = bool(data.get("remember_me", False))

        if not email or not password:
            return error_response("Email and password are required.", 422)

        admin = AuthService.authenticate(email, password)

        # Extend token lifetime when "remember me" is checked
        expires = (
            active_config.JWT_REMEMBER_ME_EXPIRES
            if remember_me
            else active_config.JWT_ACCESS_TOKEN_EXPIRES
        )
        token = create_access_token(identity=str(admin.id), expires_delta=expires)

        return success_response(
            "Login successful.",
            data={
                "access_token": token,
                "token_type": "Bearer",
                "expires_in": int(expires.total_seconds()),
                "admin": admin.to_dict(),
            },
        )

    except ValueError as exc:
        return error_response(str(exc), 401)
    except Exception:
        logger.exception("Unexpected error during login")
        return error_response("An internal error occurred. Please try again.", 500)


# --------------------------------------------------------------------------- #
#  POST /api/auth/forgot-password                                               #
# --------------------------------------------------------------------------- #
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    try:
        data = request.get_json(silent=True) or {}
        email = data.get("email", "").strip()

        if not email:
            return error_response("Email is required.", 422)

        # Always returns success to prevent email enumeration
        AuthService.initiate_password_reset(email)

        return success_response(
            "If an account with that email exists, a reset link has been sent."
        )

    except Exception:
        logger.exception("Unexpected error during forgot-password")
        return error_response("An internal error occurred. Please try again.", 500)


# --------------------------------------------------------------------------- #
#  POST /api/auth/reset-password                                                #
# --------------------------------------------------------------------------- #
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    try:
        data = request.get_json(silent=True) or {}
        token = data.get("token", "").strip()
        new_password = data.get("new_password", "")
        confirm_password = data.get("confirm_password", "")

        if not token:
            return error_response("Reset token is required.", 422)

        if len(new_password) < 8:
            return error_response("Password must be at least 8 characters long.", 422)

        if new_password != confirm_password:
            return error_response("Passwords do not match.", 422)

        AuthService.reset_password(token, new_password)
        return success_response("Password has been reset successfully. Please log in.")

    except ValueError as exc:
        return error_response(str(exc), 400)
    except Exception:
        logger.exception("Unexpected error during reset-password")
        return error_response("An internal error occurred. Please try again.", 500)
