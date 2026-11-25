import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
import GDIP_CODE as arm

@pytest.fixture(autouse=True)
def offline_mode(monkeypatch):
    monkeypatch.setattr(arm, 'DRY_RUN', True)
