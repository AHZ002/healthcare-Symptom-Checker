import json
from sqlalchemy.orm import Session
from backend.database.db import SymptomQuery
from backend.models.schemas import SymptomAnalysis


def save_query(db: Session, symptoms: str, analysis: SymptomAnalysis) -> SymptomQuery:
    """Save a symptom query and its LLM analysis to the database."""
    record = SymptomQuery(
        symptoms          = symptoms,
        conditions        = json.dumps([c.model_dump() for c in analysis.conditions]),
        recommended_steps = json.dumps(analysis.recommended_steps),
        urgency_level     = analysis.urgency_level,
        disclaimer        = analysis.disclaimer
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_all_queries(db: Session, limit: int = 50) -> list[SymptomQuery]:
    """Retrieve the most recent queries, newest first."""
    return (
        db.query(SymptomQuery)
        .order_by(SymptomQuery.created_at.desc())
        .limit(limit)
        .all()
    )


def format_record(record: SymptomQuery) -> dict:
    """
    Convert a DB record into a dict matching SymptomResponse schema.
    Deserializes JSON strings back into Python lists.
    """
    return {
        "id":                record.id,
        "symptoms":          record.symptoms,
        "conditions":        json.loads(record.conditions),
        "recommended_steps": json.loads(record.recommended_steps),
        "urgency_level":     record.urgency_level,
        "disclaimer":        record.disclaimer,
        "created_at":        record.created_at
    }