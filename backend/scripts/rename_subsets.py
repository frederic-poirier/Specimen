from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, Tuple


def _ensure_project_on_path():
    this = Path(__file__).resolve()
    project_root = this.parents[2]  # .../Specimen
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


_ensure_project_on_path()

from backend.core.db import SessionLocal  # type: ignore
from backend.models.font import Font, Family  # type: ignore
from backend.scripts.subset import SUBSET_FOLDER  # type: ignore

try:
    # Reuse sanitizer to keep rules identical to subset generation
    from backend.scripts.subset import _sanitize_filename  # type: ignore
except Exception:  # pragma: no cover
    # Minimal fallback if internal import changes
    import re

    def _sanitize_filename(name: str) -> str:
        name = re.sub(r"[<>:\\/:|?*]", "-", name or "")
        name = re.sub(r"\s+", " ", name).strip()
        name = name.replace(" ", "-")
        name = re.sub(r"-+", "-", name)
        return name or "font"


def build_stem_to_family_map(session) -> Dict[str, Tuple[str, bool]]:
    """Return mapping: font filename stem -> (sanitized family name, is_rep).

    If multiple fonts share the same stem, representative entries take precedence.
    """
    mapping: Dict[str, Tuple[str, bool]] = {}

    rows = (
        session.query(Font.id, Font.path, Family.name, Family.representative_id)
        .join(Family, Family.id == Font.family_id)
        .all()
    )
    for font_id, fpath, fam_name, rep_id in rows:
        stem = Path(fpath).stem
        fam_sanitized = _sanitize_filename(fam_name or "")
        is_rep = rep_id == font_id if rep_id is not None else False

        if stem not in mapping:
            mapping[stem] = (fam_sanitized, is_rep)
        else:
            # Prefer representative mapping if available
            if is_rep and not mapping[stem][1]:
                mapping[stem] = (fam_sanitized, True)

    return mapping


def rename_subsets(dry_run: bool = False, subset_dir: Path | None = None, ext: str = ".woff2") -> int:
    """Rename files in subset directory to their SQL family names.

    Returns the number of files changed.
    """
    changed = 0
    subset_dir = subset_dir or SUBSET_FOLDER

    session = SessionLocal()
    try:
        stem_map = build_stem_to_family_map(session)

        files = sorted(subset_dir.glob(f"*{ext}"))
        for src in files:
            src_stem = src.stem
            target_base = stem_map.get(src_stem, (None, False))[0]
            if not target_base:
                # No mapping found; skip
                continue

            dst = subset_dir / f"{target_base}{ext}"

            if dst == src:
                continue  # already correct name

            if dst.exists():
                # Resolve duplicates: keep the newest
                try:
                    src_m = src.stat().st_mtime
                    dst_m = dst.stat().st_mtime
                except OSError:
                    src_m = 0
                    dst_m = 0

                if src_m > dst_m:
                    # Replace older target with newer source
                    if dry_run:
                        print(f"REPLACE {dst.name} <- {src.name}")
                    else:
                        dst.unlink(missing_ok=True)
                        src.rename(dst)
                    changed += 1
                else:
                    # Target newer; remove source duplicate
                    if dry_run:
                        print(f"DELETE duplicate {src.name} (kept {dst.name})")
                    else:
                        src.unlink(missing_ok=True)
                    changed += 1
            else:
                if dry_run:
                    print(f"RENAME {src.name} -> {dst.name}")
                else:
                    src.rename(dst)
                changed += 1

    finally:
        session.close()

    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rename subset files to SQL family names")
    parser.add_argument("--dry-run", action="store_true", help="Show planned changes without applying")
    parser.add_argument("--subset-dir", type=Path, default=None, help="Override subset directory")
    parser.add_argument("--ext", default=".woff2", help="Subset file extension (default: .woff2)")
    args = parser.parse_args(argv)

    changed = rename_subsets(dry_run=args.dry_run, subset_dir=args.subset_dir, ext=args.ext)
    if args.dry_run:
        print(f"Would change {changed} file(s)")
    else:
        print(f"Changed {changed} file(s)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

