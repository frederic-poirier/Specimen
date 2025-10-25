from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Float
from datetime import datetime, timezone
from backend.core.db import Base

class Font(Base):
    __tablename__ = "fonts"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(512), unique=True, nullable=False)
    sha1 = Column(String(64), unique=True, nullable=False)

    # Identification
    family = Column(String)
    family_normalized = Column(String)
    full_name = Column(String)
    style_name = Column(String)  # Nom de style ("Regular", "Bold Italic")
    format = Column(String)

    # Licence / Vendor
    license = Column(String)
    vendor = Column(String)

    # Panose + tables techniques
    panose = Column(JSON)
    code_page1 = Column(Integer)
    code_page2 = Column(Integer)

    # Glyph info
    glyph_count = Column(Integer)

    # Style metrics
    weight_class = Column(Integer)
    width_class = Column(Integer)
    units_per_em = Column(Integer)
    ascender = Column(Integer)
    descender = Column(Integer)
    line_gap = Column(Integer)
    x_height = Column(Integer, nullable=True)
    cap_height = Column(Integer, nullable=True)
    italic_angle = Column(Float, nullable=True)

    # Gestion
    representative = Column(Boolean, default=False)  # un seul true par famille
    
    status = Column(String, default="ok")
    last_scan = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc)
    )
