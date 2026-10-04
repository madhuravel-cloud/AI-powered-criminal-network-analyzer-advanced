from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Case
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/cases",
    tags=["Cases"],
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


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
                {
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
                }
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
            "case": {
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
            },
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