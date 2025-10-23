from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FolderBase(BaseModel):
    path: str
    is_watching: bool = True


class FolderCreate(FolderBase):
    pass


class Folder(FolderBase):
    id: int
    file_count: int = 0
    status: str = "idle"
    error_message: Optional[str] = None
    last_scan: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
