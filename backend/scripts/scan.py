from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.models.font import Font, Family
from backend.scripts.group import group
from backend.scripts.extract import extract
from backend.scripts.representative import representative, representative_fallback
from backend.scripts.subset import subset


FONT_EXTENSIONS = [".ttf", ".otf", ".woff", ".woff2", ".svg"]

class SHA1Cache:
    def __init__(self, db: Session, threshold: int = 1000):
        self.db = db
        self.threshold = threshold
        self.cache = None
        self.use_cache = False

    def initialize(self, total_fonts: int):
        if total_fonts > self.threshold:
            self.cache = {s for (s,) in self.db.query(Font.sha1).all()}
            self.use_cache = True
        else:
            self.use_cache = False

    def has(self, sha1: str) -> bool:
        if self.use_cache:
            return sha1 in self.cache
        return (
            self.db.query(Font.id)
            .filter(Font.sha1 == sha1)
            .limit(1)
            .scalar()
            is not None
        )
    
    def add(self, sha1: str):
        if self.use_cache:
            self.cache.add(sha1)


def scan(db: Session, input_path: Path):
    print('received')
    font_paths = [p for ext in FONT_EXTENSIONS for p in input_path.rglob(f"*{ext}")]
    total_fonts = len(font_paths)

    sha_cache = SHA1Cache(db)
    sha_cache.initialize(total_fonts)
    
    families_cache = {
        (f.name_normalized, f.vendor, tuple(f.panose or [])): {
            "id": f.id,
            "representative_id": f.representative_id,
            "vendor": f.vendor,
            "panose": f.panose,
            "name_normalized": f.name_normalized,
        }
        for f in db.query(Family).all()
    }

    rep_rows = db.query(Family.id, Family.representative_id).all()
    representative_cache = {fid: rid for (fid, rid) in rep_rows}

    count = 0
    for font_path in font_paths:
        if font_path.name.startswith("._"):
            print(f"[skip] Resource fork: {font_path.name}")
            continue

        data = extract(font_path)
        if not data:
            continue

        sha = data["sha1"]
        if sha_cache.has(sha):
            existing = db.query(Font).filter_by(sha1=sha).first()
            if existing:
                existing.last_scan = datetime.now(timezone.utc)
            continue

        family_key, is_new_family = group(data, families_cache)

        if is_new_family:
            new_family = Family(
                name=data["family"],
                name_normalized=data["family_normalized"],
                vendor=data.get("vendor"),
                panose=data.get("panose"),
                code_page1=data.get("code_page1"),
                code_page2=data.get("code_page2"),
                glyph_count=data.get("glyph_count"),
            )
            db.add(new_family)
            db.flush()

            families_cache[family_key]["id"] = new_family.id
            family_id = new_family.id
        else:
            family_id = families_cache[family_key]["id"]

        # Map only valid fields for Font ORM
        allowed_keys = {
            "path",
            "sha1",
            "format",
            "full_name",
            "style_name",
            "weight_class",
            "width_class",
            "units_per_em",
            "ascender",
            "descender",
            "line_gap",
            "x_height",
            "cap_height",
            "italic_angle",
        }
        font_data = {k: data.get(k) for k in allowed_keys}
        font_obj = Font(family_id=family_id, **font_data)
        db.add(font_obj)
        db.flush()

        if representative(font_obj, families_cache[family_key], representative_cache):
            families_cache[family_key]["representative_id"] = font_obj.id
            representative_cache[family_id] = font_obj.id
            db.query(Family).filter_by(id=family_id).update(
                {"representative_id": font_obj.id}
            )
            subset(Path(font_obj.path))

        sha_cache.add(sha)
        
        count += 1
        if count % 100 == 0:
            db.commit()
    
    representative_fallback(db, families_cache)
    db.commit()
