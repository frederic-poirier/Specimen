from pathlib import Path
from sqlalchemy.orm import Session
from backend.models.font import Family, Font
from backend.scripts.subset import subset



EXCLUDED_KEYWORDS = [
    "italic", "oblique", "wide", "expanded", "extended", 
    "condensed", "narrow", "compressed"
]


def is_clean_style(style_name: str | None) -> bool:
    if not style_name:
        return True
    s = style_name.lower()
    return not any(kw in s for kw in EXCLUDED_KEYWORDS)

def is_regular_candidate(font_obj) -> bool:
    if font_obj.weight_class == 400 and is_clean_style(font_obj.style_name):
        return True
    
    if font_obj.style_name and font_obj.style_name.strip().lower() == "regular":
        return True
    
    return False


def representative(font_obj, family_entry, representative_cache) -> bool:
    family_id = family_entry.get("id")
    
    if family_entry.get("representative_id") or representative_cache.get(family_id):
        return False
    
    if is_regular_candidate(font_obj):
        family_entry["representative_id"] = font_obj.id
        if family_id:
            representative_cache[family_id] = font_obj.id
        return True
    
    return False

def representative_fallback(db: Session, families_cache: dict) -> None:
    for fam_key, fam_entry in families_cache.items():
        # Si la famille a déjà un représentant, on skip
        if fam_entry.get("representative_id"):
            continue

        family_id = fam_entry.get("id")
        if not family_id:
            continue  # devrait être rare

        # Récupérer toutes les fonts liées à la famille
        fonts = db.query(Font).filter(Font.family_id == family_id).all()
        if not fonts:
            continue

        # 1. Style strict "regular"
        representative_font = next(
            (f for f in fonts if f.style_name and f.style_name.strip().lower() == "regular"),
            None
        )

        # 2. Style "propre"
        if representative_font is None:
            representative_font = next(
                (f for f in fonts if is_clean_style(f.style_name)),
                None
            )

        # 3. Fallback premier
        if representative_font is None:
            representative_font = fonts[0]

        # Mise à jour du cache et de la DB
        fam_entry["representative_id"] = representative_font.id
        db.query(Family).filter(Family.id == family_id).update(
            {"representative_id": representative_font.id}
        )

        # Générer subset
        subset(Path(representative_font.path))

    db.commit()