from datetime import datetime, timezone
from extensions import db, bcrypt


class Admin(db.Model):
    """Admin user model."""
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    opportunities = db.relationship(
        "Opportunity", backref="creator", lazy=True, cascade="all, delete-orphan"
    )
    reset_tokens = db.relationship(
        "PasswordResetToken", backref="admin", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        """Hash and store the password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Verify the plain-text password against the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Admin {self.email}>"
