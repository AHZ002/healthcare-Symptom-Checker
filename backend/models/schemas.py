from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


# Request 

class SymptomRequest(BaseModel):
    symptoms: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Symptom description provided by the user"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"symptoms": "I have a severe headache, fever of 101F, and neck stiffness for 2 days"}
            ]
        }
    }


#  LLM Output Structure 

class Condition(BaseModel):
    name: str
    likelihood: str         # "High", "Moderate", "Low"
    description: str


class SymptomAnalysis(BaseModel):
    conditions: List[Condition]
    recommended_steps: List[str]
    urgency_level: str       # "Emergency", "High", "Moderate", "Low"
    disclaimer: str


# API Response

class SymptomResponse(BaseModel):
    id: int
    symptoms: str
    conditions: List[Condition]
    recommended_steps: List[str]
    urgency_level: str
    disclaimer: str
    created_at: datetime

    model_config = {"from_attributes": True}


# History Response

class HistoryResponse(BaseModel):
    total: int
    queries: List[SymptomResponse]