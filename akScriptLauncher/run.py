from typing import Optional, Dict, Any
import runpy

def run_script(filepath: str, extra_globals: Optional[Dict[str, Any]] = None) -> Any:
    init_globals = extra_globals or {}
    return runpy.run_path(filepath, init_globals=init_globals, run_name="__main__")