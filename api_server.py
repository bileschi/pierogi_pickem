import os
import csv
import hmac
import hashlib
import base64
import time
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

SEASON = os.environ.get("FOOTBALL_SEASON", "2025_2026")
CSV_PATH = os.path.join(SEASON, "playoffs.csv")
SECRET = os.environ.get("PIEROGI_SECRET", "change-me")
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGINS] if ALLOWED_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PickSubmission(BaseModel):
    game_id: str
    week: int
    player: str
    pick: str
    token: str


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip('=')


def sign(payload: str) -> str:
    sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).digest()
    return b64url(sig)


def validate_token(token: str, player: str) -> None:
    try:
        parts = token.split(":")
        if len(parts) != 3:
            raise ValueError("bad token format")
        t_player, exp_str, sig = parts
        if t_player != player:
            raise ValueError("player mismatch")
        exp = int(exp_str)
        if exp < int(time.time()):
            raise ValueError("token expired")
        expected = sign(f"{t_player}:{exp}")
        if not hmac.compare_digest(sig, expected):
            raise ValueError("invalid signature")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {e}")


def compute_game_id(week: int, row: dict) -> str:
    return f"{week}:{row.get('prop_date','')}:{row.get('away_team','')}@{row.get('home_team','')}"


@app.get("/api/health")
async def health():
    return {"ok": True}


@app.post("/api/picks")
async def submit_pick(sub: PickSubmission):
    validate_token(sub.token, sub.player)

    # Load CSV rows
    if not os.path.exists(CSV_PATH):
        raise HTTPException(status_code=404, detail="CSV not found")

    with open(CSV_PATH, "r", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    # Ensure player column exists
    player_col = f"{sub.player}_pick"
    if player_col not in fieldnames:
        raise HTTPException(status_code=400, detail=f"Unknown player '{sub.player}'")

    # Find target row by computed game_id
    target_idx: Optional[int] = None
    for idx, row in enumerate(rows):
        week = int(row.get("week", 0) or 0)
        gid = compute_game_id(week, row)
        if gid == sub.game_id and week == sub.week:
            target_idx = idx
            break
    if target_idx is None:
        raise HTTPException(status_code=404, detail="Game not found")

    # Update pick (store MANUAL marker)
    rows[target_idx][player_col] = f"{sub.pick} MANUAL"

    # Write back CSV atomically
    tmp_path = CSV_PATH + ".tmp"
    with open(tmp_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp_path, CSV_PATH)

    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
