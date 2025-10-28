from pathlib import Path
import re
from sqlalchemy.orm import Session
from backend.models.font import Font, Family
from backend.scripts.subset import subset

# Dossier subset
SUBSET_DIR = Path(r"C:\Users\fredm\Code\Specimen\backend\subset")
SUBSET_DIR.mkdir(parents=True, exist_ok=True)

# Même sanitization que celle utilisée lors de la création des fichiers subset
def _sanitize_filename(name: str) -> str:
    name = re.sub(r"[<>:\\/|?*]", "-", name)
    name = re.sub(r"\s+", " ", name).strip()
    name = name.replace(" ", "-")
    name = re.sub(r"-+", "-", name)
    return name or "font"


def repair_missing_subsets(db: Session):
    families = db.query(Family).all()

    total = len(families)
    repaired = 0
    missing = 0
    failed = 0

    for fam in families:
        # Nom du fichier attendu
        sanitized_name = _sanitize_filename(fam.name or "font")
        expected_file = SUBSET_DIR / f"{sanitized_name}.woff2"

        if expected_file.exists():
            continue  # OK, rien à faire

        missing += 1
        print(f"[MISSING] Subset manquant pour famille '{fam.name}' (ID {fam.id})")

        # Si aucune font représentante
        if fam.representative_id is None:
            print(f"  └─ Aucun representative_id, impossible de régénérer.")
            continue

        font = db.query(Font).filter(Font.id == fam.representative_id).first()
        if not font:
            print(f"  └─ Police représentante introuvable dans la base (id={fam.representative_id})")
            # On pourrait également nettoyer representative_id ici
            db.query(Family).filter_by(id=fam.id).update({"representative_id": None})
            failed += 1
            continue

        font_path = Path(font.path)
        if not font_path.exists():
            print(f"  └─ Fichier source introuvable : {font_path}")
            db.query(Family).filter_by(id=fam.id).update({"representative_id": None})
            failed += 1
            continue

        # Tentative de régénération
        result = subset(font_path)
        if result and result.exists():
            print(f"  [OK] Subset recréé pour '{fam.name}' → {result.name}")
            repaired += 1
        else:
            print(f"  [FAIL] Subset échoué pour '{fam.name}'")
            db.query(Family).filter_by(id=fam.id).update({"representative_id": None})
            failed += 1

    db.commit()

    print("\n--- RAPPORT ---")
    print(f"Familles totales       : {total}")
    print(f"Subsets manquants      : {missing}")
    print(f"Subsets réparés        : {repaired}")
    print(f"Subsets échoués        : {failed}")

if __name__ == "__main__":
    from backend.core.db import SessionLocal

    with SessionLocal() as db:
        repair_missing_subsets(db)
