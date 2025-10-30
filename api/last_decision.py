from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from global_agents.state import get_last_decision, set_last_decision

app = FastAPI()

@app.get("/api/last_decision")
def read_last():
    return {"last_decision": get_last_decision()}

@app.post("/api/last_decision")
async def write_last(req: Request):
    body = await req.json()
    set_last_decision(body.get("decision"))
    return JSONResponse({"ok": True})