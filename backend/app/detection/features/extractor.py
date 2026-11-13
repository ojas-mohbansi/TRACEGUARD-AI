"""
Feature extraction module for TraceGuard AI.
Extracts per-session feature vectors from protocol events.
"""
from typing import List, Dict, Any, Union, Optional
import numpy as np
import pandas as pd


# Inline HTTP FSM Transition Table as defined in API_CONTRACTS.md
VALID_TRANSITIONS = {
    ("IDLE", "CONNECT"): "CONNECTED",
    ("CONNECTED", "REQUEST"): "REQUEST_RECEIVED",
    ("CONNECTED", "TIMEOUT"): "CLOSED",
    ("REQUEST_RECEIVED", "AUTH_SUCCESS"): "AUTH_CHECKED",
    ("REQUEST_RECEIVED", "AUTH_FAILURE"): "AUTH_FAILED",
    ("REQUEST_RECEIVED", "MALFORMED"): "ERROR",
    ("AUTH_CHECKED", "RESPONSE_200"): "RESPONSE_SENT",
    ("AUTH_CHECKED", "RESPONSE_301"): "RESPONSE_SENT",
    ("AUTH_CHECKED", "RESPONSE_500"): "ERROR",
    ("AUTH_FAILED", "RESPONSE_401"): "RESPONSE_SENT",
    ("AUTH_FAILED", "RESPONSE_403"): "RESPONSE_SENT",
    ("RESPONSE_SENT", "REQUEST"): "REQUEST_RECEIVED",
    ("RESPONSE_SENT", "CLOSE"): "CLOSED",
    ("ERROR", "CLOSE"): "CLOSED",
    ("ERROR", "ERROR_RESPONSE"): "RESPONSE_SENT",
}

FEATURE_COLUMNS = [
    "event_count",
    "unique_event_types",
    "session_duration_seconds",
    "avg_inter_event_time",
    "std_inter_event_time",
    "invalid_transition_count",
    "auth_failure_count",
    "error_count",
    "response_2xx_ratio",
    "response_4xx_ratio",
    "response_5xx_ratio",
    "avg_bytes",
    "has_close",
    "request_rate",
    "unique_methods",
]


