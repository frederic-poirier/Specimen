from fontTools.ttLib import TTFont
from lxml import etree
from pathlib import Path
from hashlib import sha1
import re

DICTIONARY = [
    'regular', 'book', 'normal', 'roman',
    'light', 'thin', 'ultralight', 'hairline',
    'medium', 'semibold', 'demibold', 'demi',
    'bold', 'heavy', 'black', 'extrabold', 'ultrabold',
    'italic', 'oblique', 'condensed', 'narrow',
    'expanded', 'wide', 'extra', 'extraexpanded',
    'extended', 'compressed', 'narrower', 'wider',
    'display', 'headline', 'title', 'text', 'sc', 'comp', 
    'exbold', 'exheavy', 'exblack', 'exlight', 'extrathin',
    'it', 'ex', 'ultra', 'super', 'sub', 'smallcaps', 'caps',
    'demi', 'semi', 'lt', 'act'
]
STYLE_KEYWORDS = sorted(DICTIONARY, key=lambda w: -len(w))

PREFERRED_PLATFORM_IDS = [3, 1, 0]
PREFERRED_LANG_IDS = [0x0409, 0x0000, 0x040C, 0x0407]


def extract(font_path: Path) -> dict | None:
    try:
        try:
            font = TTFont(font_path)
        except Exception:
            suffix = font_path.suffix.lower()
            if suffix == ".woff":
                font = TTFont(font_path, flavor="woff")
            elif suffix == ".woff2":
                try:
                    font = TTFont(font_path, flavor="woff2")
                except ModuleNotFoundError:
                    print("The WOFF2 decoder requires the 'brotli' Python package (pip install brotli or brotlicffi)")
                    return None
            elif suffix == ".svg":
                return extract_svg_font(font_path)
            else:
                print(f"[discard] Unsupported font type: {font_path}")
                return None

        file_sha1 = sha1(font_path.read_bytes()).hexdigest()
        file_format = font_path.suffix.lower().lstrip('.')

        family_name = get_name_record(font, 16) or get_name_record(font, 1)
        family_normalized = normalize_name(family_name)
        full_name = get_name_record(font, 4)
        style_name = get_name_record(font, 2)  # Nom du style lisible
        license_info = get_name_record(font, 13) or ''

        # Base metadata
        vendor = None
        panose = None
        code_page1 = None
        code_page2 = None
        glyph_count = len(font.getGlyphOrder())

        # Style metrics
        weight_class = None
        width_class = None
        units_per_em = None
        ascender = None
        descender = None
        line_gap = None
        x_height = None
        cap_height = None
        italic_angle = None

        if "OS/2" in font:
            os2 = font["OS/2"]
            try:
                vendor = os2.achVendID.decode().strip()
            except Exception:
                vendor = str(os2.achVendID)

            panose_obj = getattr(os2, "panose", None)
            if panose_obj:
                try:
                    panose = [int(x) for x in panose_obj]  # certains sont listables
                except TypeError:
                    # fallback si ce n'est pas iterable
                    panose = [
                        panose_obj.bFamilyType,
                        panose_obj.bSerifStyle,
                        panose_obj.bWeight,
                        panose_obj.bProportion,
                        panose_obj.bContrast,
                        panose_obj.bStrokeVariation,
                        panose_obj.bArmStyle,
                        panose_obj.bLetterForm,
                        panose_obj.bMidline,
                        panose_obj.bXHeight
                    ]
            else:
                panose = None

            code_page1 = getattr(os2, "ulCodePageRange1", None)
            code_page2 = getattr(os2, "ulCodePageRange2", None)
            weight_class = getattr(os2, "usWeightClass", None)
            width_class = getattr(os2, "usWidthClass", None)
            ascender = getattr(os2, "sTypoAscender", None)
            descender = getattr(os2, "sTypoDescender", None)
            line_gap = getattr(os2, "sTypoLineGap", None)
            x_height = getattr(os2, "sxHeight", None) if hasattr(os2, "sxHeight") else None
            cap_height = getattr(os2, "sCapHeight", None) if hasattr(os2, "sCapHeight") else None

        if "head" in font:
            units_per_em = getattr(font["head"], "unitsPerEm", None)

        if "post" in font:
            italic_angle = getattr(font["post"], "italicAngle", None)

        font.close()

        return {
            "path": str(font_path),
            "sha1": file_sha1,
            "format": file_format,
            "family": family_name,
            "family_normalized": family_normalized,
            "full_name": full_name,
            "style_name": style_name,
            "license": license_info,
            "vendor": vendor,
            "panose": panose,
            "code_page1": code_page1,
            "code_page2": code_page2,
            "glyph_count": glyph_count,
            "weight_class": weight_class,
            "width_class": width_class,
            "units_per_em": units_per_em,
            "ascender": ascender,
            "descender": descender,
            "line_gap": line_gap,
            "x_height": x_height,
            "cap_height": cap_height,
            "italic_angle": italic_angle,
            "representative": False  # initialisé à False, choisi plus tard
        }

    except Exception as e:
        print(f"[error] Failed to extract {font_path}: {e}")
        return None

def extract_svg_font(font_path: Path) -> dict | None:
    try:
        data = font_path.read_bytes()
        sha = sha1(data).hexdigest()
        tree = etree.fromstring(data)

        # Recherche du <font> node
        font_el = tree.find(".//{http://www.w3.org/2000/svg}font")
        if font_el is None:
            print(f"[discard] No <font> element in {font_path}")
            return None

        font_face = font_el.find("{http://www.w3.org/2000/svg}font-face")
        family_name = font_face.get("font-family") if font_face is not None else "Unknown"
        style_name = font_face.get("font-style") if font_face is not None else None
        weight = font_face.get("font-weight") if font_face is not None else None

        # Normalisation
        family_normalized = normalize_name(family_name)

        return {
            "path": str(font_path),
            "sha1": sha,
            "format": "svg",
            "family": family_name,
            "family_normalized": family_normalized,
            "full_name": family_name,
            "style_name": style_name,
            "license": None,
            "vendor": None,
            "panose": None,
            "code_page1": None,
            "code_page2": None,
            "glyph_count": 0,  # optionnel, SVG fonts ne sont pas structurées pareil
            "weight_class": weight,
            "width_class": None,
            "units_per_em": None,
            "ascender": None,
            "descender": None,
            "line_gap": None,
            "x_height": None,
            "cap_height": None,
            "italic_angle": None,
            "representative": False
        }

    except Exception as e:
        print(f"[error] Failed to extract SVG {font_path}: {e}")
        return None


def get_name_record(font, nameID):
    for p_id in PREFERRED_PLATFORM_IDS:
        for l_id in PREFERRED_LANG_IDS:
            for record in font["name"].names:
                if record.nameID == nameID and record.platformID == p_id and record.langID == l_id:
                    try:
                        return record.toUnicode()
                    except Exception:
                        continue
    return None


def normalize_name(name: str) -> str:
    if not name:
        return ""
    name = name.lower()
    name = re.sub(r'[^a-z0-9 ]', ' ', name)
    tokens = name.split()
    tokens = [t for t in tokens if t not in STYLE_KEYWORDS]
    return ''.join(tokens)
