#!/usr/bin/env python3
"""
Shim kompatibilitas: ``python cli/hambalang.py ...`` sekarang memakai CLI
terpadu di ``hambalang.cli``. Helper print_* tetap diekspor untuk
``cli/cli_extensions.py`` (perintah legacy obfuscate/analyze).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hambalang.cli import Style, error, header, info, main, success  # noqa: E402


class Color:
    WARNING = "\033[93m" if Style.enabled else ""
    ENDC = "\033[0m" if Style.enabled else ""


print_header = header
print_success = success
print_error = error
print_info = info

if __name__ == "__main__":
    sys.exit(main())
