from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional
from global_agents.state import get_last_decision, set_last_decision

router = APIRouter()

@router.get("/api/last_decision")
def read_last():
    return JSONResponse({"last_decision": get_last_decision()})

@router.post("/api/last_decision")
async def upsert_last(req: Request):
    """
    Body examples:
      {"ok":true,"decision":{"action":"BUY","symbol":"EURUSD=X","volume":"0.02"}}
      {"ok":true,"decision":null}  # clears
    """
    try:
        body: Dict[str, Any] = await req.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "invalid json"}, status_code=400)

    decision: Optional[Dict[str, Any]] = body.get("decision", None)
    # light validation
    if decision is not None and not isinstance(decision, dict):
        return JSONResponse({"ok": False, "error": "decision must be object or null"}, status_code=400)

    set_last_decision(decision)
    return JSONResponse({"ok": True})