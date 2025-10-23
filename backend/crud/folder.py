from sqlalchemy.orm import Session
from backend.models.folder import Folder
from backend.schemas.folder import FolderCreate
from datetime import datetime, timezone
from pathlib import Path
import os

def get_folders(db: Session):
    return db.query(Folder).all()

def get_folder_by_id(db: Session, folder_id: int):
    return db.query(Folder).filter(Folder.id == folder_id).first()

def create_folder(db: Session, path: str):
    db_folder = Folder(path=path)
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)
    return db_folder

def delete_folder(db: Session, folder_id: int):
    db_folder = get_folder_by_id(db, folder_id)
    if db_folder:
        db.delete(db_folder)
        db.commit()
    return db_folder


def scan_folder(db: Session, folder_id: int):
    folder = get_folder_by_id(db, folder_id)
    if not folder:
        return None

    try:
        folder.status = "scanning"
        db.add(folder)
        db.commit()

        p = Path(folder.path)
        # Count files recursively; ignore errors
        count = 0
        for _root, _dirs, files in os.walk(p, topdown=True):
            count += len(files)

        folder.file_count = count
        folder.status = "idle"
        folder.error_message = None
    except Exception as e:
        folder.status = "error"
        folder.error_message = str(e)
    finally:
        folder.last_scan = datetime.now(tz=timezone.utc)
        folder.updated_at = datetime.now(tz=timezone.utc)
        db.add(folder)
        db.commit()
        db.refresh(folder)

    return folder


BASE = Path("C:/Users/fredm").resolve()
EXTENSION = [".ttf", ".otf", ".woff", ".woff2"]
def find_folder():
    return BASE