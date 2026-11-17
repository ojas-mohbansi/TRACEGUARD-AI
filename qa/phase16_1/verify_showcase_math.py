import os
import sys
import json

sys.path.insert(0, os.path.abspath("backend"))

from app.api.showcase import _create_showcase_events
from app.detection.fsm import FSMEngine
from app.detection.ml import MLEngine
from app.detection.hybrid import HybridEngine

def verify_math():
    fsm_eng = FSMEngine()
    ml_eng = MLEngine()
    hybrid_eng = HybridEngine(fsm_engine=fsm_eng, ml_engine=ml_eng, fsm_weight=0.6, ml_weight=0.4)
    
    scenarios = ["normal", "fsm_only", "ml_only", "hybrid"]
    audit_results = {}
    
    for sc in scenarios:
        events = _create_showcase_events(sc, f"sess_math_{sc}", "default-workspace")
        event_dicts = [
            {
                "event_id": e.event_id,
                "session_id": e.session_id,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "protocol": e.protocol,
                "event_type": e.event_type,
                "source": e.source,
                "destination": e.destination,
                "method": e.method,
                "path_category": e.path_category,
                "status_code": e.status_code,
                "bytes": e.bytes,
                "label": e.label
            }
            for e in events
        ]
        
        fsm_res = fsm_eng.validate_session(event_dicts)
        ml_res = ml_eng.predict_session(event_dicts)
        hyb_res = hybrid_eng.detect_session(event_dicts)
        
        fsm_violation = fsm_res.get("fsm_violation", False)
        fsm_score = float(fsm_res.get("risk_score", 0))
        ml_score = float(ml_res.get("anomaly_score", 0.0)) * 100.0
        
        raw_combined = (0.6 * fsm_score) + (0.4 * ml_score)
        if fsm_violation:
            combined_with_floor = max(raw_combined, 60.0)
        else:
            combined_with_floor = raw_combined
            
        calculated_risk = int(round(min(100.0, max(0.0, combined_with_floor))))
        actual_risk = hyb_res["risk_score"]
        attribution = hyb_res["attribution"]
        
        audit_results[sc] = {
            "scenario": sc,
            "fsm_violation": fsm_violation,
            "fsm_score": fsm_score,
            "ml_anomaly_score": round(ml_res.get("anomaly_score", 0.0), 4),
            "ml_score": round(ml_score, 2),
            "ml_anomalous": hyb_res["ml_anomalous"],
            "raw_formula": f"0.6 * {fsm_score} + 0.4 * {ml_score:.2f} = {raw_combined:.2f}",
            "floor_applied": bool(fsm_violation and raw_combined < 60.0),
            "combined_score": round(combined_with_floor, 2),
            "calculated_risk_score": calculated_risk,
            "actual_risk_score": actual_risk,
            "math_exact_match": (calculated_risk == actual_risk),
            "attribution": attribution,
            "engine_output": hyb_res["engine"]
        }
        
    print("=== SHOWCASE SCENARIO MATHEMATICAL RECONCILIATION ===")
    print(json.dumps(audit_results, indent=2))
    
    with open("qa/phase16_1/showcase_math_audit.json", "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)

if __name__ == "__main__":
    verify_math()
