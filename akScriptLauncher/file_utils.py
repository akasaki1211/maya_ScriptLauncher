from pathlib import Path
from typing import List, Tuple, Optional


def _find_icon(script_path: Path) -> Optional[Path]:
    ico = script_path.with_suffix('.ico')
    if ico.is_file():
        return ico
    png = script_path.with_suffix('.png')
    if png.is_file():
        return png
    return None


def load_scripts(path: Path) -> Tuple[List[Tuple[str, Path]], List[Tuple[str, str, Path, Optional[Path]]]]:
    dirs: List[Tuple[str, Path]] = []
    files: List[Tuple[str, str, Path, Optional[Path]]] = []

    for f in sorted(path.iterdir()):
        if f.is_dir():
            dirs.append((f.name, f))
        else:
            ext = f.suffix.lower()
            if ext not in ['.py', '.mel']:
                continue

            icon_path = _find_icon(f)
            files.append((f.name, ext, f, icon_path))

    return dirs, files
