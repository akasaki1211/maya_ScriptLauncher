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


def load_scripts(path: Path) -> Tuple[List[Path], List[Tuple[Path, Optional[Path]]]]:
    
    dirs: List[Path] = []
    files: List[Tuple[Path, Optional[Path]]] = []

    for f in sorted(path.iterdir()):
        if f.is_dir():
            dirs.append(f)
        else:
            if f.suffix.lower() not in ['.py', '.mel']:
                continue
            files.append((f, _find_icon(f)))

    return dirs, files
