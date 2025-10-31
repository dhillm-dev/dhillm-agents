from pathlib import Path

REQ = [l.strip() for l in Path("requirements.txt").read_text().splitlines() if l.strip() and not l.strip().startswith("#")]

def test_no_duplicate_pins():
    seen = {}
    for line in REQ:
        name = line.split("==")[0].strip().lower()
        seen[name] = seen.get(name,0)+1
    dups = [k for k,v in seen.items() if v>1]
    assert not dups, f"Duplicate pins: {dups}"

def test_required_present():
    need = {"fastapi","pydantic","uvicorn","ta","pandas","numpy","yfinance","requests"}
    have = {l.split("==")[0].strip().lower() for l in REQ if "==" in l}
    missing = need - have
    assert not missing, f"Missing pins: {missing}"
