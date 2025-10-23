from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone
from backend.core.db import Base

class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, nullable=False)
    is_watching = Column(Boolean, default=True)
    
    file_count = Column(Integer, default=0)
    
    status = Column(String, default="idle")
    error_message = Column(String, nullable=True)

    last_scan = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc))
