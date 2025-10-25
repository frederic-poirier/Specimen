from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.core.db import get_db
from backend.scripts.scan_fonts import scan_fonts_to_db
from backend.models.font import Font


router = APIRouter()


@router.get("/scan/path")
def scan_path(path: str = Query(..., description="Absolute path to folder to scan"),
              db: Session = Depends(get_db)):
    p = Path(path)
    if not p.exists() or not p.is_dir():
        raise HTTPException(status_code=400, detail="Path must be an existing directory")

    try:
        scan_fonts_to_db(db, p)
        return {"success": True}
    except Exception as e:
        # Minimal error surface as requested
        return {"success": False, "error": str(e)}


@router.get("/fonts/representative")
def list_representative_fonts(db: Session = Depends(get_db)):
    reps = db.query(Font).filter_by(representative=True).all()
    # Minimal payload to demonstrate functionality
    return [
        {
            "id": f.id,
            "family": f.family,
            "full_name": f.full_name,
            "style_name": f.style_name,
            "path": f.path,
        }
        for f in reps
    ]


@router.get("/fonts/family/{font_id}")
def list_family(font_id: int, db: Session = Depends(get_db)):
    # Find the clicked font to identify its normalized family
    font = db.query(Font).filter_by(id=font_id).first()
    if not font:
        raise HTTPException(status_code=404, detail="Font not found")

    fam_norm = font.family_normalized
    if not fam_norm:
        # Fallback: return just the single font if no family info available
        return [{
            "id": font.id,
            "family": font.family,
            "full_name": font.full_name,
            "style_name": font.style_name,
            "path": font.path,
        }]

    members = (
        db.query(Font)
        .filter_by(family_normalized=fam_norm)
        .order_by(Font.full_name.asc())
        .all()
    )
    return [
        {
            "id": f.id,
            "family": f.family,
            "full_name": f.full_name,
            "style_name": f.style_name,
            "path": f.path,
            "representative": f.representative,
        }
        for f in members
    ]
