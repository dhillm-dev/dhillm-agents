from fastapi import FastAPI
from fastapi.responses import JSONResponse
from global_agents.agents import perf_tracker
from global_agents.memory import market_memory

app = FastAPI()


@app.get("/api/learn_state")
def learn_state():
    return JSONResponse({
        "performance": perf_tracker.get_stats(),
        "top_memory": market_memory.recall(20)
    })
