"""Protocol constants, canonical log schema, and Modbus/TCP function-code metadata.

This module is the single source of truth for:

* MBAP framing bounds and Modbus/TCP addressing limits.
* The subset of function codes the NIDS understands, including per-code
  register/quantity limits and expected request lengths.
* The canonical column names, input aliases, and pandas dtypes that make up the
  clean frame handed to the sliding-window manager (Phase 1.2) and FSM engine.

Everything here is declarative and side-effect free so it can be imported by
every layer of the pipeline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Mapping

# ---------------------------------------------------------------------------
# MBAP / transport limits
# ---------------------------------------------------------------------------

MODBUS_TCP_PORT: Final[int] = 502
"""IANA-assigned Modbus/TCP port."""

DEFAULT_ALLOWED_PORTS: Final[frozenset[int]] = frozenset({MODBUS_TCP_PORT})
"""Ports accepted by the strict validation profile."""

MBAP_HEADER_LEN: Final[int] = 7
"""Transaction ID (2) + Protocol ID (2) + Length (2) + Unit ID (1)."""

MBAP_MIN_LENGTH: Final[int] = 2
"""Minimum Length field: 1 unit-ID byte + 1 function-code byte."""

MBAP_MAX_LENGTH: Final[int] = 254
"""Maximum Length field: 1 unit-ID byte + a 253-byte PDU."""

MODBUS_MAX_PDU: Final[int] = 253
"""Maximum PDU size before protocol ID / unit ID are counted."""

MODBUS_PROTOCOL_ID: Final[int] = 0
"""The only Protocol Identifier defined for Modbus (/TCP) traffic."""

EXCEPTION_FLAG: Final[int] = 0x80
"""OR-ed into the function code of an exception response."""

BASE_FC_MIN: Final[int] = 1
"""Lowest defined request function code."""

BASE_FC_MAX: Final[int] = 127
"""Highest defined request function code (0x80+ are exception responses)."""

TRANSACTION_ID_MAX: Final[int] = 0xFFFF
REGISTER_ADDRESS_MAX: Final[int] = 0xFFFF
UNIT_ID_MAX: Final[int] = 0xFF
PORT_MIN: Final[int] = 1
PORT_MAX: Final[int] = 0xFFFF

MIN_VALID_TIMESTAMP_YEAR: Final[int] = 1990
MAX_VALID_TIMESTAMP_YEAR: Final[int] = 2100
"""Sane bounds for parsed timestamps; rejects 1970 defaults and far-future junk."""

EPOCH_UNIT_BOUNDS: Final[tuple[tuple[float, str], ...]] = (
    (1e11, "s"),
    (1e14, "ms"),
    (1e17, "us"),
    (1e20, "ns"),
)
"""Absolute-epoch heuristics: first upper bound (exclusive) that fits wins."""


# ---------------------------------------------------------------------------
# Function-code metadata
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class FunctionCodeSpec:
    """Static description of a Modbus function code.

    ``fixed_request_length`` is the expected MBAP *Length* field for a request
    whose payload size does not depend on a quantity; ``per_unit_length`` adds
    bytes per written item for the variable-length write functions. ``None``
    means the length is not derivable from the columns available in Phase 1.1
    and therefore cannot be checked.
    """

    code: int
    name: str
    min_quantity: int | None = None
    max_quantity: int | None = None
    fixed_request_length: int | None = None
    per_unit_length: int = 0
    uses_register_address: bool = True
    writes: bool = False


FUNCTION_CODES: Final[Mapping[int, FunctionCodeSpec]] = MappingProxyType(
    {
        1: FunctionCodeSpec(1, "Read Coils", 1, 2000, 6, 0, True, False),
        2: FunctionCodeSpec(2, "Read Discrete Inputs", 1, 2000, 6, 0, True, False),
        3: FunctionCodeSpec(3, "Read Holding Registers", 1, 125, 6, 0, True, False),
        4: FunctionCodeSpec(4, "Read Input Registers", 1, 125, 6, 0, True, False),
        5: FunctionCodeSpec(5, "Write Single Coil", None, None, 6, 0, True, True),
        6: FunctionCodeSpec(6, "Write Single Register", None, None, 6, 0, True, True),
        7: FunctionCodeSpec(7, "Read Exception Status", None, None, 2, 0, False, False),
        8: FunctionCodeSpec(8, "Diagnostics", None, None, None, 0, False, False),
        11: FunctionCodeSpec(11, "Get Comm Event Counter", None, None, 2, 0, False, False),
        12: FunctionCodeSpec(12, "Get Comm Event Log", None, None, None, 0, False, False),
        15: FunctionCodeSpec(15, "Write Multiple Coils", 1, 1968, 7, 2, True, True),
        16: FunctionCodeSpec(16, "Write Multiple Registers", 1, 123, 7, 2, True, True),
        17: FunctionCodeSpec(17, "Report Server ID", None, None, None, 0, False, False),
        20: FunctionCodeSpec(20, "Read File Record", None, None, None, 0, False, False),
        21: FunctionCodeSpec(21, "Write File Record", None, None, None, 0, False, True),
        22: FunctionCodeSpec(22, "Mask Write Register", None, None, 8, 0, True, True),
        23: FunctionCodeSpec(
            23, "Read/Write Multiple Registers", 1, 125, 11, 2, True, True
        ),
        24: FunctionCodeSpec(24, "Read FIFO Queue", None, None, 4, 0, False, False),
        43: FunctionCodeSpec(43, "Read Device Identification", None, None, 5, 0, False, False),
    }
)
"""Known function codes. Unknown but in-range codes (9, 10, 13, ...) stay valid."""

EXCEPTION_RESPONSE_LENGTH: Final[int] = 3
"""MBAP Length of an exception response: unit ID + 0x80|FC + exception code."""


def base_function_code(function_code: int) -> int:
    """Return the request function code for a request *or* exception response."""
    return function_code & 0x7F if function_code >= EXCEPTION_FLAG else function_code


def is_exception_response(function_code: int) -> bool:
    """True when ``function_code`` carries the Modbus exception flag."""
    return EXCEPTION_FLAG <= function_code <= 0xFF


def function_code_spec(function_code: int) -> FunctionCodeSpec | None:
    """Look up metadata for a request or exception function code."""
    return FUNCTION_CODES.get(base_function_code(function_code))


def expected_request_length(function_code: int, quantity: int | None = None) -> int | None:
    """Expected MBAP Length for a request, or ``None`` when not derivable.

    ``quantity`` is the number of coils/registers written for FC15/FC16, and the
    write quantity for FC23.
    """
    spec = function_code_spec(function_code)
    if spec is None or spec.fixed_request_length is None:
        return None
    if spec.per_unit_length:
        if quantity is None:
            return None
        return spec.fixed_request_length + spec.per_unit_length * quantity
    return spec.fixed_request_length


# ---------------------------------------------------------------------------
# Canonical schema and column aliases
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    "timestamp",
    "source_ip",
    "dest_ip",
    "tcp_connection",
    "transaction_id",
    "function_code",
    "register_address",
    "data_length",
    "label",
)
"""Fields every input log must carry. ``register_address`` may be blank."""

NULLABLE_REQUIRED_COLUMNS: Final[tuple[str, ...]] = ("register_address",)
"""Required columns whose *values* may legitimately be absent."""

OPTIONAL_COLUMNS: Final[tuple[str, ...]] = (
    "source_port",
    "dest_port",
    "protocol_id",
    "unit_id",
    "quantity",
    "direction",
)
"""Enrichment fields used when present, tolerated when absent."""

DERIVED_COLUMNS: Final[tuple[str, ...]] = ("flow_key", "raw_index")
"""Columns the parser computes rather than reads."""

CANONICAL_COLUMNS: Final[tuple[str, ...]] = REQUIRED_COLUMNS + OPTIONAL_COLUMNS + DERIVED_COLUMNS

COLUMN_DTYPES: Final[Mapping[str, str]] = MappingProxyType(
    {
        "timestamp": "datetime64[ns, UTC]",
        "source_ip": "string",
        "dest_ip": "string",
        "tcp_connection": "string",
        "transaction_id": "int64",
        "function_code": "int64",
        "register_address": "Int64",
        "data_length": "int64",
        "label": "int64",
        "source_port": "Int64",
        "dest_port": "Int64",
        "protocol_id": "Int64",
        "unit_id": "Int64",
        "quantity": "Int64",
        "direction": "string",
        "flow_key": "string",
        "raw_index": "int64",
    }
)
"""Pinned dtypes for the clean frame; nullable ints preserve missing optionals."""

COLUMN_ALIASES: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
    {
        "timestamp": ("timestamp", "time", "ts", "datetime", "date_time", "event_time", "eventtime"),
        "source_ip": ("source_ip", "sourceip", "src_ip", "srcip", "source", "src", "client_ip"),
        "dest_ip": ("dest_ip", "destip", "dst_ip", "dstip", "destination", "dst", "server_ip"),
        "tcp_connection": (
            "tcp_connection",
            "tcpconnection",
            "tcp_conn",
            "conn",
            "connection",
            "stream_id",
            "streamid",
            "socket_id",
            "socketid",
            "session_id",
        ),
        "transaction_id": ("transaction_id", "transactionid", "tid", "trans_id", "transid"),
        "function_code": ("function_code", "functioncode", "fc", "func", "function"),
        "register_address": (
            "register_address",
            "registeraddress",
            "reg_addr",
            "regaddr",
            "address",
            "addr",
            "start_address",
        ),
        "data_length": ("data_length", "datalength", "length", "mbap_length", "mbaplen", "payload_length"),
        "label": ("label", "attack", "is_attack", "target", "class", "y"),
        "source_port": ("source_port", "sourceport", "src_port", "srcport", "sport"),
        "dest_port": ("dest_port", "destport", "dst_port", "dstport", "dport", "port"),
        "protocol_id": ("protocol_id", "protocolid", "pid", "proto_id"),
        "unit_id": ("unit_id", "unitid", "uid", "slave_id", "slaveid"),
        "quantity": ("quantity", "qty", "count", "register_count", "num_registers"),
        "direction": ("direction", "dir", "msg_type", "pdu_type"),
    }
)
"""Canonical name -> spellings seen in synthetic data, CIC-like exports and pcaps."""


def normalize_column_name(name: str) -> str:
    """Fold a header to its comparison key: lowercase alphanumerics only."""
    return re.sub(r"[^a-z0-9]", "", str(name).strip().lower())


def _build_alias_index() -> dict[str, str]:
    index: dict[str, str] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in (canonical, *aliases):
            index[normalize_column_name(alias)] = canonical
    return index


ALIAS_TO_CANONICAL: Final[Mapping[str, str]] = MappingProxyType(_build_alias_index())
"""Normalised alias -> canonical column name, ready for header mapping."""

DIRECTIONS: Final[tuple[str, ...]] = ("request", "response", "unknown")
