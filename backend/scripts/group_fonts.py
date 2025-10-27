from sqlalchemy.orm import Session
from difflib import SequenceMatcher
from collections import defaultdict
from typing import Dict, List
from pathlib import Path
from backend.models.font import Font
from backend.scripts.subset_representatives import make_subset

MATCHING_THRESHOLD = 0.8
GLYPH_TOLERANCE = 0.1  

EXCLUDED_KEYWORDS = [
    "italic", "oblique", "wide", "expanded", "extended", 
    "condensed", "narrow", "compressed"
]

def compare_metadata(f1: Font, f2: Font) -> bool:
    if f1.vendor and f2.vendor and f1.vendor != f2.vendor:
        return False
    
    if f1.glyph_count and f2.glyph_count:
        diff = abs(f1.glyph_count - f2.glyph_count) / max(f1.glyph_count, 1)
        if diff > GLYPH_TOLERANCE:
            return False
        
    if f1.license and f2.license and f1.license != f2.license:
        return False
    
    if f1.panose and f2.panose and f1.panose != f2.panose:
        return False
    
    return True


def similar_name(name1: str, name2: str) -> float:
    return SequenceMatcher(None, name1 or "", name2 or "").ratio()


def group_exact(db: Session) -> Dict[str, List[Font]]:
    families = defaultdict(list)
    fonts = db.query(Font).filter(Font.family_normalized.isnot(None)).all()

    for font in fonts:
        families[font.family_normalized].append(font)

    return families


def group_fuzzy(db: Session, existing_families: Dict[str, List[Font]], threshold: float = MATCHING_THRESHOLD) -> Dict[str, List[Font]]:
    families = existing_families.copy()
    fonts = db.query(Font).filter(Font.family_normalized.is_(None)).all()

    used_ids = set()
    for f1 in fonts:
        if f1.id in used_ids:
            continue

        base_name = f1.family or ""
        if not base_name:
            continue

        group = [f1]
        used_ids.add(f1.id)

        for f2 in fonts:
            if f2.id in used_ids:
                continue

            name2 = f2.family or ""
            if not name2:
                continue

            if similar_name(base_name.lower(), name2.lower()) >= threshold and compare_metadata(f1, f2):
                group.append(f2)
                used_ids.add(f2.id)

        # Si on a trouvé au moins 2 fonts, créer une nouvelle famille fuzzy
        if len(group) > 1:
            families[base_name.lower()] = group

    return families


def assign_representative_family(db: Session, families: Dict[str, list[Font]]):
    for family_name, fonts in families.items():
        if not fonts:
            continue

        def is_clean_style(f: Font) -> bool:
            """Retourne True si le style ne contient aucun mot-clé exclu."""
            if not f.style_name:
                return True
            s = f.style_name.lower()
            return not any(kw in s for kw in EXCLUDED_KEYWORDS)

        representative_font = None

        # 1. Regular weight (400) sans exclu
        for f in fonts:
            if f.weight_class == 400 and is_clean_style(f):
                representative_font = f
                break

        # 2. style_name strict == "regular"
        if representative_font is None:
            for f in fonts:
                if f.style_name and f.style_name.strip().lower() == "regular":
                    representative_font = f
                    break

        # 3. premier style clean
        if representative_font is None:
            for f in fonts:
                if is_clean_style(f):
                    representative_font = f
                    break

        # 4. fallback
        if representative_font is None:
            representative_font = fonts[0]

        representative_family_name = representative_font.family or family_name

        for f in fonts:
            f.family = representative_family_name
            f.family_normalized = family_name
            f.representative = (f.id == representative_font.id)

        # Ensure a subset is generated for the chosen representative
        try:
            if representative_font.path:
                make_subset(Path(representative_font.path))
        except Exception as _e:
            # Keep grouping robust even if subsetting fails
            pass

    db.commit()


def group_fonts(db: Session):
    print("=== Grouping fonts by exact normalized name ===")
    families = group_exact(db)
    print(f"Found {len(families)} exact families.")

    print("=== Fuzzy grouping on remaining fonts ===")
    families = group_fuzzy(db, families)
    print(f"Total families after fuzzy grouping: {len(families)}")

    print("=== Assigning representative families ===")
    assign_representative_family(db, families)
    print("Font families updated in database.")
