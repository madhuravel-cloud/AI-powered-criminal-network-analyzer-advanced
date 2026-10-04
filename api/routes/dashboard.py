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

        # =====================================================
        # BASIC COUNTS
        # =====================================================

        total_cases = (
            db.query(func.count(Case.id))
            .scalar()
            or 0
        )

        total_people = (
            db.query(func.count(Entity.id))
            .filter(Entity.entity_type == "PERSON")
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

        # =====================================================
        # ACTIVE CASES
        # =====================================================

        active_cases = (
            db.query(func.count(Case.id))
            .filter(Case.status == "ACTIVE")
            .scalar()
            or 0
        )

        # =====================================================
        # CASE TYPE BREAKDOWN
        # =====================================================

        case_types = (
            db.query(
                Case.case_type,
                func.count(Case.id),
            )
            .group_by(Case.case_type)
            .all()
        )

        case_type_breakdown = [
            {
                "type": case_type or "UNKNOWN",
                "count": count,
            }
            for case_type, count in case_types
        ]

        # =====================================================
        # EVIDENCE SOURCE BREAKDOWN
        # =====================================================

        evidence_types = (
            db.query(
                Evidence.evidence_type,
                func.count(Evidence.id),
            )
            .group_by(Evidence.evidence_type)
            .all()
        )

        evidence_breakdown = [
            {
                "type": evidence_type or "UNKNOWN",
                "count": count,
            }
            for evidence_type, count in evidence_types
        ]

        # =====================================================
        # RECENT CASES
        # =====================================================

        recent_cases = (
            db.query(Case)
            .order_by(Case.created_at.desc())
            .limit(5)
            .all()
        )

        recent_case_data = []

        for case in recent_cases:

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

            recent_case_data.append(
                {
                    "id": case.id,
                    "fir_number": case.fir_number,
                    "case_type": case.case_type,
                    "police_station": case.police_station,
                    "status": case.status,
                    "incident_date": (
                        case.incident_date.isoformat()
                        if case.incident_date
                        else None
                    ),
                    "created_at": (
                        case.created_at.isoformat()
                        if case.created_at
                        else None
                    ),
                    "evidence_count": evidence_count,
                    "relationship_count": relationship_count,
                }
            )

        # =====================================================
        # RESPONSE
        # =====================================================

        return {
            "status": "success",

            "statistics": {
                "total_cases": total_cases,
                "active_cases": active_cases,
                "total_people": total_people,
                "total_entities": total_entities,
                "total_evidence": total_evidence,
                "total_relationships": total_relationships,
            },

            "case_types": case_type_breakdown,

            "evidence_sources": evidence_breakdown,

            "recent_cases": recent_case_data,
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch dashboard data: {str(e)}",
        )

    finally:

        db.close()