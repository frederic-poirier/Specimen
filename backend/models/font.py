from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    ForeignKey, JSON, Float
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.core.db import Base


class Font(Base):
    __tablename__ = "fonts"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(512), unique=True, nullable=False)
    sha1 = Column(String(64), unique=True, nullable=False)

    full_name = Column(String)
    style_name = Column(String)
    format = Column(String)

    # Relation avec la famille
    family_id = Column(Integer, ForeignKey("families.id"), index=True)

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

    # Timestamps et état
    status = Column(String, default="ok")
    last_scan = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc)
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc)
    )

    # Relation ORM inverse (accès Font.family)
    family = relationship("Family", back_populates="fonts", foreign_keys=[family_id])


class Family(Base):
    __tablename__ = "families"  # nom en minuscules et pluriel par convention

    id = Column(Integer, primary_key=True, index=True)

    # Informations communes aux fonts
    name = Column(String, index=True)
    name_normalized = Column(String, index=True)
    license = Column(String, nullable=True)
    vendor = Column(String, nullable=True)
    panose = Column(JSON, nullable=True)
    code_page1 = Column(Integer, nullable=True)
    code_page2 = Column(Integer, nullable=True)
    glyph_count = Column(Integer, nullable=True)

    # Identifiant de la font représentante
    representative_id = Column(Integer, ForeignKey("fonts.id"), nullable=True)

    # Métadonnées et timestamps
    status = Column(String, default="ok")
    last_scan = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc)
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc)
    )

    # Relations ORM
    fonts = relationship(
        "Font",
        back_populates="family",
        cascade="all, delete-orphan",
        foreign_keys=[Font.family_id],
    )
    representative = relationship("Font", foreign_keys=[representative_id], uselist=False)
