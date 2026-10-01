#!/usr/bin/env python3
"""
Shim kompatibilitas: interpreter lama berbasis string-splitting sudah diganti
core terpadu di paket ``hambalang`` (lexer + parser + interpreter + VM).

    python interpreter/hamba_v2.py program.hl   ==   hambalang run program.hl
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hambalang.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(["run", *sys.argv[1:]]))
