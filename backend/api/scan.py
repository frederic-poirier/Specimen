from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.core.db import get_db
from backend.scripts.scan import scan

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
