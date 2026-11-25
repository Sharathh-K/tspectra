from datetime import date as Date
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException

from api.schemas import RiskScene

app = FastAPI(title="TerraSpectra mock field API")
SCENE = Path(__file__).resolve().parents[1] / "data/mock/mock_risk.json"


@lru_cache(maxsize=1)
def load_scene():
    return RiskScene.model_validate_json(SCENE.read_bytes())


@app.get("/risk", response_model=RiskScene)
def get_risk(date: Date | None = None):
    scene = load_scene()
    if date is not None and date != scene.date:
        raise HTTPException(status_code=404, detail="No mock acquisition for this date")
    return scene
