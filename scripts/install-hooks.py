#!/usr/bin/env python3
"""
scripts/install-hooks.py
==============================================================================
Installs and configures Git Hooks (.githooks/) for this repository.
==============================================================================
"""

import os
import stat
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    hooks_dir = root / ".githooks"

    if not hooks_dir.exists():
        print(f"[ERROR] Hooks directory not found at: {hooks_dir}")
        return 1

    print(f"[*] Setting git core.hooksPath to: {hooks_dir}")
    try:
        subprocess.run(
            ["git", "config", "core.hooksPath", ".githooks"],
            cwd=str(root),
            check=True,
        )
        print("[+] git config core.hooksPath set successfully.")
    except Exception as e:
        print(f"[!] Warning: Failed to run git config: {e}")

    # Make executable on Unix/macOS
    if os.name != "nt":
        for hook_file in hooks_dir.iterdir():
            if hook_file.is_file():
                st = hook_file.stat()
                hook_file.chmod(st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
                print(f"  [CHMOD +x] {hook_file.name}")

    print("[+] Git hooks setup complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
