"""Test suite for TraceGuard AI ML Engine."""

import os
from pathlib import Path
import pandas as pd
import pytest

from backend.app.detection.features.extractor import FeatureExtractor, FEATURE_COLUMNS
from backend.app.detection.ml.engine import MLEngine
from backend.app.evaluation.evaluator import Evaluator


@pytest.fixture
def feature_extractor():
    return FeatureExtractor()


@pytest.fixture
def ml_engine():
    return MLEngine()


def test_feature_extraction_produces_15_features(feature_extractor):
    """1. Verify feature extraction produces exactly 15 features."""
    assert len(FEATURE_COLUMNS) == 15
    events = [
        {
            "event_id": "evt_1",
            "session_id": "sess_test",
            "timestamp": "2026-11-13T10:00:00",
            "protocol": "HTTP",
            "event_type": "CONNECT",
            "method": "CONNECT",
            "status_code": 0,
            "bytes": 100,
        },
        {
            "event_id": "evt_2",
            "session_id": "sess_test",
            "timestamp": "2026-11-13T10:00:01",
            "protocol": "HTTP",
            "event_type": "REQUEST",
            "method": "GET",
            "status_code": 0,
            "bytes": 250,
        },
        {
            "event_id": "evt_3",
            "session_id": "sess_test",
            "timestamp": "2026-11-13T10:00:02",
            "protocol": "HTTP",
            "event_type": "RESPONSE_200",
            "method": "GET",
            "status_code": 200,
            "bytes": 1200,
        },
        {
            "event_id": "evt_4",
            "session_id": "sess_test",
            "timestamp": "2026-11-13T10:00:03",
            "protocol": "HTTP",
            "event_type": "CLOSE",
            "method": "CLOSE",
            "status_code": 0,
            "bytes": 50,
        },
    ]
    feats = feature_extractor.extract_session_features(events)
    assert len(feats) == 15
    for col in FEATURE_COLUMNS:
        assert col in feats
        assert isinstance(feats[col], (int, float))


def test_model_file_exists():
    """2. Verify model file exists at models/isolation_forest.joblib."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    model_path = root_dir / "models" / "isolation_forest.joblib"
    assert model_path.exists(), f"Model file not found at {model_path}"
    assert model_path.stat().st_size > 0


def test_anomaly_scores_range_and_predict(ml_engine, feature_extractor):
    """3. Verify anomaly scores are in [0.0, 1.0] range."""
    # Test on synthetic test dataset
    root_dir = Path(__file__).resolve().parent.parent.parent
    test_path = root_dir / "datasets" / "synthetic" / "test_data.csv"
    assert test_path.exists()

    test_df = pd.read_csv(test_path)
    grouped = test_df.groupby("session_id")
    features_list = []
    for sid, group in list(grouped)[:10]:
        f = feature_extractor.extract_session_features(group.to_dict("records"))
        f["session_id"] = sid
        features_list.append(f)

    f_df = pd.DataFrame(features_list)
    results = ml_engine.predict(f_df)
    assert len(results) == len(features_list)

    for res in results:
        assert res["engine"] == "ml"
        assert res["prediction"] in ["normal", "anomalous"]
        assert 0 <= res["risk_score"] <= 100
        assert 0.0 <= res["ml_anomaly_score"] <= 1.0
        assert res["severity"] in ["low", "medium", "high", "critical"]


def test_higher_scores_more_suspicious(ml_engine, feature_extractor):
    """4. Verify higher scores = more suspicious (anomalous sessions score higher than clean normal sessions)."""
    # Clean normal session
    clean_events = [
        {"session_id": "s_clean", "timestamp": "2026-11-13T10:00:00", "event_type": "CONNECT", "method": "CONNECT", "status_code": 0, "bytes": 100},
        {"session_id": "s_clean", "timestamp": "2026-11-13T10:00:01", "event_type": "REQUEST", "method": "GET", "status_code": 0, "bytes": 200},
        {"session_id": "s_clean", "timestamp": "2026-11-13T10:00:02", "event_type": "AUTH_SUCCESS", "method": "GET", "status_code": 0, "bytes": 50},
        {"session_id": "s_clean", "timestamp": "2026-11-13T10:00:03", "event_type": "RESPONSE_200", "method": "GET", "status_code": 200, "bytes": 1500},
        {"session_id": "s_clean", "timestamp": "2026-11-13T10:00:04", "event_type": "CLOSE", "method": "CLOSE", "status_code": 0, "bytes": 50},
    ]

    # Extreme attack session: massive invalid transitions, 5xx errors, abnormal bytes
    attack_events = [
        {"session_id": "s_attack", "timestamp": f"2026-11-13T10:00:0{i}", "event_type": "RESPONSE_500", "method": "POST", "status_code": 500, "bytes": 999999}
        for i in range(8)
    ]

    clean_feats = feature_extractor.extract_session_features(clean_events)
    clean_feats["session_id"] = "s_clean"

    attack_feats = feature_extractor.extract_session_features(attack_events)
    attack_feats["session_id"] = "s_attack"

    df = pd.DataFrame([clean_feats, attack_feats])
    preds = ml_engine.predict(df)
    pred_map = {p["session_id"]: p for p in preds}

    clean_pred = pred_map["s_clean"]
    attack_pred = pred_map["s_attack"]

    assert attack_pred["ml_anomaly_score"] > clean_pred["ml_anomaly_score"]
    assert attack_pred["risk_score"] >= clean_pred["risk_score"]


def test_no_data_leakage():
    """5. Verify training data and test data don't share sessions (no data leakage)."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    train_path = root_dir / "datasets" / "synthetic" / "training_data.csv"
    test_path = root_dir / "datasets" / "synthetic" / "test_data.csv"

    assert train_path.exists()
    assert test_path.exists()

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    train_sessions = set(train_df["session_id"].unique())
    test_sessions = set(test_df["session_id"].unique())

    overlap = train_sessions.intersection(test_sessions)
    assert len(overlap) == 0, f"Found {len(overlap)} overlapping sessions between train and test datasets!"


