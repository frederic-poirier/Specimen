from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.schemas.folder import Folder, FolderCreate
from backend.crud import folder as crud
from backend.core.db import get_db
from pathlib import Path

router = APIRouter(prefix="/folders", tags=["Folders"])

@router.get("/", response_model=list[Folder])
def list_folders(db: Session = Depends(get_db)):
    return crud.get_folders(db)

@router.post("/")
def add_folder(path: str = Query(...),  db: Session = Depends(get_db)):
    return crud.create_folder(db, path)

@router.delete("/{folder_id}", response_model=Folder)
def remove_folder(folder_id: int, db: Session = Depends(get_db)):
    folder = crud.delete_folder(db, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder


@router.post("/{folder_id}/scan", response_model=Folder)
def scan_folder(folder_id: int, db: Session = Depends(get_db)):
    folder = crud.scan_folder(db, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder



BASE_DIR = Path("C:/Users/fredm").resolve()
@router.get("/validate")
def validate_folder(path: str = Query(...)):
    if not path.strip():
        return {"valid": False, "error": "Path is empty"}

    try:
        input_path = Path(path).expanduser()

        # Cas 1 : chemin relatif -> on le combine à BASE_DIR
        if not input_path.is_absolute():
            p = (BASE_DIR / input_path).resolve(strict=False)
        else:
            # Cas 2 : chemin absolu -> on résout directement
            p = input_path.resolve(strict=False)

    except Exception as e:
        return {"valid": False, "error": f"Invalid path: {str(e)}"}

    # Optionnel : sécurité — le chemin final doit être dans BASE_DIR
    if BASE_DIR not in p.parents and p != BASE_DIR:
        return {"valid": False, "error": "Path is outside the allowed base directory"}

    if not p.exists():
        return {"valid": False, "error": "Path does not exist", "path": str(p)}

    if not p.is_dir():
        return {"valid": False, "error": "Path is not a directory"}

    try:
        _ = next(p.iterdir(), None)
    except PermissionError:
        return {"valid": False, "error": "Directory is not readable"}

    return {"valid": True, "path": str(p)}