class FeatureExtractor:
    """Extracts 15 tabular features from network event sequences per session."""

    def __init__(self):
        self.feature_columns = FEATURE_COLUMNS

    @staticmethod
    def _parse_timestamp(ts: Any) -> Optional[pd.Timestamp]:
        if ts is None or pd.isna(ts):
            return None
        if isinstance(ts, pd.Timestamp):
            return ts
        try:
            return pd.to_datetime(ts)
        except Exception:
            return None

    @staticmethod
    def _safe_status_code(val: Any) -> Optional[int]:
        if val is None or pd.isna(val):
            return None
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_float(val: Any, default: float = 0.0) -> float:
        if val is None or pd.isna(val):
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    def extract_session_features(self, events: List[Union[Dict[str, Any], Any]]) -> Dict[str, float]:
        """
        Extract 15 features from a list of events belonging to a single session.
        Events are expected to be dicts or objects with keys/attributes:
        - timestamp, event_type, method, status_code, bytes
        """
        if not events:
            return {col: 0.0 for col in self.feature_columns}

        # Normalize events to list of dicts
        norm_events = []
        for e in events:
            if isinstance(e, dict):
                norm_events.append(e)
            else:
                norm_events.append({
                    "event_id": getattr(e, "event_id", ""),
                    "session_id": getattr(e, "session_id", ""),
                    "timestamp": getattr(e, "timestamp", None),
                    "event_type": getattr(e, "event_type", ""),
                    "method": getattr(e, "method", None),
                    "status_code": getattr(e, "status_code", None),
                    "bytes": getattr(e, "bytes", 0),
                    "protocol": getattr(e, "protocol", "HTTP"),
                })

        # Sort events by timestamp if available
        try:
            norm_events.sort(key=lambda x: self._parse_timestamp(x["timestamp"]) or pd.Timestamp.min)
        except Exception:
            pass

        n_events = len(norm_events)
        event_types = [str(e.get("event_type", "")) for e in norm_events if e.get("event_type") and not pd.isna(e.get("event_type"))]
        unique_event_types = len(set(event_types))

        # Timestamps & durations
        parsed_ts = [self._parse_timestamp(e["timestamp"]) for e in norm_events if e.get("timestamp") is not None and not pd.isna(e.get("timestamp"))]
        timestamps = [ts for ts in parsed_ts if ts is not None]
        if len(timestamps) >= 2:
            duration = max(0.0, (timestamps[-1] - timestamps[0]).total_seconds())
            inter_times = [
                max(0.0, (timestamps[i] - timestamps[i - 1]).total_seconds())
                for i in range(1, len(timestamps))
            ]
            avg_inter_time = float(np.mean(inter_times)) if inter_times else 0.0
            std_inter_time = float(np.std(inter_times)) if inter_times else 0.0
        elif len(timestamps) == 1:
            duration = 0.0
            avg_inter_time = 0.0
            std_inter_time = 0.0
        else:
            duration = 0.0
            avg_inter_time = 0.0
            std_inter_time = 0.0

        # FSM invalid transition count
        current_state = "IDLE"
        invalid_transition_count = 0
        for e in norm_events:
            ev_type = str(e.get("event_type", ""))
            key = (current_state, ev_type)
            if key in VALID_TRANSITIONS:
                current_state = VALID_TRANSITIONS[key]
            else:
                invalid_transition_count += 1

        # Counts & ratios
        auth_failure_count = sum(1 for e in norm_events if e.get("event_type") == "AUTH_FAILURE")
        
        # Error count: MALFORMED, RESPONSE_500, status_code >= 500, or event_type containing ERROR
        error_count = 0
        status_codes = []
        for e in norm_events:
            ev_type = str(e.get("event_type", ""))
            sc = self._safe_status_code(e.get("status_code"))
            if sc is not None:
                status_codes.append(sc)
            if ev_type in ("MALFORMED", "RESPONSE_500", "ERROR", "ERROR_RESPONSE") or (sc is not None and sc >= 500):
                error_count += 1

        total_status_codes = len(status_codes)
        resp_2xx = sum(1 for sc in status_codes if 200 <= sc < 300)
        resp_4xx = sum(1 for sc in status_codes if 400 <= sc < 500)
        resp_5xx = sum(1 for sc in status_codes if 500 <= sc < 600)

        # Fallback to event_type if status_code wasn't explicit
        if total_status_codes == 0:
            resp_2xx = sum(1 for e in norm_events if e.get("event_type") in ("RESPONSE_200", "RESPONSE_301"))
            resp_4xx = sum(1 for e in norm_events if e.get("event_type") in ("RESPONSE_401", "RESPONSE_403"))
            resp_5xx = sum(1 for e in norm_events if e.get("event_type") == "RESPONSE_500")
            denom = resp_2xx + resp_4xx + resp_5xx
            response_2xx_ratio = float(resp_2xx / denom) if denom > 0 else 0.0
            response_4xx_ratio = float(resp_4xx / denom) if denom > 0 else 0.0
            response_5xx_ratio = float(resp_5xx / denom) if denom > 0 else 0.0
        else:
            response_2xx_ratio = float(resp_2xx / total_status_codes)
            response_4xx_ratio = float(resp_4xx / total_status_codes)
            response_5xx_ratio = float(resp_5xx / total_status_codes)

        byte_values = []
        for e in norm_events:
            b = e.get("bytes")
            if b is not None and not pd.isna(b):
                try:
                    byte_values.append(float(b))
                except Exception:
                    byte_values.append(0.0)
            else:
                byte_values.append(0.0)

        avg_bytes = float(np.mean(byte_values)) if byte_values else 0.0

        has_close = 1.0 if any(e.get("event_type") == "CLOSE" for e in norm_events) else 0.0

        # Request rate: requests per second
        request_count = sum(1 for e in norm_events if e.get("event_type") == "REQUEST")
        if duration > 0.0:
            request_rate = float(request_count / duration)
        else:
            request_rate = float(request_count)

        methods = [
            str(e.get("method")) for e in norm_events
            if e.get("method") and not pd.isna(e.get("method"))
        ]
        unique_methods = len(set(methods))

        return {
            "event_count": float(n_events),
            "unique_event_types": float(unique_event_types),
            "session_duration_seconds": float(duration),
            "avg_inter_event_time": float(avg_inter_time),
            "std_inter_event_time": float(std_inter_time),
            "invalid_transition_count": float(invalid_transition_count),
            "auth_failure_count": float(auth_failure_count),
            "error_count": float(error_count),
            "response_2xx_ratio": float(response_2xx_ratio),
            "response_4xx_ratio": float(response_4xx_ratio),
            "response_5xx_ratio": float(response_5xx_ratio),
            "avg_bytes": float(avg_bytes),
            "has_close": float(has_close),
            "request_rate": float(request_rate),
            "unique_methods": float(unique_methods),
        }

    def extract_batch(self, sessions: Union[Dict[str, List[Any]], pd.DataFrame, List[List[Any]]]) -> pd.DataFrame:
        """
        Extract features for multiple sessions.
        Accepts:
        - Dict of {session_id: [events]}
        - DataFrame containing a 'session_id' column
        - List of event lists
        Returns pd.DataFrame with session_id column and 15 feature columns.
        """
        rows = []
        session_ids = []

        if isinstance(sessions, pd.DataFrame):
            if "session_id" in sessions.columns:
                for sid, group in sessions.groupby("session_id", sort=False):
                    session_ids.append(str(sid))
                    events = group.to_dict(orient="records")
                    rows.append(self.extract_session_features(events))
            else:
                session_ids.append("session_0")
                rows.append(self.extract_session_features(sessions.to_dict(orient="records")))
        elif isinstance(sessions, dict):
            for sid, evs in sessions.items():
                session_ids.append(str(sid))
                rows.append(self.extract_session_features(evs))
        elif isinstance(sessions, list):
            for i, evs in enumerate(sessions):
                sid = f"session_{i}"
                if evs and isinstance(evs[0], dict) and "session_id" in evs[0]:
                    sid = str(evs[0]["session_id"])
                session_ids.append(sid)
                rows.append(self.extract_session_features(evs))
        else:
            raise ValueError(f"Unsupported input type for extract_batch: {type(sessions)}")

        df = pd.DataFrame(rows, columns=self.feature_columns)
        df.insert(0, "session_id", session_ids)
        return df
