from datetime import datetime, timezone
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, HTTPException, Query
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from backend.core.db import get_db
from backend.models.font import Font, Family

router = APIRouter()

@router.get("/fonts/representative")
def list_representative_fonts(db: Session = Depends(get_db)):
    results = (
        db.query(
            Family.id,
            Family.name,
            func.count(Font.id).label("font_count"),
            func.group_concat(distinct(Font.format)).label("extensions"),
        )
        .join(Font, Family.id == Font.family_id)
        .group_by(Family.id, Family.name)
        .order_by(Family.name)
        .all()
    )

    return [
        {
            "id": r.id,
            "name": r.name,
            "font_count": r.font_count,
            "extensions": sorted(set(filter(None, (r.extensions or "").split(","))))
        }
        for r in results
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

@router.get("/font")
def get_local_font(path: str = Query(...)):
    # Remplacer les backslashes échappés en vrais chemins Windows
    normalized_path = path.replace("\\", "/")
    file = Path(normalized_path).resolve()

    print("➡️ Fichier demandé:", file)

    if not file.exists():
        raise HTTPException(status_code=404, detail=f"Font not found: {file}")

    if file.suffix.lower() not in [".ttf", ".otf", ".woff", ".woff2"]:
        raise HTTPException(status_code=400, detail=f"Invalid font extension: {file.suffix}")

    # Déterminer le bon type MIME
    mime_map = {
        ".ttf": "font/ttf",
        ".otf": "font/otf",
        ".woff": "font/woff",
        ".woff2": "font/woff2"
    }
    media_type = mime_map[file.suffix.lower()]

    return FileResponse(file, media_type=media_type)