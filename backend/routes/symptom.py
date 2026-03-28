import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.database.crud import save_query, get_all_queries, format_record
from backend.models.schemas import SymptomRequest, SymptomResponse, HistoryResponse
from backend.services.llm_service import analyze_symptoms

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Symptom Checker"])


# POST /api/v1/check-symptoms

@router.post(
    "/check-symptoms",
    response_model=SymptomResponse,
    summary="Analyze symptoms and return probable conditions",
    description="Accepts a symptom description and returns possible conditions, "
                "recommended next steps, and urgency level. For educational purposes only."
)
async def check_symptoms(request: SymptomRequest, db: Session = Depends(get_db)):
    """
    Accepts symptom text, queries the LLM, saves to DB, returns structured analysis.
    """
    logger.info(f"Received symptom check request | length={len(request.symptoms)} chars")

    try:
        analysis = analyze_symptoms(request.symptoms)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again.")

    try:
        record = save_query(db, request.symptoms, analysis)
    except Exception as e:
        logger.error(f"Failed to save query to database: {e}")
        raise HTTPException(status_code=500, detail="Failed to save results. Please try again.")

    return SymptomResponse(**format_record(record))


# GET /api/v1/history

@router.get(
    "/history",
    response_model=HistoryResponse,
    summary="Retrieve past symptom queries",
    description="Returns the most recent symptom analyses stored in the database."
)
async def get_history(db: Session = Depends(get_db)):
    """
    Fetches all past queries from the database, newest first.
    """
    try:
        records = get_all_queries(db)
        formatted = [format_record(r) for r in records]
        return HistoryResponse(total=len(formatted), queries=formatted)
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history.")