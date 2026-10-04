from fastapi import APIRouter, HTTPException
from sqlalchemy import func

from database.connection import SessionLocal
from database.models import (
    Case,
    Evidence,
    Relationship,
)


router = APIRouter(
    prefix="/cases",
    tags=["Cases"],
)


# =========================================================
# SERIALIZE CASE
# =========================================================

def serialize_case(db, case):

    evidence_count = (
        db.query(func.count(Evidence.id))
        .filter(Evidence.case_id == case.id)
        .scalar()
        or 0
    )

    relationship_count = (
        db.query(func.count(Relationship.id))
        .filter(Relationship.case_id == case.id)
        .scalar()
        or 0
    )

    return {
        "id": case.id,

        "fir_number": case.fir_number,

        "case_type": case.case_type,

        "police_station": case.police_station,

        "incident_date": (
            case.incident_date.isoformat()
            if case.incident_date
            else None
        ),

        "registered_date": (
            case.registered_date.isoformat()
            if case.registered_date
            else None
        ),

        "status": case.status,

        "created_at": (
            case.created_at.isoformat()
            if case.created_at
            else None
        ),

        "evidence_count": evidence_count,

        "relationship_count": relationship_count,
    }


# =========================================================
# GET ALL CASES
# =========================================================

@router.get("")
def get_cases():

    db = SessionLocal()

    try:

        cases = (
            db.query(Case)
            .order_by(Case.created_at.desc())
            .all()
        )

        return {
            "status": "success",
            "count": len(cases),
            "cases": [
                serialize_case(db, case)
                for case in cases
            ],
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch cases: {str(e)}",
        )

    finally:

        db.close()


# =========================================================
# GET SINGLE CASE
# =========================================================

@router.get("/{case_id}")
def get_case(case_id: str):

    db = SessionLocal()

    try:

        case = (
            db.query(Case)
            .filter(Case.id == case_id)
            .first()
        )

        if not case:

            raise HTTPException(
                status_code=404,
                detail=f"Case {case_id} not found",
            )

        return {
            "status": "success",
            "case": serialize_case(db, case),
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch case: {str(e)}",
        )

    finally:

        db.close()