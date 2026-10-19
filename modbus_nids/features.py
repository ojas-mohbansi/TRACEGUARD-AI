"""Batch API for Phase 1.2 windowed feature extraction.

The heavy lifting lives in :mod:`modbus_nids.window`; this module resolves the
three supported input shapes (an :class:`IngestResult`, a clean DataFrame, or an
iterable of :class:`ModbusRecord`) and returns a :class:`FeatureBatch` whose
rows stay aligned with the ingested records' labels and ``raw_index`` values.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Union

import numpy as np
import pandas as pd

from .models import IngestResult, ModbusRecord
from .parser import frame_to_records
from .window import (
    DEFAULT_EPSILON,
    DEFAULT_WINDOW_SIZE,
    FEATURE_COLUMNS,
    SessionWindowManager,
    WindowError,
)

__all__ = ["FeatureBatch", "FeatureSource", "WindowError", "extract_features"]

FeatureSource = Union[IngestResult, pd.DataFrame, Iterable[ModbusRecord]]
"""Accepted inputs for :func:`extract_features`."""


@dataclass(slots=True)
class FeatureBatch:
    """Feature rows plus the label/provenance columns they were built from.

    ``frame`` contains metadata and features in ingested order. ``X``, ``y`` and
    ``raw_index`` are convenience views for the downstream FSM/ML tiers.
    """

    frame: pd.DataFrame
    feature_names: tuple[str, ...] = field(default=FEATURE_COLUMNS)

    def __post_init__(self) -> None:
        required = (*self.feature_names, "label", "raw_index", "session_id")
        missing = [column for column in required if column not in self.frame.columns]
        if missing:
            raise ValueError(f"feature frame is missing column(s): {', '.join(missing)}")

    def __len__(self) -> int:
        return len(self.frame)

    @property
    def features(self) -> pd.DataFrame:
        """Numeric feature matrix as a labeled DataFrame."""
        return self.frame.loc[:, list(self.feature_names)]

    @property
    def X(self) -> np.ndarray:
        """Feature matrix shaped ``(n_events, n_features)`` as float64."""
        return self.features.to_numpy(dtype=np.float64)

    @property
    def y(self) -> np.ndarray:
        """Ground-truth labels aligned with ``X`` as int64."""
        return self.frame["label"].to_numpy(dtype=np.int64)

    @property
    def raw_index(self) -> np.ndarray:
        """Raw ingestion row indices aligned with ``X``."""
        return self.frame["raw_index"].to_numpy(dtype=np.int64)

    @property
    def session_ids(self) -> np.ndarray:
        """Session identifier for each row, aligned with ``X``."""
        return self.frame["session_id"].to_numpy()


def _resolve_records(source: FeatureSource) -> list[ModbusRecord]:
    if isinstance(source, IngestResult):
        return list(source.records)
    if isinstance(source, pd.DataFrame):
        return frame_to_records(source)
    records = list(source)
    invalid = [type(item).__name__ for item in records if not isinstance(item, ModbusRecord)]
    if invalid:
        raise TypeError(
            "extract_features expects ModbusRecord items; got " + ", ".join(sorted(set(invalid)))
        )
    return records


def extract_features(
    source: FeatureSource,
    *,
    window_size: int = DEFAULT_WINDOW_SIZE,
    epsilon: float = DEFAULT_EPSILON,
) -> FeatureBatch:
    """Compute session-isolated features for parsed Modbus/TCP records.

    Args:
        source: An ingestion result, a clean frame, or an iterable of records.
        window_size: Trailing events retained per TCP session (default 10).
        epsilon: Seconds added inside ``log(dt + epsilon)``.

    Returns:
        A :class:`FeatureBatch` aligned row-for-row with the input records.

    Raises:
        WindowError: If a session's timestamps regress.
        ValueError: If the feature frame or configuration is invalid.
        TypeError: If an iterable contains non-record items.
    """
    manager = SessionWindowManager(window_size=window_size, epsilon=epsilon)
    frame = manager.transform(_resolve_records(source))
    return FeatureBatch(frame=frame)

