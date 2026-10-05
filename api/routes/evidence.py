from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from database.connection import SessionLocal
from database.models import Evidence, Case


router = APIRouter(
    prefix="/evidence",
    tags=["Evidence"],
)


class EvidenceCreate(BaseModel):
    id: str
    case_id: str
    evidence_type: str
    source: Optional[str] = None
    storage_path: Optional[str] = None
    extracted_text: Optional[str] = None
    file_hash: Optional[str] = None
    layer_id: Optional[str] = None


def serialize_evidence(evidence: Evidence):
    return {
        "id": evidence.id,
        "case_id": evidence.case_id,
        "evidence_type": evidence.evidence_type,
        "source": evidence.source,
        "storage_path": evidence.storage_path,
        "extracted_text": evidence.extracted_text,
        "file_hash": evidence.file_hash,
        "layer_id": evidence.layer_id,
        "created_at": (
            evidence.created_at.isoformat()
            if evidence.created_at
            else None
        ),
    }


@router.get("")
def get_evidence(case_id: Optional[str] = None):
    db = SessionLocal()

    try:
        query = db.query(Evidence)

        if case_id:
            query = query.filter(Evidence.case_id == case_id)

        evidence = (
            query
            .order_by(Evidence.created_at.desc())
            .all()
        )

        return {
            "status": "success",
            "count": len(evidence),
            "evidence": [
                serialize_evidence(item)
                for item in evidence
            ],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch evidence: {str(e)}",
        )

    finally:
        db.close()


@router.get("/{evidence_id}")
def get_single_evidence(evidence_id: str):
    db = SessionLocal()

    try:
        evidence = (
            db.query(Evidence)
            .filter(Evidence.id == evidence_id)
            .first()
        )

        if not evidence:
            raise HTTPException(
                status_code=404,
                detail=f"Evidence {evidence_id} not found",
            )

        return {
            "status": "success",
            "evidence": serialize_evidence(evidence),
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch evidence: {str(e)}",
        )

    finally:
        db.close()


@router.post("")
def create_evidence(payload: EvidenceCreate):
    db = SessionLocal()

    try:
        case = (
            db.query(Case)
            .filter(Case.id == payload.case_id)
            .first()
        )

        if not case:
            raise HTTPException(
                status_code=404,
                detail=f"Case {payload.case_id} not found",
            )

        existing = (
            db.query(Evidence)
            .filter(Evidence.id == payload.id)
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Evidence {payload.id} already exists",
            )

        evidence = Evidence(
            id=payload.id,
            case_id=payload.case_id,
            evidence_type=payload.evidence_type,
            source=payload.source,
            storage_path=payload.storage_path,
            extracted_text=payload.extracted_text,
            file_hash=payload.file_hash,
            layer_id=payload.layer_id,
        )

        db.add(evidence)
        db.commit()
        db.refresh(evidence)

        return {
            "status": "success",
            "message": "Evidence added successfully",
            "evidence": serialize_evidence(evidence),
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create evidence: {str(e)}",
        )

    finally:
        db.close()