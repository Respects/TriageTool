from fastapi import FastAPI, HTTPException
from triage import triage_case
from Core.models import TriageLogEntry, StoredCase
from Data.database import save_case, save_log, get_all_cases, update_case_status
from Core.models import StatusUpdate
import time

app = FastAPI()


@app.get("/cases")
def list_cases():
    return get_all_cases()


@app.patch("/cases/{case_id}/status")
def set_case_status(case_id: str, update: StatusUpdate):
    updated = update_case_status(case_id, update.status)
    if updated == 0:
        raise HTTPException(status_code=404, detail=f"No case with id {case_id}")
    return {"case_id": case_id, "status": update.status}


@app.post("/triage")
def triage_endpoint(case: dict):
    start = time.perf_counter()
    result = triage_case(case)
    duration = round(time.perf_counter() - start, 3)


    if result is None:
        save_case(StoredCase.from_failure(case))
        raise HTTPException(status_code=422, detail={"message": "Triage failed — needs manual review",
                                                     "processing_duration": duration, "case_id": case["case_id"]})

    save_case(StoredCase.from_success(case, result))
    return {**result.model_dump(), "processing_duration": duration, "case_id": case["case_id"]}


@app.post("/log")
def log_endpoint(entry: TriageLogEntry):
    save_log(entry)
    return {"status": "logged"}