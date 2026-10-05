from fastapi import APIRouter, HTTPException

from api.analysis_service import (
    analyze_investigation,
    normalize_case_id,
)


router = APIRouter(
    prefix="/investigations",
    tags=["Analysis"],
)


# ============================================================
# COMPLETE INVESTIGATION ANALYSIS
# ============================================================

@router.post("/{case_id}/analyze")
def run_analysis(case_id: str):

    try:

        result = analyze_investigation(
            case_id
        )

        if not result["seed_people"]:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"No people found for "
                    f"investigation {case_id}"
                ),
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
            detail=str(e),
        )


# ============================================================
# REAL LAYER 1
# ============================================================

@router.get("/{case_id}/layer1")
def get_layer1_analysis(
    case_id: str,
):

    try:

        result = analyze_investigation(
            case_id
        )

        return {
            "status": "success",

            "case_id":
                result["case_id"],

            "layer": 1,

            "layer_name":
                "Target / Profile",

            "candidate_count":
                result[
                    "candidate_count"
                ],

            "overall_relevance_score":
                result[
                    "overall_relevance_score"
                ],

            "people":
                result[
                    "top_relevant_people"
                ],
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# REAL ANOMALY
# ============================================================

@router.get("/{case_id}/anomaly")
def get_anomaly_analysis(
    case_id: str,
):

    try:

        result = analyze_investigation(
            case_id
        )

        return {
            "status": "success",

            "case_id":
                result["case_id"],

            "anomaly":
                result.get(
                    "anomaly",
                    {
                        "present": False,
                        "indicator_count": 0,
                        "indicators": [],
                    },
                ),
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )