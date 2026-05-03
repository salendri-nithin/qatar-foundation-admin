import logging
from typing import List, Optional

from extensions import db
from models import Opportunity

logger = logging.getLogger(__name__)


class OpportunityService:
    """Business logic for Opportunity CRUD operations."""

    # ------------------------------------------------------------------ #
    #  Read — All                                                          #
    # ------------------------------------------------------------------ #
    @staticmethod
    def get_all(admin_id: int) -> List[Opportunity]:
        return (
            Opportunity.query.filter_by(admin_id=admin_id)
            .order_by(Opportunity.created_at.desc())
            .all()
        )

    # ------------------------------------------------------------------ #
    #  Read — Single                                                       #
    # ------------------------------------------------------------------ #
    @staticmethod
    def get_one(opportunity_id: int, admin_id: int) -> Opportunity:
        """
        Fetch a single opportunity that belongs to *admin_id*.
        Raises ValueError if not found or not owned by the admin.
        """
        opp = db.session.get(Opportunity, opportunity_id)
        if not opp or opp.admin_id != admin_id:
            raise ValueError("Opportunity not found.")
        return opp

    # ------------------------------------------------------------------ #
    #  Create                                                              #
    # ------------------------------------------------------------------ #
    @staticmethod
    def create(data: dict, admin_id: int) -> Opportunity:
        max_applicants = data.get("max_applicants")
        if max_applicants is not None and str(max_applicants).strip() != "":
            max_applicants = int(max_applicants)
        else:
            max_applicants = None

        opp = Opportunity(
            admin_id=admin_id,
            name=data["name"].strip(),
            duration=data["duration"].strip(),
            start_date=data["start_date"].strip(),
            description=data["description"].strip(),
            skills=data["skills"].strip(),
            category=data["category"].strip(),
            future_opportunities=data.get("future_opportunities", "").strip() or None,
            max_applicants=max_applicants,
        )
        db.session.add(opp)
        db.session.commit()
        logger.info("Opportunity created: id=%s admin_id=%s", opp.id, admin_id)
        return opp

    # ------------------------------------------------------------------ #
    #  Update                                                              #
    # ------------------------------------------------------------------ #
    @staticmethod
    def update(opportunity_id: int, data: dict, admin_id: int) -> Opportunity:
        opp = OpportunityService.get_one(opportunity_id, admin_id)

        max_applicants = data.get("max_applicants")
        if max_applicants is not None and str(max_applicants).strip() != "":
            max_applicants = int(max_applicants)
        else:
            max_applicants = None

        opp.name = data["name"].strip()
        opp.duration = data["duration"].strip()
        opp.start_date = data["start_date"].strip()
        opp.description = data["description"].strip()
        opp.skills = data["skills"].strip()
        opp.category = data["category"].strip()
        opp.future_opportunities = data.get("future_opportunities", "").strip() or None
        opp.max_applicants = max_applicants

        db.session.commit()
        logger.info("Opportunity updated: id=%s admin_id=%s", opp.id, admin_id)
        return opp

    # ------------------------------------------------------------------ #
    #  Delete                                                              #
    # ------------------------------------------------------------------ #
    @staticmethod
    def delete(opportunity_id: int, admin_id: int) -> None:
        opp = OpportunityService.get_one(opportunity_id, admin_id)
        db.session.delete(opp)
        db.session.commit()
        logger.info("Opportunity deleted: id=%s admin_id=%s", opportunity_id, admin_id)
