"""Endpoints for managing instructor availability slots."""

from fastapi import APIRouter, HTTPException, Response

from app.api.deps.types import CurrentInstrutor, DbSession
from app.schemas.common import success_response
from app.schemas.slot import SlotCreateRequest, SlotResource
from app.services.slot_service import SlotOverlapError, SlotService

router = APIRouter(tags=["Slots"])


@router.post("/instructors/me/slots", status_code=201)
def create_slot(
    body: SlotCreateRequest,
    current_user: CurrentInstrutor,
    db: DbSession,
) -> Response:
    """Create an available one-hour slot for the calling instructor.

    Requires the INSTRUTOR role. The slot must start in the future and last exactly
    one hour (422 otherwise). Returns 409 when it overlaps an existing slot.
    """
    service = SlotService(db)
    try:
        slot = service.create_slot(
            instructor_id=current_user.user_id,
            starts_at=body.starts_at,
            ends_at=body.ends_at,
        )
        db.commit()
        return success_response(
            SlotResource.model_validate(slot).model_dump(mode="json"),
            meta={},
            status_code=201,
        )
    except SlotOverlapError as e:
        raise HTTPException(
            status_code=409, detail={"code": "SLOT_OVERLAP", "message": str(e)}
        ) from e


@router.get("/instructors/me/slots")
def list_my_slots(
    current_user: CurrentInstrutor,
    db: DbSession,
) -> Response:
    """List the calling instructor's slots ordered by start time.

    Requires the INSTRUTOR role.
    """
    service = SlotService(db)
    slots = service.list_slots(current_user.user_id)
    return success_response(
        [SlotResource.model_validate(s).model_dump(mode="json") for s in slots],
        meta={"total": len(slots)},
    )


@router.get("/instructors/{instructor_id}/slots")
def list_instructor_slots(
    instructor_id: str,
    db: DbSession,
) -> Response:
    """List an instructor's slots of any status, ordered by start time.

    Public. The instructor may be identified by public slug or ID.
    """
    service = SlotService(db)
    slots = service.list_slots(instructor_id, status=None)
    return success_response(
        [SlotResource.model_validate(s).model_dump(mode="json") for s in slots],
        meta={"total": len(slots)},
    )


@router.delete("/instructors/me/slots/{slot_id}", status_code=200)
def delete_slot(
    slot_id: str,
    current_user: CurrentInstrutor,
    db: DbSession,
) -> Response:
    """Delete one of the calling instructor's slots.

    Requires the INSTRUTOR role. Returns 400 when the slot does not belong to the
    caller, does not exist, or is reserved by a booking.
    """
    service = SlotService(db)
    try:
        service.delete_slot(current_user.user_id, slot_id)
        db.commit()
        return success_response({"deleted": True}, meta={})
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail={"code": "SLOT_DELETE_ERROR", "message": str(e)}
        ) from e
