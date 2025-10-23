import platform
import subprocess
import json
import os

def search_fonts():
    os_name = platform.system()

    try:
        if os_name == "Windows":
            print("Using Windows search")
            cmd = [
                "es.exe",
                "-regex", r".*\.(ttf|otf|woff2?)$"
            ]
        elif os_name == "Darwin":
            cmd = [
                "mdfind",
                "kMDItemFSName == '*.ttf' || kMDItemFSName == '*.otf' || kMDItemFSName == '*.woff*'"
            ]
        elif os_name == "Linux":
            cmd = [
                "locate", "--ignore-case", "--regex", r"\.(ttf|otf|woff2?)$"
            ]
        else:
            raise RuntimeError(f"Unsupported OS: {os_name}")

        result = subprocess.check_output(cmd, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        # command failed or isn't available — fallback to scanning common font directories
        fonts = []
        common_dirs = []
        if os_name == "Windows":
            common_dirs = [
                os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
            ]
        elif os_name == "Darwin":
            common_dirs = [
                "/Library/Fonts",
                "/System/Library/Fonts",
                os.path.expanduser("~/Library/Fonts")
            ]
        elif os_name == "Linux":
            common_dirs = [
                "/usr/share/fonts",
                "/usr/local/share/fonts",
                os.path.expanduser("~/.local/share/fonts"),
                os.path.expanduser("~/.fonts")
            ]
        for d in common_dirs:
            if os.path.isdir(d):
                for root, _, files in os.walk(d):
                    for fn in files:
                        if fn.lower().endswith((".ttf", ".otf", ".woff", ".woff2")):
                            fonts.append(os.path.join(root, fn))
        # deduplicate and sort the fallback results
        fonts = sorted(set(fonts))
    else:
        # split, remove empty lines, deduplicate and sort
        fonts = sorted({line.strip() for line in result.splitlines() if line.strip()})

    out_path = os.path.join(os.path.dirname(__file__), "fonts.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"fonts": fonts}, f, indent=2, ensure_ascii=False)

    return out_path
