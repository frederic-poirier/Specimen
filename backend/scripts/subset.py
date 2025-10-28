from fontTools.ttLib import TTFont
from fontTools import subset as ft_subset
from fontTools.varLib import instancer
from pathlib import Path
import re

# Dossier de sortie stable
SUBSET_FOLDER = (Path(__file__).resolve().parent.parent / "subset").resolve()
SUBSET_FOLDER.mkdir(parents=True, exist_ok=True)

# Texte de prévisualisation propre (ASCII uniquement)
PREVIEW_TEXT = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    " .,:;!?\"'()[]{}<>-_/\\@&%*+=#"
    " The quick brown fox jumps over the lazy dog"
)


# -------------------------------
# Helpers internes
# -------------------------------

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
    axes = font["fvar"].axes
    instance_coords = {axis.axisTag: axis.defaultValue for axis in axes}
    instancer.instantiateVariableFont(font, instance_coords, inplace=True)
    return font


def _sanitize_filename(name: str) -> str:
    """Return a safe filename based on a font name."""
    # Replace invalid Windows filename chars and collapse whitespace
    name = re.sub(r"[<>:\\/|?*]", "-", name)
    name = re.sub(r"\s+", " ", name).strip()
    # Replace spaces with dashes and collapse repeats
    name = name.replace(" ", "-")
    name = re.sub(r"-+", "-", name)
    return name or "font"


def get_family_name(font: TTFont) -> str:
    """Extract the font family name, preferring Typographic Family (ID 16)."""
    try:
        name_table = font["name"]
        family = name_table.getDebugName(16) or name_table.getDebugName(1)
        if not family:
            for nid in (21, 2, 6):
                family = name_table.getDebugName(nid)
                if family:
                    break
        return _sanitize_filename(family) if family else "font"
    except Exception:
        return "font"


# -------------------------------
# Fonction principale
# -------------------------------

def subset(path: Path) -> Path | None:
    """
    Génére un subset woff2 pour la police donnée.
    Retourne le chemin du subset, ou None en cas d'erreur.
    """
    # Build output file name from the font family name
    _tmp_font = None
    try:
        _tmp_font = open_font(path)
        _family = get_family_name(_tmp_font)
    except Exception:
        _family = "font"
    finally:
        if _tmp_font:
            try:
                _tmp_font.close()
            except Exception:
                pass
    output_path = SUBSET_FOLDER / f"{_family}.woff2"

    # 1. Cache de fichier: skip si subset déjà à jour
    try:
        if output_path.exists() and output_path.stat().st_mtime > path.stat().st_mtime:
            return output_path
    except OSError:
        # Si une erreur d'accès au fichier se produit, on continue le process
        pass

    font = None
    try:
        font = open_font(path)

        # 2. Variable font: instanciation si nécessaire
        if is_variable_font(font):
            font = instantiate_variable_font(font)

        # 3. Configuration des options de subset
        options = ft_subset.Options()
        options.flavor = "woff2"
        options.with_zopfli = True
        options.text = PREVIEW_TEXT
        options.layout_features = ["kern", "liga", "clig", "calt"]
        options.ignore_missing_glyphs = True
        options.drop_tables += ["STAT", "MVAR", "HVAR", "fvar"]
        options.recalc_timestamp = False

        # 4. Exécution
        subsetter = ft_subset.Subsetter(options=options)
        subsetter.populate(text=PREVIEW_TEXT)
        subsetter.subset(font)

        # 5. Sauvegarde du subset
        font.save(output_path)
        return output_path

    except Exception as e:
        if isinstance(e, ModuleNotFoundError):
            print("[subset error] WOFF2 output requires 'brotli' (pip install brotli or brotlicffi)")
        else:
            print(f"[subset error] {path}: {e}")
        return None

    finally:
        if font:
            try:
                font.close()
            except Exception:
                pass

if __name__ == "__main__":
    # Le chemin que vous voulez tester
    test_path = Path(r"C:\Users\fredm\Font\PANGRAM PANGRAM\Casa\PPCasa-Regular.otf")
    output = subset(test_path)
    print("Subset généré :", output)
