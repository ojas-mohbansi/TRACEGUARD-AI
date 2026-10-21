"""Hybrid Modbus/TCP NIDS — ingestion and windowed feature layers.

Public surface for the rest of the system: canonical schema constants, the
validated record type, the ingestion result/report contracts, the CSV /
record / DataFrame entry points, and the Phase 1.3 session-isolated window
extractor that feeds the FSM and ML tiers.
"""

from __future__ import annotations

from .constants import (
    CANONICAL_COLUMNS,
    DEFAULT_ALLOWED_PORTS,
    DERIVED_COLUMNS,
    FUNCTION_CODES,
    MBAP_MAX_LENGTH,
    MBAP_MIN_LENGTH,
    MODBUS_TCP_PORT,
    OPTIONAL_COLUMNS,
    REQUIRED_COLUMNS,
    FunctionCodeSpec,
)
from .models import (
    Direction,
    IngestConfig,
    IngestMeta,
    IngestResult,
    IngestionError,
    ModbusRecord,
    RejectReason,
    RejectionReport,
    SchemaError,
    SourceError,
    ValidationIssue,
    WarningCode,
)
from .parser import (
    frame_to_records,
    map_columns,
    parse_csv,
    parse_dataframe,
    parse_records,
    records_to_frame,
)
from .synthetic import generate_synthetic_logs, write_synthetic_csv
from .validation import RowValidation, coerce_timestamp, validate_row
from .features import FeatureBatch, extract_features
from .window import (
    DEFAULT_EPSILON,
    DEFAULT_WINDOW_SIZE,
    FEATURE_COLUMNS,
    METADATA_COLUMNS,
    NGRAM_SIZES,
    OUTPUT_COLUMNS,
    READ_FUNCTION_CODES,
    WRITE_FUNCTION_CODES,
    SessionKey,
    SessionWindowManager,
    WindowError,
)

__version__ = "0.3.0"

__all__ = [
    "__version__",
    "CANONICAL_COLUMNS",
    "DEFAULT_ALLOWED_PORTS",
    "DERIVED_COLUMNS",
    "FUNCTION_CODES",
    "MBAP_MAX_LENGTH",
    "MBAP_MIN_LENGTH",
    "MODBUS_TCP_PORT",
    "OPTIONAL_COLUMNS",
    "REQUIRED_COLUMNS",
    "DEFAULT_EPSILON",
    "DEFAULT_WINDOW_SIZE",
    "Direction",
    "FEATURE_COLUMNS",
    "FeatureBatch",
    "FunctionCodeSpec",
    "IngestConfig",
    "IngestMeta",
    "IngestResult",
    "IngestionError",
    "METADATA_COLUMNS",
    "ModbusRecord",
    "NGRAM_SIZES",
    "OUTPUT_COLUMNS",
    "READ_FUNCTION_CODES",
    "RejectReason",
    "RejectionReport",
    "RowValidation",
    "SchemaError",
    "SessionKey",
    "SessionWindowManager",
    "SourceError",
    "ValidationIssue",
    "WRITE_FUNCTION_CODES",
    "WarningCode",
    "WindowError",
    "coerce_timestamp",
    "extract_features",
    "frame_to_records",
    "generate_synthetic_logs",
    "map_columns",
    "parse_csv",
    "parse_dataframe",
    "parse_records",
    "records_to_frame",
    "validate_row",
    "write_synthetic_csv",
]
