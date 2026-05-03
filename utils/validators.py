import re
from typing import Optional


EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email))


def validate_signup_payload(data: dict) -> Optional[str]:
    """
    Validate Admin Sign-Up payload.
    Returns an error message string on failure, or None on success.
    """
    required = ["full_name", "email", "password", "confirm_password"]
    for field in required:
        if not data.get(field, "").strip():
            return f"'{field}' is required."

    if not is_valid_email(data["email"].strip()):
        return "Please provide a valid email address."

    if len(data["password"]) < 8:
        return "Password must be at least 8 characters long."

    if data["password"] != data["confirm_password"]:
        return "Passwords do not match."

    return None


def validate_opportunity_payload(data: dict) -> Optional[str]:
    """
    Validate Opportunity create/update payload.
    Returns an error message string on failure, or None on success.
    """
    from models.opportunity import ALLOWED_CATEGORIES

    required = ["name", "duration", "start_date", "description", "skills", "category"]
    for field in required:
        if not str(data.get(field, "")).strip():
            return f"'{field}' is required."

    if data["category"] not in ALLOWED_CATEGORIES:
        return (
            f"Invalid category. Must be one of: {', '.join(ALLOWED_CATEGORIES)}."
        )

    max_applicants = data.get("max_applicants")
    if max_applicants is not None and max_applicants != "":
        try:
            val = int(max_applicants)
            if val < 1:
                raise ValueError
        except (ValueError, TypeError):
            return "'max_applicants' must be a positive integer."

    return None
