from fastapi import APIRouter, HTTPException
from sqlalchemy import func

from database.connection import SessionLocal
from database.models import (
    Case,
    Entity,
    Evidence,
    Relationship,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("")
def get_dashboard():

    db = SessionLocal()

    try:

        total_cases = (
            db.query(func.count(Case.id))
            .scalar()
            or 0
        )

        active_cases = (
            db.query(func.count(Case.id))
            .filter(Case.status == "ACTIVE")
            .scalar()
            or 0
        )

        total_entities = (
            db.query(func.count(Entity.id))
            .scalar()
            or 0
        )

        total_evidence = (
            db.query(func.count(Evidence.id))
            .scalar()
            or 0
        )

        total_relationships = (
            db.query(func.count(Relationship.id))
            .scalar()
            or 0
        )

        case_type_rows = (
            db.query(
                Case.case_type,
                func.count(Case.id),
            )
            .group_by(Case.case_type)
            .all()
        )

        evidence_source_rows = (
            db.query(
                Evidence.evidence_type,
                func.count(Evidence.id),
            )
            .group_by(Evidence.evidence_type)
            .all()
        )

        recent_cases = (
            db.query(Case)
            .order_by(Case.created_at.desc())
            .limit(10)
            .all()
        )

        return {
            "status": "success",

            "statistics": {
                "total_cases": total_cases,
                "active_cases": active_cases,
                "total_entities": total_entities,
                "total_evidence": total_evidence,
                "total_relationships": total_relationships,
            },

            "case_types": [
                {
                    "type": case_type or "UNKNOWN",
                    "count": count,
                }
                for case_type, count in case_type_rows
            ],

            "evidence_sources": [
                {
                    "type": evidence_type or "UNKNOWN",
                    "count": count,
                }
                for evidence_type, count in evidence_source_rows
            ],

            "recent_cases": [
                {
                    "id": case.id,
                    "fir_number": case.fir_number,
                    "case_type": case.case_type,
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
                }
                for case in recent_cases
            ],
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to load dashboard: {str(e)}",
        )

    finally:
        db.close()