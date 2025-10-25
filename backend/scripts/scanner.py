import subprocess
import shutil
import json
from pathlib import Path

# --- Locate es.exe ---
es_path = shutil.which("es.exe")
if not es_path:
    raise RuntimeError(
        "Everything CLI (es.exe) not found in PATH. "
        "Please install Everything from https://www.voidtools.com/ "
        "and add es.exe to your PATH."
    )

# --- Run search ---
query = "ext:ttf;otf;woff;woff2"
result = subprocess.run([es_path, query], capture_output=True, text=True)
paths = [line for line in result.stdout.splitlines() if line]

# --- Grouping function ---
def structure_font_data(paths):
    fonts_dict = {}
    for path in paths:
        p = Path(path)
        name = p.stem
        ext = p.suffix.lstrip(".").lower()

        if name not in fonts_dict:
            fonts_dict[name] = {
                "name": name,
                "paths": [str(p)],
                "extensions": [ext]
            }
        else:
            # add only if not already recorded
            if str(p) not in fonts_dict[name]["paths"]:
                fonts_dict[name]["paths"].append(str(p))
            if ext not in fonts_dict[name]["extensions"]:
                fonts_dict[name]["extensions"].append(ext)

    # Convert dict to list
    return list(fonts_dict.values())

# --- Build output ---
fonts_data = structure_font_data(paths)
output = {
    "total_fonts": len(fonts_data),
    "fonts": fonts_data
}

# --- Write JSON file ---
json_file = Path("fonts.json")
json_file.write_text(json.dumps(output, indent=2), encoding="utf-8")

print(f"Saved {output['total_fonts']} fonts to {json_file.resolve()}")
