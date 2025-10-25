from sqlalchemy.orm import Session
from backend.models.font import Font
from backend.core.db import SessionLocal  # selon votre structure
from fontTools.ttLib import TTFont
from fontTools import subset
from pathlib import Path



SUBSET_FOLDER = Path("../subset")
SUBSET_FOLDER.mkdir(parents=True, exist_ok=True)

PREVIEW_TEXT = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "àâäçéèêëîïôöùûüÿœæ"
    "ÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸŒÆ"
    " .,:;!?\"'()[]{}<>-–—_@&%*/\\+=#"
)

def open_font(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".woff":
        return TTFont(path, flavor="woff")
    elif suffix == ".woff2":
        return TTFont(path, flavor="woff2")
    return TTFont(path)

def make_subset(path: Path) -> Path | None:
    try:
        output_path = SUBSET_FOLDER / f"{path.stem}.woff2"
        if output_path.exists() and output_path.stat().st_mtime > path.stat().st_mtime:
            return output_path

        font = open_font(path)

        options = subset.Options()
        options.flavor = "woff2"
        options.with_zopfli = True
        options.text = PREVIEW_TEXT
        options.layout_features = ["kern", "liga", "clig", "calt"]
        options.ignore_missing_glyphs = True
        options.drop_tables += ['STAT', 'MVAR', 'HVAR', 'fvar']
        options.recalc_timestamp = False

        subsetter = subset.Subsetter(options=options)
        subsetter.populate(text=PREVIEW_TEXT)
        subsetter.subset(font)

        font.save(output_path)
        return output_path

    except Exception as e:
        print(f"[subset error] {path}: {e}")
        return None

    finally:
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
