import json, pathlib

def test_vercel_json():
    p = pathlib.Path("vercel.json"); assert p.exists(), "vercel.json missing"
    cfg = json.loads(p.read_text())
    assert "functions" in cfg and "routes" in cfg, "functions/routes missing"
