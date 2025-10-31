from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from api.retrain_now import app

if __name__ == "__main__":
    c = TestClient(app)
    r = c.get("/api/retrain_now")
    print("status:", r.status_code)
    print(r.text)
