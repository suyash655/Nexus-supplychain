from typing import List, Optional

from pydantic import BaseModel


class AnalysisTriggerResponse(BaseModel):
    status: str = "success"
    message: str
    task_id: Optional[str] = None

class RiskScoreResponse(BaseModel):
    supplier: str
    risk_score: float
    tier: str
    factors: List[str]
