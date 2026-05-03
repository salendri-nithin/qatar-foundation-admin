import secrets
from datetime import datetime, timezone, timedelta
from extensions import db


class PasswordResetToken(db.Model):
    """Single-use, time-limited password reset token."""
    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=False, index=True)
    token = db.Column(db.String(128), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    @classmethod
    def generate(cls, admin_id: int) -> "PasswordResetToken":
        """Create a new token with a 1-hour expiry."""
        return cls(
            admin_id=admin_id,
            token=secrets.token_urlsafe(64),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )

    @property
    def is_valid(self) -> bool:
        """True if the token has not been used and has not expired."""
        now = datetime.now(timezone.utc)
        expires = (
            self.expires_at.replace(tzinfo=timezone.utc)
            if self.expires_at.tzinfo is None
            else self.expires_at
        )
        return not self.used and expires > now

    def __repr__(self) -> str:
        return f"<PasswordResetToken admin_id={self.admin_id}>"
