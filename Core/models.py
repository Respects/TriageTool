from typing import Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import json


Outcome = Literal["Success", "NeedsReview"]
Status = Literal["New", "Processing", "Closed"]
Priority = Literal["High", "Medium", "Low"]


class TriageResult(BaseModel):
    priority: Literal["High", "Medium", "Low"]
    priority_reasoning: str
    case_summary: str


class StoredCase(BaseModel):
    case_id: str
    outcome: Outcome
    status: Status
    date_submitted: str
    date_updated: str
    raw_case: str

    priority: Optional[Priority] = None
    reasoning: Optional[str] = None
    summary: Optional[str] = None

    @classmethod
    def from_success(cls, case: dict, result: TriageResult) -> "StoredCase":
        now = datetime.now().isoformat()
        return cls(
            case_id=case["case_id"],
            outcome="Success",
            status="New",
            date_submitted=now,
            date_updated=now,
            raw_case=json.dumps(case),
            priority=result.priority,
            reasoning=result.priority_reasoning,
            summary=result.case_summary,
        )

    @classmethod
    def from_failure(cls, case: dict) -> "StoredCase":
        now = datetime.now().isoformat()
        return cls(
            case_id=case["case_id"],
            outcome="NeedsReview",
            status="New",
            date_submitted=now,
            date_updated=now,
            raw_case=json.dumps(case),
        )


class TriageLogEntry(BaseModel):
    case_id: str
    resulting_priority: Optional[Priority] = None
    outcome: Outcome
    source: str
    processing_duration: float


class StatusUpdate(BaseModel):
    status: Status