def test_evaluation_metrics_reasonable(ml_engine, feature_extractor):
    """6. Run evaluation and verify metrics are reasonable (F1 > 0.5)."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    test_path = root_dir / "datasets" / "synthetic" / "test_data.csv"
    test_df = pd.read_csv(test_path)

    grouped = test_df.groupby("session_id")
    features_list = []
    ground_truth = {}

    for sid, group in grouped:
        f = feature_extractor.extract_session_features(group.to_dict("records"))
        f["session_id"] = sid
        features_list.append(f)
        ground_truth[sid] = group["label"].iloc[0]

    f_df = pd.DataFrame(features_list)
    predictions = ml_engine.predict(f_df)

    metrics = Evaluator.evaluate_engine(predictions, ground_truth)
    assert metrics["f1_score"] > 0.5, f"F1 score {metrics['f1_score']} is not > 0.5"
    assert metrics["precision"] > 0.4
    assert metrics["recall"] > 0.4
    assert metrics["true_positives"] + metrics["false_positives"] + metrics["true_negatives"] + metrics["false_negatives"] == len(grouped)


def test_missing_and_malformed_event_data(ml_engine, feature_extractor):
    """7. Verify missing and malformed event data handled gracefully."""
    # Empty events
    empty_feat = feature_extractor.extract_session_features([])
    assert len(empty_feat) == 15
    pred_empty = ml_engine.predict_session([])
    assert pred_empty["prediction"] == "normal"
    assert pred_empty["risk_score"] == 0

    # Malformed events (None types, string instead of int bytes, missing fields)
    malformed_events = [
        {"session_id": "mal_1", "timestamp": None, "event_type": None, "method": None, "status_code": "unknown", "bytes": "lots"},
        {"session_id": "mal_1", "timestamp": "invalid_date", "event_type": 12345, "method": 999, "status_code": None, "bytes": None},
    ]
    mal_feat = feature_extractor.extract_session_features(malformed_events)
    assert len(mal_feat) == 15
    pred_mal = ml_engine.predict_session(malformed_events)
    assert "ml_anomaly_score" in pred_mal
    assert 0.0 <= pred_mal["ml_anomaly_score"] <= 1.0


def test_reproduce_reported_evaluation_benchmarks(ml_engine, feature_extractor):
    """8. Reproduce reported benchmarks: Test F1 ~0.5312 and Unseen Detection Rate 68%."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    
    # 1. Test data F1 ~ 0.5312
    test_path = root_dir / "datasets" / "synthetic" / "test_data.csv"
    test_df = pd.read_csv(test_path)
    test_feats = feature_extractor.extract_batch(test_df)
    test_preds = ml_engine.predict(test_feats)
    gt_test = test_df.groupby("session_id")["label"].first().to_dict()
    test_metrics = Evaluator.evaluate_engine(test_preds, gt_test)
    assert abs(test_metrics["f1_score"] - 0.5312) < 0.02, f"Expected F1 ~0.5312, got {test_metrics['f1_score']}"

    # 2. Unseen templates detection rate ~ 68%
    unseen_path = root_dir / "datasets" / "synthetic" / "unseen_templates.csv"
    unseen_df = pd.read_csv(unseen_path)
    unseen_feats = feature_extractor.extract_batch(unseen_df)
    unseen_preds = ml_engine.predict(unseen_feats)
    gt_unseen = unseen_df.groupby("session_id")["label"].first().to_dict()
    unseen_metrics = Evaluator.evaluate_engine(unseen_preds, gt_unseen)
    assert abs(unseen_metrics["detection_rate"] - 0.68) < 0.02, f"Expected unseen detection rate ~0.68, got {unseen_metrics['detection_rate']}"

