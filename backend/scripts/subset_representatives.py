from sqlalchemy.orm import Session
from backend.models.font import Font
from backend.core.db import SessionLocal  # selon votre structure

from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.varLib import instancer
from pathlib import Path

# Always resolve to backend/subset regardless of current working directory
SUBSET_FOLDER = (Path(__file__).resolve().parent.parent / "subset").resolve()
SUBSET_FOLDER.mkdir(parents=True, exist_ok=True)
PREVIEW_TEXT = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "àâäçéèêëîïôöùûüÿœæ"
    "ÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸŒÆ"
    " .,:;!?\"'()[]{}<>-–—_@&%*/\\+=#"
)

def open_font(path: Path) -> TTFont:
    suffix = path.suffix.lower()
    if suffix == ".woff":
        return TTFont(path, flavor="woff")
    elif suffix == ".woff2":
        return TTFont(path, flavor="woff2")
    return TTFont(path)

def is_variable_font(font: TTFont) -> bool:
    return "fvar" in font

def instantiate_variable_font(font: TTFont) -> TTFont:
    # On récupère les axes disponibles
    axes = font["fvar"].axes
    # On choisit la valeur par défaut pour chaque axe
    instance_coords = {axis.axisTag: axis.defaultValue for axis in axes}

    # Instanciation en place
    instancer.instantiateVariableFont(font, instance_coords, inplace=True)
    return font

def make_subset(path: Path) -> Path | None:
    output_path = SUBSET_FOLDER / f"{path.stem}.woff2"
    if output_path.exists() and output_path.stat().st_mtime > path.stat().st_mtime:
        return output_path

    font = None
    try:
        font = open_font(path)

        # Étape variable → statique si nécessaire
        if is_variable_font(font):
            font = instantiate_variable_font(font)

        # Options de sous-setting
        options = subset.Options()
        options.flavor = "woff2"
        options.with_zopfli = True
        options.text = PREVIEW_TEXT
        options.layout_features = ["kern", "liga", "clig", "calt"]
        options.ignore_missing_glyphs = True
        options.drop_tables += ['STAT', 'MVAR', 'HVAR', 'fvar']
        options.recalc_timestamp = False

        # Exécution du subset
        subsetter = subset.Subsetter(options=options)
        subsetter.populate(text=PREVIEW_TEXT)
        subsetter.subset(font)

        font.save(output_path)
        return output_path

    except Exception as e:
        print(f"[subset error] {path}: {e}")
        return None

    finally:
        if font:
            try:
                font.close()
            except Exception:
                pass




def subset_all_representatives():
    """Fait un subset pour toutes les fonts marquées representative=True."""
    subsetted = []
    with SessionLocal() as session:  # ouvre et ferme automatiquement la session
        fonts = (
            session.query(Font)
            .filter(Font.representative == True)  # noqa
            .all()
        )

        if not fonts:
            print("Aucune police representative trouvée.")
            return []

        for f in fonts:
            font_path = Path(f.path)
            if not font_path.exists():
                print(f"[skip] Fichier introuvable : {font_path}")
                continue

            output = make_subset(font_path)
            if output:
                print(f"[ok] Subset généré pour {f.full_name or font_path.name}: {output}")
                subsetted.append(output)
            else:
                print(f"[error] Subset échoué pour {font_path}")

    return subsetted

if __name__ == "__main__":
    results = subset_all_representatives()
    print(f"Subset terminé. {len(results)} fichiers générés.")
