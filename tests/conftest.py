import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from hambalang import run_source  # noqa: E402

ENGINES = ["interpreter", "vm"]


@pytest.fixture(params=ENGINES)
def engine(request):
    return request.param


@pytest.fixture
def run(engine):
    """run(src, **opts) -> output, dijalankan di interpreter DAN VM."""

    def _run(src: str, **opts) -> str:
        opts.setdefault("seed", 42)
        return run_source(src, engine=engine, **opts)

    return _run
