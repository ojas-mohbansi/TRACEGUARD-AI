"""
Evaluation module for detection engines in TraceGuard AI.
Computes metrics: Precision, Recall, F1, Detection Rate, FPR, False Alarms per 100 benign, TP/FP/TN/FN.
Supports multi-engine side-by-side comparison.
"""
from typing import Dict, Any, List, Union
import numpy as np


class Evaluator:
    """Evaluates detection performance against ground truth labels."""

    @staticmethod
    def evaluate_engine(
        predictions: List[Dict[str, Any]],
        ground_truth: Union[Dict[str, str], List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """
        Evaluate single engine predictions.
        predictions: list of {session_id: str, prediction: "normal"|"anomalous", processing_time_ms: float, ...}
        ground_truth: dict {session_id: "normal"|"anomalous"} or list of {session_id, label}
        """
        if isinstance(ground_truth, list):
            gt_dict = {
                str(item.get("session_id")): str(item.get("label", item.get("actual", "normal"))).lower()
                for item in ground_truth
            }
        else:
            gt_dict = {str(k): str(v).lower() for k, v in ground_truth.items()}

        tp = 0
        fp = 0
        tn = 0
        fn = 0
        processing_times = []
        detail_predictions = []

        for p in predictions:
            sid = str(p.get("session_id"))
            pred = str(p.get("prediction", "normal")).lower()
            actual = gt_dict.get(sid, "normal")
            ptime = float(p.get("processing_time_ms", 0.0) or 0.0)
            processing_times.append(ptime)

            is_correct = (pred == actual)
            detail_predictions.append({
                "session_id": sid,
                "prediction": pred,
                "actual": actual,
                "correct": is_correct,
            })

            if actual == "anomalous":
                if pred == "anomalous":
                    tp += 1
                else:
                    fn += 1
            else:  # actual == "normal"
                if pred == "anomalous":
                    fp += 1
                else:
                    tn += 1

        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        
        # Detection Rate is synonymous with recall/sensitivity
        detection_rate = recall

        # False Positive Rate = FP / (FP + TN)
        benign_total = fp + tn
        fpr = float(fp / benign_total) if benign_total > 0 else 0.0

        # False alarms per 100 benign sessions
        false_alarms_per_100 = float(fpr * 100.0)

        avg_proc_time = float(np.mean(processing_times)) if processing_times else 0.0

        return {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "detection_rate": round(detection_rate, 4),
            "false_positive_rate": round(fpr, 4),
            "false_alarms_per_100_benign": round(false_alarms_per_100, 2),
            "avg_processing_time_ms": round(avg_proc_time, 2),
            "true_positives": int(tp),
            "false_positives": int(fp),
            "true_negatives": int(tn),
            "false_negatives": int(fn),
            "predictions": detail_predictions,
        }

    @classmethod
    def compare_engines(
        cls,
        engine_results: Dict[str, List[Dict[str, Any]]],
        ground_truth: Union[Dict[str, str], List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """
        Compare multiple detection engines (e.g., {"fsm": [...], "ml": [...], "hybrid": [...]})
        against ground truth.
        """
        engines_metrics = {}
        for engine_name, preds in engine_results.items():
            engines_metrics[engine_name] = cls.evaluate_engine(preds, ground_truth)

        total_sessions = len(ground_truth) if isinstance(ground_truth, (dict, list)) else 0
        return {
            "total_sessions": total_sessions,
            "engines": engines_metrics,
        }
