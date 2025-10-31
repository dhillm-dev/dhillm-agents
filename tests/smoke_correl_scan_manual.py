from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from api.correl_scan import app

if __name__ == "__main__":
    c = TestClient(app)
    r = c.get("/api/correl_scan")
    print("status:", r.status_code)
    print(r.text)
