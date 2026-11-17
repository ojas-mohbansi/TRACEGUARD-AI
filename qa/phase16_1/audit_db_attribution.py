import os
import sys
import json

sys.path.insert(0, os.path.abspath("backend"))

from app.db.database import SessionLocal
from app.models.models import Alert
from sqlalchemy import func

def audit_database_attribution():
    db = SessionLocal()
    try:
        total_alerts = db.query(Alert).count()
        by_engine = db.query(Alert.engine, func.count(Alert.id)).group_by(Alert.engine).all()
        engine_dict = {str(k): v for k, v in by_engine}
        
        sum_engines = sum(engine_dict.values())
        
        # Check showcase alerts vs normal alerts
        demo_alerts = db.query(Alert).filter(Alert.dataset_id == "demo_showcase").count()
        live_or_sim_alerts = total_alerts - demo_alerts
        
        report = {
            "total_alerts_in_db": total_alerts,
            "engine_counts": engine_dict,
            "sum_of_engine_counts": sum_engines,
            "strictly_mutually_exclusive": (sum_engines == total_alerts),
            "demo_showcase_alerts": demo_alerts,
            "standard_alerts": live_or_sim_alerts
        }
        
        print("=== DATABASE ALERT ATTRIBUTION AUDIT ===")
        print(json.dumps(report, indent=2))
        
        with open("qa/phase16_1/database_attribution_audit.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
            
    finally:
        db.close()

if __name__ == "__main__":
    audit_database_attribution()
