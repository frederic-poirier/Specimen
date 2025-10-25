from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.core.db import SessionLocal
from backend.models.font import Font
from backend.scripts.group_fonts import group_fonts
from backend.scripts.extract_metadata import extract_metadata


FONT_EXTENSIONS = [".ttf", ".otf", ".woff", ".woff2"]


def scan_fonts_to_db(db: Session, input_path: Path):
    count = 0
    # Track seen sha1s to avoid duplicate inserts within the same batch
    seen_sha1s = {s for (s,) in db.query(Font.sha1).all()}

    for extension in FONT_EXTENSIONS:
        for font_path in input_path.rglob(f"*{extension}"):

            if font_path.name.startswith("._"):
                print(f"[skip] Resource fork: {font_path.name}")
                continue

            data = extract_metadata(font_path)
            if not data:
                continue

            sha = data["sha1"]
            if sha in seen_sha1s:
                # Already present in DB or added in this run; update timestamp if exists
                existing = db.query(Font).filter_by(sha1=sha).first()
                if existing:
                    existing.last_scan = datetime.now(timezone.utc)
                continue

            existing = db.query(Font).filter_by(sha1=sha).first()
            if existing:
                existing.last_scan = datetime.now(timezone.utc)
                seen_sha1s.add(sha)
            else:
                db.add(Font(**data))
                seen_sha1s.add(sha)
                count += 1
                print(f"[+] Added {font_path.name}")

                # Commit in batches to limit memory
                if count % 100 == 0:
                    db.commit()

    db.commit()
    print(f"[OK] Scan termine: {count} nouvelles polices ajoutees.")


if __name__ == "__main__":
    folder = Path(r"C:\\Users\\fredm\\Font\\Other")
    if not folder.exists():
        print(f"[!] Le dossier {folder} est introuvable.")
        raise SystemExit(1)

    with SessionLocal() as db:
        scan_fonts_to_db(db, folder)
        print("[..] Regroupement des familles en cours...")
        group_fonts(db)
        print("[OK] Regroupement termine.")

