from pathlib import Path
from typing import List, Tuple, Optional

from .constants import ICON_EXTS


def _find_icon(script_path: Path) -> Optional[Path]:
    for extension in ICON_EXTS:
        icon = script_path.with_suffix(extension)
        if icon.is_file():
            return icon
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
