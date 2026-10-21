"""Tests for the Phase 2.1 Tier-1 deterministic protocol FSM.

The suite is organised around the engine's four obligations:

* key a conversation without direction, so a request and its response share
  one state;
* resolve the request/response role from the wire rather than from labels;
* apply the declared transition table and the transaction-correlation rules;
* keep the memory bounded and report every verdict with full provenance.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from modbus_nids import (
    VERDICT_COLUMNS,
    ConversationKey,
    FSMConfig,
    FSMNote,
    FSMReason,
    ModbusFSM,
    ModbusRecord,
    RoleSource,
    SessionState,
    SymbolClass,
    Tier1Result,
    TransitionTarget,
    evaluate_tier1,
    generate_synthetic_logs,
    parse_dataframe,
)
from modbus_nids import fsm as fsm_module
from modbus_nids.fsm import TRANSITIONS

TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

CLIENT = "10.0.0.1"
SERVER = "10.0.0.2"


def make_record(**overrides: object) -> ModbusRecord:
    """A client-to-server request, the default shape of a Modbus/TCP event."""
    defaults: dict[str, object] = {
        "timestamp": TS,
        "source_ip": CLIENT,
        "dest_ip": SERVER,
        "tcp_connection": "conn-1",
        "transaction_id": 1,
        "function_code": 3,
        "register_address": 100,
        "data_length": 6,
        "label": 0,
        "source_port": 40000,
        "dest_port": 502,
        "unit_id": 1,
        "quantity": 10,
        "direction": "request",
    }
    defaults.update(overrides)
    return ModbusRecord(**defaults)  # type: ignore[arg-type]


def make_response(**overrides: object) -> ModbusRecord:
    """A server-to-client response."""
    defaults: dict[str, object] = {
        "timestamp": TS,
        "source_ip": SERVER,
        "dest_ip": CLIENT,
        "tcp_connection": "conn-1",
        "transaction_id": 1,
        "function_code": 3,
        "register_address": 100,
        "data_length": 5,
        "label": 0,
        "source_port": 502,
        "dest_port": 40000,
        "unit_id": 1,
        "quantity": 10,
        "direction": "response",
    }
    defaults.update(overrides)
    return ModbusRecord(**defaults)  # type: ignore[arg-type]


def exchange(*records: ModbusRecord) -> list:
    """Observe a sequence of records and return their verdicts."""
    engine = ModbusFSM()
    return [engine.observe(record) for record in records]


# ---------------------------------------------------------------------------
# Conversation key
# ---------------------------------------------------------------------------


def test_conversation_key_label_joins_the_three_parts() -> None:
    key = ConversationKey(CLIENT, SERVER, "conn-1")

    assert key.label == "10.0.0.1|10.0.0.2|conn-1"
    assert str(key) == key.label


def test_request_only_label_matches_the_directional_flow_key() -> None:
    record = make_record()

    verdict = exchange(record)[0]

    assert verdict.session_id == record.flow_key
    assert verdict.session_key == ConversationKey(CLIENT, SERVER, "conn-1")


def test_a_response_joins_the_request_conversation() -> None:
    verdicts = exchange(make_record(transaction_id=5), make_response(transaction_id=5))

    assert verdicts[0].session_id == verdicts[1].session_id
    assert verdicts[0].session_key == verdicts[1].session_key


def test_conversation_keys_are_hashable_and_comparable() -> None:
    key = ConversationKey(CLIENT, SERVER, "conn-1")

    assert key == ConversationKey(CLIENT, SERVER, "conn-1")
    assert key != ConversationKey(CLIENT, SERVER, "conn-2")
    assert len({key, ConversationKey(CLIENT, SERVER, "conn-1")}) == 1


# ---------------------------------------------------------------------------
# Role resolution
# ---------------------------------------------------------------------------


def test_ports_identify_the_server_end() -> None:
    verdict = exchange(make_record(source_port=40000, dest_port=502))[0]

    assert verdict.role_source is RoleSource.PORTS
    assert verdict.direction == "request"
    assert verdict.session_key.client_ip == CLIENT
    assert verdict.session_key.server_ip == SERVER


def test_response_ports_flip_the_endpoint_roles() -> None:
    verdict = exchange(make_response(source_port=502, dest_port=40000))[0]

    assert verdict.role_source is RoleSource.PORTS
    assert verdict.direction == "response"
    assert verdict.session_key.client_ip == CLIENT
    assert verdict.session_key.server_ip == SERVER


def test_ambiguous_ports_fall_back_to_the_declared_direction() -> None:
    verdict = exchange(
        make_record(source_port=502, dest_port=502, direction="response")
    )[0]

    assert verdict.role_source is RoleSource.DECLARED
    assert verdict.direction == "response"


def test_declared_direction_is_used_when_the_ports_are_absent() -> None:
    verdict = exchange(
        make_record(source_port=None, dest_port=None, direction="response")
    )[0]

    assert verdict.role_source is RoleSource.DECLARED
    assert verdict.direction == "response"


def test_learned_roles_are_used_when_nothing_else_is_available() -> None:
    engine = ModbusFSM()
    engine.observe(make_record(transaction_id=1))
    verdict = engine.observe(
        make_record(
            transaction_id=2,
            source_port=None,
            dest_port=None,
            direction="unknown",
        )
    )

    assert verdict.role_source is RoleSource.LEARNED
    assert verdict.direction == "request"


def test_the_default_role_marks_the_direction_as_inferred() -> None:
    verdict = exchange(
        make_record(source_port=None, dest_port=None, direction="unknown")
    )[0]

    assert verdict.role_source is RoleSource.DEFAULT
    assert FSMNote.DIRECTION_INFERRED in verdict.notes
    assert verdict.is_violation is False


def test_a_direction_conflict_is_a_note_and_not_a_violation() -> None:
    verdict = exchange(make_record(direction="response"))[0]

    assert FSMNote.DIRECTION_CONFLICT in verdict.notes
    assert verdict.reason is None
    assert verdict.score == 0.0


def test_the_exception_flag_marks_a_response() -> None:
    verdict = exchange(make_record(function_code=0x83, data_length=3))[0]

    assert verdict.direction == "response"
    assert verdict.symbol.value == "response_exception"
    assert FSMNote.DIRECTION_CONFLICT in verdict.notes


# ---------------------------------------------------------------------------
# The declared transition table
# ---------------------------------------------------------------------------


def test_the_first_request_moves_from_idle_to_request_sent() -> None:
    verdict = exchange(make_record(transaction_id=1))[0]

    assert verdict.state_before is SessionState.IDLE
    assert verdict.state_after is SessionState.REQUEST_SENT
    assert verdict.outstanding == 1


def test_a_second_request_moves_to_waiting_response() -> None:
    verdicts = exchange(
        make_record(transaction_id=1), make_record(transaction_id=2)
    )

    assert verdicts[1].state_before is SessionState.REQUEST_SENT
    assert verdicts[1].state_after is SessionState.WAITING_RESPONSE
    assert verdicts[1].outstanding == 2


def test_a_response_derives_the_state_back_to_idle() -> None:
    verdicts = exchange(
        make_record(transaction_id=7), make_response(transaction_id=7)
    )

    assert verdicts[1].state_before is SessionState.REQUEST_SENT
    assert verdicts[1].state_after is SessionState.IDLE
    assert verdicts[1].outstanding == 0


def test_a_response_keeps_the_state_while_transactions_are_open() -> None:
    verdicts = exchange(
        make_record(transaction_id=1),
        make_record(transaction_id=2),
        make_response(transaction_id=1),
    )

    assert verdicts[2].state_after is SessionState.REQUEST_SENT
    assert verdicts[2].outstanding == 1


def test_the_declared_table_agrees_with_the_derived_state() -> None:
    verdicts = exchange(
        make_record(transaction_id=1),
        make_record(transaction_id=2),
        make_response(transaction_id=2),
        make_response(transaction_id=1),
    )

    assert verdicts[0].state_after is SessionState.REQUEST_SENT
    assert verdicts[1].state_after is SessionState.WAITING_RESPONSE
    assert verdicts[2].state_after is SessionState.REQUEST_SENT
    assert verdicts[3].state_after is SessionState.IDLE
    assert TRANSITIONS[(SessionState.IDLE, SymbolClass.REQUEST)] is (
        TransitionTarget.REQUEST_SENT
    )
    assert TRANSITIONS[(SessionState.REQUEST_SENT, SymbolClass.REQUEST)] is (
        TransitionTarget.WAITING_RESPONSE
    )
    assert TRANSITIONS[(SessionState.REQUEST_SENT, SymbolClass.RESPONSE)] is (
        TransitionTarget.DERIVED
    )


def test_the_table_covers_every_state_and_symbol_class() -> None:
    assert set(TRANSITIONS) == {
        (state, symbol_class)
        for state in SessionState
        for symbol_class in SymbolClass
    }


def test_a_missing_transition_cell_is_an_undefined_transition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        fsm_module,
        "TRANSITIONS",
        {
            key: value
            for key, value in TRANSITIONS.items()
            if key != (SessionState.IDLE, SymbolClass.REQUEST)
        },
    )

    verdict = exchange(make_record())[0]

    assert verdict.reason is FSMReason.UNDEFINED_TRANSITION
    assert verdict.score == 1.0
    assert verdict.decision == "anomaly"
    assert verdict.bypass_ml is True


def test_a_violation_moves_the_conversation_to_error() -> None:
    verdict = exchange(make_response(transaction_id=99))[0]

    assert verdict.reason is FSMReason.RESPONSE_WITHOUT_REQUEST
    assert verdict.state_after is SessionState.ERROR


def test_the_error_state_recovers_on_the_next_valid_event() -> None:
    engine = ModbusFSM()
    engine.observe(make_response(transaction_id=99))
    verdict = engine.observe(make_record(transaction_id=1))

    assert verdict.state_before is SessionState.ERROR
    assert verdict.reason is None
    assert verdict.state_after is SessionState.REQUEST_SENT


# ---------------------------------------------------------------------------
# Hard rules
# ---------------------------------------------------------------------------


def test_a_response_without_a_request_is_a_violation() -> None:
    verdict = exchange(make_response(transaction_id=42))[0]

    assert verdict.reason is FSMReason.RESPONSE_WITHOUT_REQUEST
    assert "no open request" in verdict.detail


def test_a_duplicate_response_is_reported_as_response_after_close() -> None:
    verdicts = exchange(
        make_record(transaction_id=5),
        make_response(transaction_id=5),
        make_response(transaction_id=5),
    )

    assert verdicts[2].reason is FSMReason.RESPONSE_AFTER_CLOSE


def test_a_response_with_the_wrong_function_code_is_a_violation() -> None:
    verdicts = exchange(
        make_record(transaction_id=5, function_code=3),
        make_response(transaction_id=5, function_code=6),
    )

    assert verdicts[1].reason is FSMReason.FUNCTION_CODE_MISMATCH
    assert "does not match" in verdicts[1].detail


def test_an_exception_response_may_answer_a_request() -> None:
    verdicts = exchange(
        make_record(transaction_id=5, function_code=3),
        make_response(transaction_id=5, function_code=0x83, data_length=3),
    )

    assert verdicts[1].reason is None
    assert verdicts[1].outstanding == 0


def test_an_exception_response_with_the_wrong_length_is_a_violation() -> None:
    verdicts = exchange(
        make_record(transaction_id=5, function_code=3),
        make_response(transaction_id=5, function_code=0x83, data_length=4),
    )

    assert verdicts[1].reason is FSMReason.EXCEPTION_LENGTH_INVALID


def test_a_response_with_the_wrong_unit_id_is_a_violation() -> None:
    verdicts = exchange(
        make_record(transaction_id=5, unit_id=1),
        make_response(transaction_id=5, unit_id=7),
    )

    assert verdicts[1].reason is FSMReason.UNIT_ID_MISMATCH


def test_reusing_an_open_transaction_id_is_a_violation() -> None:
    verdicts = exchange(
        make_record(transaction_id=5), make_record(transaction_id=5)
    )

    assert verdicts[1].reason is FSMReason.TRANSACTION_ID_REUSE
    assert "awaiting a response" in verdicts[1].detail


def test_reusing_a_closed_transaction_id_is_a_violation() -> None:
    verdicts = exchange(
        make_record(transaction_id=5),
        make_response(transaction_id=5),
        make_record(transaction_id=5),
    )

    assert verdicts[2].reason is FSMReason.TRANSACTION_ID_REUSE
    assert "already completed" in verdicts[2].detail


def test_an_unsupported_function_code_is_only_checked_when_opted_in() -> None:
    permissive = exchange(make_record(function_code=16))[0]
    strict = exchange(
        make_record(function_code=16),
    )[0]
    engine = ModbusFSM(FSMConfig(supported_function_codes=frozenset({3})))
    verdict = engine.observe(make_record(function_code=16))

    assert permissive.reason is None
    assert strict.reason is None
    assert verdict.reason is FSMReason.UNSUPPORTED_FUNCTION_CODE


def test_a_response_in_an_error_session_without_a_match_is_a_violation() -> None:
    engine = ModbusFSM()
    engine.observe(make_response(transaction_id=99))
    verdict = engine.observe(make_response(transaction_id=98))

    assert verdict.reason is FSMReason.SESSION_IN_ERROR
    assert verdict.state_before is SessionState.ERROR


def test_a_violation_leaves_the_open_transaction_intact() -> None:
    engine = ModbusFSM()
    engine.observe(make_record(transaction_id=5))
    engine.observe(make_response(transaction_id=5, function_code=6))

    assert engine.outstanding_count == 1


# ---------------------------------------------------------------------------
# The verdict contract
# ---------------------------------------------------------------------------


def test_a_clean_event_scores_zero_and_is_forwarded_to_the_ml_tier() -> None:
    verdict = exchange(make_record())[0]

    assert verdict.score == 0.0
    assert verdict.decision == "benign"
    assert verdict.bypass_ml is False
    assert verdict.reason is None


def test_a_violation_scores_one_and_bypasses_the_ml_tier() -> None:
    verdict = exchange(make_response(transaction_id=42))[0]

    assert verdict.score == 1.0
    assert verdict.decision == "anomaly"
    assert verdict.bypass_ml is True


def test_the_verdict_carries_its_provenance() -> None:
    record = make_record(transaction_id=9, raw_index=17)
    verdict = exchange(record)[0]

    assert verdict.raw_index == 17
    assert verdict.transaction_id == 9
    assert verdict.function_code == 3
    assert verdict.session_id == "10.0.0.1|10.0.0.2|conn-1"
    assert verdict.symbol_class is SymbolClass.REQUEST
    assert verdict.notes == ()


def test_the_verdict_serialises_to_plain_python() -> None:
    verdict = exchange(make_record())[0]
    payload = verdict.to_dict()

    assert payload["decision"] == "benign"
    assert payload["state_before"] == "idle"
    assert payload["notes"] == []
    assert payload["reason"] == ""


def test_an_unanswered_request_is_legal_and_reported_as_incomplete() -> None:
    engine = ModbusFSM()
    verdicts = [engine.observe(make_record(transaction_id=index)) for index in range(3)]
    summary = engine.finish()

    assert all(verdict.reason is None for verdict in verdicts)
    assert summary.incomplete_transactions == 3
    assert summary.violations == 0
    assert summary.notes["incomplete_transaction"] == 3


def test_notes_are_known_codes() -> None:
    verdict = exchange(make_record(direction="response"))[0]

    assert all(isinstance(note, FSMNote) for note in verdict.notes)


# ---------------------------------------------------------------------------
# Bounded memory
# ---------------------------------------------------------------------------


def test_outstanding_transactions_are_bounded() -> None:
    engine = ModbusFSM(FSMConfig(max_outstanding=2))
    verdicts = [
        engine.observe(make_record(transaction_id=index)) for index in range(3)
    ]

    assert engine.outstanding_count == 2
    assert FSMNote.OUTSTANDING_EVICTED in verdicts[2].notes


def test_the_closed_transaction_ring_is_bounded() -> None:
    engine = ModbusFSM(FSMConfig(tid_history=2))
    for index in range(1, 4):
        engine.observe(make_record(transaction_id=index))
        engine.observe(make_response(transaction_id=index))
    verdict = engine.observe(make_record(transaction_id=1))

    assert verdict.reason is None


def test_max_sessions_evicts_the_least_recently_used_conversation() -> None:
    engine = ModbusFSM(FSMConfig(max_sessions=1))
    engine.observe(make_record(tcp_connection="A"))
    verdict = engine.observe(make_record(tcp_connection="B"))

    assert engine.session_count == 1
    assert engine.evicted_sessions == 1
    assert FSMNote.SESSION_EVICTED in verdict.notes


def test_the_learned_role_map_is_bounded_by_the_session_cap() -> None:
    engine = ModbusFSM(FSMConfig(max_sessions=2))
    for index in range(5):
        engine.observe(
            make_record(
                tcp_connection=f"conn-{index}",
                source_port=None,
                dest_port=None,
                direction="unknown",
            )
        )

    # The map is internal, but an unbounded role map is a slow leak.
    assert len(engine._roles) <= 2


def test_the_most_recent_connection_keeps_its_learned_role() -> None:
    engine = ModbusFSM(FSMConfig(max_sessions=1))
    engine.observe(
        make_record(tcp_connection="A", source_port=None, dest_port=None, direction="unknown")
    )
    engine.observe(
        make_record(tcp_connection="B", source_port=None, dest_port=None, direction="unknown")
    )

    verdict = engine.observe(
        make_response(tcp_connection="B", source_port=None, dest_port=None, direction="unknown")
    )

    assert verdict.role_source is RoleSource.LEARNED
    assert verdict.direction == "response"


def test_prune_evicts_idle_conversations() -> None:
    engine = ModbusFSM()
    engine.observe(make_record(timestamp=TS, tcp_connection="A"))

    evicted = engine.prune(TS + timedelta(seconds=10), idle_timeout=5)

    assert evicted == 1
    assert engine.session_count == 0


def test_prune_requires_a_policy() -> None:
    engine = ModbusFSM()
    engine.observe(make_record())

    with pytest.raises(ValueError, match="idle_timeout"):
        engine.prune()


def test_reset_clears_every_conversation_and_counter() -> None:
    engine = ModbusFSM()
    engine.observe(make_record())
    engine.reset()

    assert engine.session_count == 0
    assert engine.outstanding_count == 0
    assert engine.finish().events == 0


def test_a_response_timeout_expires_stale_transactions() -> None:
    engine = ModbusFSM(FSMConfig(response_timeout=5.0))
    engine.observe(make_record(transaction_id=1, timestamp=TS))
    verdict = engine.observe(make_record(transaction_id=2, timestamp=TS + timedelta(seconds=10)))

    assert FSMNote.TRANSACTION_EXPIRED in verdict.notes
    assert engine.outstanding_count == 1


# ---------------------------------------------------------------------------
# Batch API
# ---------------------------------------------------------------------------


def test_evaluate_accepts_records_frames_and_ingest_results() -> None:
    records = [make_record(transaction_id=index) for index in range(3)]
    result = parse_dataframe(
        pd.DataFrame.from_records([record.as_row() for record in records])
    )

    from_records = ModbusFSM().evaluate(records)
    from_frame = ModbusFSM().evaluate(result.frame)
    from_result = ModbusFSM().evaluate(result)

    assert len(from_records) == len(from_frame) == len(from_result) == 3
    assert from_records.scores.tolist() == from_frame.scores.tolist()
    assert from_records.scores.tolist() == from_result.scores.tolist()


def test_evaluate_resets_the_engine_between_batches() -> None:
    engine = ModbusFSM()
    engine.observe(make_record(transaction_id=1))
    engine.evaluate([make_record(transaction_id=2)])

    assert engine.finish().events == 1
    assert engine.outstanding_count == 1


def test_evaluate_rejects_non_records() -> None:
    with pytest.raises(TypeError, match="ModbusRecord"):
        ModbusFSM().evaluate([make_record(), "not-a-record"])  # type: ignore[list-item]


def test_evaluate_tier1_is_the_one_call_api() -> None:
    result = evaluate_tier1([make_record(), make_response(transaction_id=42)])

    assert isinstance(result, Tier1Result)
    assert len(result) == 2
    assert result.n_violations == 1
    assert result.violation_rate == pytest.approx(0.5)


def test_the_result_frame_has_a_pinned_schema() -> None:
    frame = evaluate_tier1([make_record()]).to_frame()

    assert list(frame.columns) == list(VERDICT_COLUMNS)
    assert frame["raw_index"].dtype == "int64"
    assert frame["fsm_score"].dtype == "float64"
    assert frame["fsm_bypass_ml"].dtype == "bool"
    assert frame["fsm_session_id"].dtype == "string"


def test_an_empty_result_frame_matches_the_populated_schema() -> None:
    empty = evaluate_tier1([]).to_frame()
    populated = evaluate_tier1([make_record()]).to_frame()

    assert empty.empty
    assert list(empty.columns) == list(populated.columns)
    assert empty.dtypes.equals(populated.dtypes)


def test_the_result_exposes_arrays_and_counts() -> None:
    result = evaluate_tier1(
        [make_record(), make_response(transaction_id=42), make_record(transaction_id=2)]
    )

    assert result.scores.tolist() == [0.0, 1.0, 0.0]
    assert result.decisions.tolist() == ["benign", "anomaly", "benign"]
    assert result.anomaly_mask.tolist() == [False, True, False]
    assert result.n_sessions == 1
    assert result.reasons[FSMReason.RESPONSE_WITHOUT_REQUEST] == 1


def test_the_summary_reports_counts_and_reasons() -> None:
    engine = ModbusFSM()
    engine.evaluate([make_record(), make_response(transaction_id=42)])
    summary = engine.finish()
    payload = summary.to_dict()

    assert payload["events"] == 2
    assert payload["violations"] == 1
    assert payload["reasons"] == {"response_without_request": 1}
    assert "response_without_request" in summary.summary()


# ---------------------------------------------------------------------------
# The synthetic corpus
# ---------------------------------------------------------------------------


def test_benign_traffic_produces_no_violations() -> None:
    frame = generate_synthetic_logs(
        n_sessions=20, events_per_session=40, anomaly_rate=0.0, seed=3
    )
    result = parse_dataframe(frame)

    tier1 = evaluate_tier1(result)

    assert tier1.n_violations == 0
    assert tier1.violation_rate == 0.0


def test_every_violation_falls_on_a_labelled_anomaly() -> None:
    frame = generate_synthetic_logs(
        n_sessions=40, events_per_session=60, anomaly_rate=0.03, seed=42
    )
    result = parse_dataframe(frame)

    tier1 = evaluate_tier1(result)
    labels = result.frame["label"].to_numpy()

    assert tier1.n_violations > 0
    assert all(labels[verdict.raw_index] == 1 for verdict in tier1.verdicts if verdict.is_violation)


def test_the_injected_protocol_anomalies_are_detected() -> None:
    frame = generate_synthetic_logs(
        n_sessions=40, events_per_session=60, anomaly_rate=0.03, seed=42
    )
    result = parse_dataframe(frame)

    tier1 = evaluate_tier1(result)
    reasons = {reason.value for reason in tier1.reasons}

    assert "transaction_id_reuse" in reasons
    assert "response_without_request" in reasons


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"allowed_ports": frozenset()}, "allowed_ports"),
        ({"allowed_ports": frozenset({0})}, "allowed_ports"),
        ({"allowed_ports": frozenset({70000})}, "allowed_ports"),
        ({"max_outstanding": 0}, "max_outstanding"),
        ({"max_outstanding": 1}, "max_outstanding"),
        ({"max_outstanding": 2.5}, "max_outstanding"),
        ({"max_outstanding": True}, "max_outstanding"),
        ({"tid_history": 0}, "tid_history"),
        ({"tid_history": -1}, "tid_history"),
        ({"max_sessions": 0}, "max_sessions"),
        ({"response_timeout": 0.0}, "response_timeout"),
        ({"response_timeout": float("inf")}, "response_timeout"),
        ({"supported_function_codes": frozenset({0})}, "supported_function_codes"),
        ({"supported_function_codes": frozenset({200})}, "supported_function_codes"),
    ],
)
def test_invalid_configuration_is_rejected(
    kwargs: dict[str, object], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        FSMConfig(**kwargs)  # type: ignore[arg-type]


def test_strict_direction_rejects_an_unresolvable_direction() -> None:
    engine = ModbusFSM(FSMConfig(strict_direction=True))
    verdict = engine.observe(
        make_record(source_port=None, dest_port=None, direction="unknown")
    )

    assert verdict.reason is FSMReason.DIRECTION_UNRESOLVED
    assert verdict.bypass_ml is True
