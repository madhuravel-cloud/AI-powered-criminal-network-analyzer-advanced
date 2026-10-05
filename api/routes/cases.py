from fastapi import APIRouter, HTTPException
from sqlalchemy import func

from database.connection import SessionLocal
from database.models import (
    Case,
    Evidence,
    Relationship,
)
from database.neo4j_connection import driver


router = APIRouter(
    prefix="/cases",
    tags=["Cases"],
)


def normalize_case_id(case_id: str) -> str:
    if not case_id:
        raise ValueError("case_id is required")

    if case_id.startswith("case:"):
        return case_id

    return f"case:{case_id}"


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


@router.get("")
def get_cases():
    """
    Return all cases from PostgreSQL.
    """

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


@router.get("/{case_id}")
def get_case(case_id: str):
    """
    Return one case from PostgreSQL.
    """

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


@router.get("/relevant/{case_id}")
def get_relevant_cases(case_id: str):
    """
    Return cases connected to the selected FIR through
    shared people/entities in the Neo4j master graph.

    Flow:

        Selected Case
             ↓
        Evidence
             ↓
        Person
             ↓
        Other Evidence
             ↓
        Other Case

    The selected case itself is excluded.
    """

    try:
        normalized_case_id = normalize_case_id(case_id)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    query = """
    MATCH (seed:Case {id: $case_id})

    MATCH (seed)-[:BELONGS_TO]-(seed_evidence:Evidence)

    MATCH (seed_evidence)-[]-(person:Person)

    MATCH (person)-[]-(other_evidence:Evidence)

    MATCH (other_evidence)-[:BELONGS_TO]-(other_case:Case)

    WHERE other_case.id <> seed.id

    RETURN DISTINCT other_case.id AS case_id
    ORDER BY case_id
    """

    try:
        with driver.session() as session:
            result = session.run(
                query,
                case_id=normalized_case_id,
            )

            relevant_ids = [
                record["case_id"]
                for record in result
                if record["case_id"]
            ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to find relevant cases: {str(e)}",
        )

    if not relevant_ids:
        return {
            "status": "success",
            "seed_case": normalized_case_id,
            "count": 0,
            "cases": [],
        }

    db = SessionLocal()

    try:
        cases = (
            db.query(Case)
            .filter(Case.id.in_(relevant_ids))
            .order_by(Case.created_at.desc())
            .all()
        )

        case_map = {
            case.id: case
            for case in cases
        }

        ordered_cases = [
            case_map[case_id]
            for case_id in relevant_ids
            if case_id in case_map
        ]

        return {
            "status": "success",
            "seed_case": normalized_case_id,
            "count": len(ordered_cases),
            "cases": [
                serialize_case(db, case)
                for case in ordered_cases
            ],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load relevant case details: {str(e)}",
        )

    finally:
        db.close()