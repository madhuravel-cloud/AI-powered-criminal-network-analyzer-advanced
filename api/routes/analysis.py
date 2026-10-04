from fastapi import APIRouter, HTTPException

from api.analysis_service import analyze_investigation


router = APIRouter(
    prefix="/investigations",
    tags=["Analysis"],
)


@router.post("/{case_id}/analyze")
def run_analysis(case_id: str):

    try:
        result = analyze_investigation(case_id)

        if not result["seed_people"]:
            raise HTTPException(
                status_code=404,
                detail=f"No people found for investigation {case_id}"
            )

        return {
            "status": "success",
            "analysis": result,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )