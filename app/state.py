from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class AppState:
    uploaded_df: pd.DataFrame | None = None
    uploaded_filename: str | None = None
    trained_bundle: dict[str, Any] | None = None
    trained_task: str | None = None
    last_saved_model_path: Path | None = None


STATE = AppState()
