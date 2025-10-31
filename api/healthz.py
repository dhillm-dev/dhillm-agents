from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/api/healthz")
def healthz():
    return JSONResponse({"ok": True})
