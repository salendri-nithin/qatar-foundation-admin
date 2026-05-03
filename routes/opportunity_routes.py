import logging

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import OpportunityService
from utils.validators import validate_opportunity_payload
from utils.responses import success_response, error_response

logger = logging.getLogger(__name__)
opportunity_bp = Blueprint("opportunities", __name__, url_prefix="/api/opportunities")


def _current_admin_id() -> int:
    """Helper: extract the integer admin ID from the JWT."""
    return int(get_jwt_identity())


# --------------------------------------------------------------------------- #
#  GET /api/opportunities                                                       #
# --------------------------------------------------------------------------- #
@opportunity_bp.route("", methods=["GET"])
@jwt_required()
def get_all():
    try:
        admin_id = _current_admin_id()
        opportunities = OpportunityService.get_all(admin_id)

        if not opportunities:
            return success_response(
                "You haven't created any opportunities yet.",
                data=[],
            )

        return success_response(
            f"{len(opportunities)} opportunity/ies found.",
            data=[opp.to_dict() for opp in opportunities],
        )

    except Exception:
        logger.exception("Error fetching opportunities")
        return error_response("Failed to retrieve opportunities.", 500)


# --------------------------------------------------------------------------- #
#  POST /api/opportunities                                                      #
# --------------------------------------------------------------------------- #
@opportunity_bp.route("", methods=["POST"])
@jwt_required()
def create():
    try:
        admin_id = _current_admin_id()
        data = request.get_json(silent=True) or {}

        error = validate_opportunity_payload(data)
        if error:
            return error_response(error, 422)

        opp = OpportunityService.create(data, admin_id)
        return success_response("Opportunity created successfully.", data=opp.to_dict(), status=201)

    except Exception:
        logger.exception("Error creating opportunity")
        return error_response("Failed to create opportunity.", 500)


# --------------------------------------------------------------------------- #
#  GET /api/opportunities/<id>                                                  #
# --------------------------------------------------------------------------- #
@opportunity_bp.route("/<int:opportunity_id>", methods=["GET"])
@jwt_required()
def get_one(opportunity_id: int):
    try:
        admin_id = _current_admin_id()
        opp = OpportunityService.get_one(opportunity_id, admin_id)
        return success_response("Opportunity retrieved.", data=opp.to_dict())

    except ValueError as exc:
        return error_response(str(exc), 404)
    except Exception:
        logger.exception("Error retrieving opportunity id=%s", opportunity_id)
        return error_response("Failed to retrieve opportunity.", 500)


# --------------------------------------------------------------------------- #
#  PUT /api/opportunities/<id>                                                  #
# --------------------------------------------------------------------------- #
@opportunity_bp.route("/<int:opportunity_id>", methods=["PUT"])
@jwt_required()
def update(opportunity_id: int):
    try:
        admin_id = _current_admin_id()
        data = request.get_json(silent=True) or {}

        error = validate_opportunity_payload(data)
        if error:
            return error_response(error, 422)

        opp = OpportunityService.update(opportunity_id, data, admin_id)
        return success_response("Opportunity updated successfully.", data=opp.to_dict())

    except ValueError as exc:
        return error_response(str(exc), 404)
    except Exception:
        logger.exception("Error updating opportunity id=%s", opportunity_id)
        return error_response("Failed to update opportunity.", 500)


# --------------------------------------------------------------------------- #
#  DELETE /api/opportunities/<id>                                               #
# --------------------------------------------------------------------------- #
@opportunity_bp.route("/<int:opportunity_id>", methods=["DELETE"])
@jwt_required()
def delete(opportunity_id: int):
    try:
        admin_id = _current_admin_id()
        OpportunityService.delete(opportunity_id, admin_id)
        return success_response("Opportunity deleted successfully.")

    except ValueError as exc:
        return error_response(str(exc), 404)
    except Exception:
        logger.exception("Error deleting opportunity id=%s", opportunity_id)
        return error_response("Failed to delete opportunity.", 500)
