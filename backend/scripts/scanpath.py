import json
from pathlib import Path
from collections import Counter, defaultdict
import sys

sys.stdout.reconfigure(encoding='utf-8')

# --- Configurable thresholds ---
THRESHOLD = 2               # minimum fonts in a folder to initially select it
PROMOTION_THRESHOLD = 4     # minimum sibling folders to trigger parent promotion

# --- Load JSON ---
json_path = Path("fonts.json")
print(f"Loading {json_path.resolve()} ...")
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

fonts = data["fonts"]
print(f"Loaded {len(fonts)} font families.")

# --- Count fonts per folder ---
folder_count = Counter()
folder_fonts = defaultdict(list)
for font in fonts:
    for path in font["paths"]:
        folder = str(Path(path).parent)
        folder_count[folder] += 1
        folder_fonts[folder].append(font["name"])

print(f"Counted {len(folder_count)} unique folders.")

# --- Collapse subfolders ---
def collapse_folders(folder_count, threshold):
    sorted_folders = sorted(folder_count.items(), key=lambda x: (-x[1], x[0]))
    chosen = []
    for folder, count in sorted_folders:
        if count < threshold:
            continue
        skip = any(Path(folder).is_relative_to(Path(parent)) for parent in chosen)
        if not skip:
            chosen.append(folder)
    return chosen

selected = collapse_folders(folder_count, THRESHOLD)
print(f"Initial selection: {len(selected)} folders")

# --- Promote parents of sibling folders with a threshold ---
def promote_parents(folders, promotion_threshold):
    folders = set(folders)
    changed = True
    while changed:
        changed = False
        parents_map = defaultdict(list)
        for f in folders:
            parent = str(Path(f).parent)
            parents_map[parent].append(f)

        for parent, children in list(parents_map.items()):
            if len(children) >= promotion_threshold:
                # Promote parent
                for c in children:
                    folders.discard(c)
                folders.add(parent)
                changed = True
                print(f"Promoted {parent} (from {len(children)} siblings)")
    return list(folders)

def remove_children_of_selected(folders):
    """Ensure only top-level selected folders remain — 
    remove children of any selected parent."""
    folders = sorted(folders, key=lambda f: len(f))  # parents before children
    clean = []

    for folder in folders:
        folder_path = Path(folder)
        # if this folder is a child of an already selected parent, skip it
        if any(folder_path.is_relative_to(Path(parent)) and folder != parent for parent in clean):
            # Debug optional:
            print(f"Removed child folder {folder} (covered by parent)")
            continue
        clean.append(folder)

    return clean


final_folders = promote_parents(selected, PROMOTION_THRESHOLD)
final_folders = remove_children_of_selected(final_folders)  # Use cleaned results

# --- Print results ---
print(f"\nFinal selected folders: {len(final_folders)}")
for folder in sorted(final_folders):
    count = folder_count[folder] if folder in folder_count else 0
    print(f"• {folder} — {count} fonts")

# --- Optional: save to file ---
out_path = Path("folders_to_watch.json")
out_path.write_text(json.dumps(final_folders, indent=2), encoding="utf-8")
print(f"\nSaved {len(final_folders)} folders to {out_path.resolve()}")