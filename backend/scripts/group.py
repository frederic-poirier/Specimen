from difflib import SequenceMatcher

from difflib import SequenceMatcher

MATCHING_THRESHOLD = 0.8
PANOSE_THRESHOLD = 0.4  # seuil de tolérance panose

def fuzzy_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a or "", b or "").ratio()

def panose_similarity(a: tuple, b: tuple) -> float:
    if not a or not b:
        return 0.0
    matches = sum(1 for x, y in zip(a, b) if x == y)
    return matches / max(len(a), len(b))

def make_key(metadata: dict):
    """La clé primaire de regroupement est uniquement basée sur le nom de famille normalisé."""
    return metadata.get("family_normalized") or ""

def group(metadata: dict, families_cache: dict) -> tuple[str, bool]:
    fam_norm_new = make_key(metadata)
    vendor_new = metadata.get("vendor") or ""
    panose_new = tuple(metadata.get("panose") or [])

    # --- Vérification stricte si la famille existe déjà ---
    if fam_norm_new in families_cache:
        return fam_norm_new, False

    # --- Fuzzy match sur family_normalized ---
    best_match_key = None
    best_ratio = 0.0
    for existing_key, fam_entry in families_cache.items():
        ratio = fuzzy_ratio(fam_norm_new, existing_key)
        if ratio >= MATCHING_THRESHOLD and ratio > best_ratio:
            # Vérification permissive sur panose
            panose_existing = tuple(fam_entry.get("panose") or [])
            panose_score = panose_similarity(panose_new, panose_existing)

            # On n'exclut pas si panose diffère légèrement
            if panose_existing and panose_new and panose_score < PANOSE_THRESHOLD:
                continue

            # vendor est purement informatif ici — pas bloquant
            best_ratio = ratio
            best_match_key = existing_key

    if best_match_key:
        return best_match_key, False

    # --- Création d'une nouvelle famille ---
    families_cache[fam_norm_new] = {
        "id": None,
        "representative_id": None,
        "vendor": vendor_new,
        "panose": list(panose_new),
        "name_normalized": fam_norm_new,
    }

    return fam_norm_new, True
