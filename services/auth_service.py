import logging
from datetime import datetime, timezone, timedelta

from extensions import db
from models import Admin, PasswordResetToken

logger = logging.getLogger(__name__)


class AuthService:
    """Business logic for authentication flows."""

    # ------------------------------------------------------------------ #
    #  Sign Up                                                             #
    # ------------------------------------------------------------------ #
    @staticmethod
    def register(full_name: str, email: str, password: str) -> Admin:
        """
        Create and persist a new Admin.
        Raises ValueError if the email is already registered.
        """
        email = email.strip().lower()

        if Admin.query.filter_by(email=email).first():
            raise ValueError("An account with this email already exists.")

        admin = Admin(full_name=full_name.strip(), email=email)
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()
        logger.info("New admin registered: %s", email)
        return admin

    # ------------------------------------------------------------------ #
    #  Login                                                               #
    # ------------------------------------------------------------------ #
    @staticmethod
    def authenticate(email: str, password: str) -> Admin:
        """
        Validate credentials.
        Raises ValueError with a generic message on failure to prevent
        user-enumeration attacks.
        """
        admin = Admin.query.filter_by(email=email.strip().lower()).first()
        if not admin or not admin.check_password(password):
            raise ValueError("Invalid email or password.")
        return admin

    # ------------------------------------------------------------------ #
    #  Forgot Password                                                     #
    # ------------------------------------------------------------------ #
    @staticmethod
    def initiate_password_reset(email: str) -> None:
        """
        Generate a reset token for *email* if an account exists.
        Always returns silently — never reveal whether the email is registered.
        The generated reset link is printed to the console (no real email sent).
        """
        admin = Admin.query.filter_by(email=email.strip().lower()).first()
        if not admin:
            # Intentionally silent — prevents email enumeration
            return

        # Invalidate any existing unused tokens for this admin
        PasswordResetToken.query.filter_by(admin_id=admin.id, used=False).delete()

        token_obj = PasswordResetToken.generate(admin.id)
        db.session.add(token_obj)
        db.session.commit()

        # In production, send via email. Here we log the link.
        reset_link = f"http://localhost:5000/api/auth/reset-password?token={token_obj.token}"
        logger.info("Password reset link for %s → %s", email, reset_link)
        print(f"\n[PASSWORD RESET LINK] → {reset_link}\n")

    # ------------------------------------------------------------------ #
    #  Reset Password                                                      #
    # ------------------------------------------------------------------ #
    @staticmethod
    def reset_password(token: str, new_password: str) -> None:
        """
        Validate the reset token and update the admin's password.
        Raises ValueError on invalid/expired token.
        """
        token_obj = PasswordResetToken.query.filter_by(token=token).first()

        if not token_obj or not token_obj.is_valid:
            raise ValueError("This reset link is invalid or has expired.")

        admin = db.session.get(Admin, token_obj.admin_id)
        if not admin:
            raise ValueError("Associated account not found.")

        admin.set_password(new_password)
        token_obj.used = True
        db.session.commit()
        logger.info("Password reset successfully for admin_id=%s", admin.id)
