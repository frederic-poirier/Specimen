from pathlib import Path
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.core.db import get_db, SessionLocal
from backend.scripts.scan import scan
from backend.models.font import Font, Family

import time


router = APIRouter()



@router.get("/scan/path")
def scan_path(
    path: str = Query(..., description="Absolute path to folder to scan"),
    db: Session = Depends(get_db),
):
    p = Path(path)
    if not p.exists() or not p.is_dir():
        raise HTTPException(status_code=400, detail="Path must be an existing directory")
    scan(db, p)
 

@router.get("/fonts/representative")
def list_representative_fonts(db: Session = Depends(get_db)):
    pairs = (
        db.query(Family)
        .order_by(Family.name)
        .all()
    )
    return [
        {
            "id": fam.id,
            "name": fam.name
        }
        for (fam) in pairs
    ]

def _parse_since(s: str) -> datetime:
    try:
        if s.endswith("Z"):
            return datetime.fromisoformat(s[:-1]).replace(tzinfo=timezone.utc)
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid 'since' datetime format. Use ISO 8601, e.g. 2025-01-01T00:00:00Z")


@router.get("/fonts/recent")
def list_recent_fonts(
    since: str = Query(..., description="ISO 8601 datetime, e.g. 2025-01-01T00:00:00Z"),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    since_dt = _parse_since(since)
    rows = (
        db.query(Font)
        .filter(Font.created_at >= since_dt)
        .order_by(Font.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": f.id,
            "family_id": f.family_id,
            "full_name": f.full_name,
            "style_name": f.style_name,
            "path": f.path,
            "created_at": f.created_at,
        }
        for f in rows
    ]


@router.get("/fonts/data/{id}")
def get_font_by_id(id, db: Session = Depends(get_db)):
    rows = (db.query(Font).filter(Font.id == id)).all()
    return rows


@router.get("/fonts/family/{id}")
def get_family(id, db: Session = Depends(get_db)):
    rows = db.query(Font).filter(Font.family_id == id).all()
    return [
            {
                "id": f.id,
                "family_id": f.family_id,
                "full_name": f.full_name,
                "style_name": f.style_name,
                "path": f.path,
                "created_at": f.created_at,
            }
            for f in rows
        ]