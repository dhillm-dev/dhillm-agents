from fastapi import FastAPI
from fastapi.responses import JSONResponse
from global_agents.learn.retrainer import retrain

app = FastAPI()


@app.get("/api/retrain_now")
def retrain_now():
    try:
        res = retrain()
        return JSONResponse({"ok": True, **res})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
