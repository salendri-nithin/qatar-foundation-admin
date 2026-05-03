from datetime import datetime, timezone
from extensions import db

ALLOWED_CATEGORIES = ["Technology", "Business", "Design", "Marketing", "Data Science", "Other"]


class Opportunity(db.Model):
    """Opportunity model — owned by an Admin."""
    __tablename__ = "opportunities"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=False, index=True)

    name = db.Column(db.String(150), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=False)          # Stored comma-separated
    category = db.Column(db.String(50), nullable=False)
    future_opportunities = db.Column(db.Text, nullable=True)
    max_applicants = db.Column(db.Integer, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "admin_id": self.admin_id,
            "name": self.name,
            "duration": self.duration,
            "start_date": self.start_date,
            "description": self.description,
            "skills": self.skills,
            "category": self.category,
            "future_opportunities": self.future_opportunities,
            "max_applicants": self.max_applicants,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Opportunity {self.name}>"
