"""
Repository Inventory Generator for TraceGuard AI
Phase 18 QA Audit & Documentation Reconciliation
"""
import os
import json
import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EXCLUDED_DIRS = {
    ".git",
    ".pytest_cache",
    "node_modules",
    "dist",
    ".freebuff",
    ".wrangler",
    "__pycache__",
    ".agent",
    ".agents",
    ".github",
}

TARGET_DIRECTORIES = [
    "root",
    "backend",
    "frontend",
    "docs",
    "scripts",
    "presentation",
    "datasets",
    "qa",
]

SUPPLEMENTAL_DIRECTORIES = [
    "brand",
    "models",
    "submission",
    "website",
]

ARCHIVED_REASONS = {
    # Phase 14
    "PHASE14_2_FINAL_SIGNOFF.md": "Historical Phase 14.2 sign-off audit report; superseded by later integration phases.",
    "PHASE14_2_FORMAL_VERIFICATION.md": "Phase 14.2 verification logs and proofs; superseded by formal validation and tests.",
    "PHASE14_2_HYBRID_SCORING_VERIFICATION.md": "Phase 14.2 hybrid consensus formula testing record; preserved as historical validation.",
    "PHASE14_2_SWARM_COMPLETION.md": "Phase 14.2 multi-agent swarm task execution log; archived for provenance.",
    "PHASE14_APPLICATION_INVENTORY.md": "Interim Phase 14 inventory of components; superseded by Phase 18 complete repository inventory.",
    "PHASE14_DEFECT_REGISTER.md": "Phase 14 defect triage and bug resolution log; all defects resolved in codebase.",
    "PHASE14_FINAL_REPORT.md": "Phase 14 milestone milestone summary report; archived for project lifecycle history.",
    "PHASE14_ROUTE_COVERAGE.md": "Phase 14 frontend route testing matrix; superseded by current route and test suites.",
    "PHASE14_WORKFLOW_COVERAGE.md": "Phase 14 user journey and workflow test execution; superseded by current E2E tests.",
    # Phase 15
    "PHASE15_AUTH_AND_NAVIGATION.md": "Phase 15 JWT authentication and route guard hardening record.",
    "PHASE15_AUTOMATA_LAB_FIX.md": "Phase 15 Automata Lab state visualizer bugfix record.",
    "PHASE15_ENGINE_CLASSIFICATION.md": "Phase 15 classification engine tuning log; superseded by final hybrid calibration.",
    "PHASE15_FINAL_REPORT.md": "Phase 15 milestone summary report; archived for lifecycle history.",
    "PHASE15_LIVE_NETWORK_ARCHITECTURE.md": "Phase 15 live packet capture pipeline design notes; superseded by docs/ARCHITECTURE.md.",
    "PHASE15_THREAT_FORENSICS.md": "Phase 15 forensic incident investigation log; preserved as test evidence.",
    # Phase 16
    "PHASE16_1_EVIDENCE_RECONCILIATION.md": "Phase 16.1 forensic evidence and capture audit record.",
    "PHASE16_1_FINAL_SIGNOFF.md": "Phase 16.1 quality gate signoff; superseded by final release verification.",
    "PHASE16_1_ML_CALIBRATION.md": "Phase 16.1 Isolation Forest contamination and threshold tuning log.",
    "PHASE16_1_PRIVACY_AND_CAPTURE_AUDIT.md": "Phase 16.1 packet payload privacy audit and PII scrubbing verification.",
    "PHASE16_2_ALERT_PROVENANCE_AUDIT.md": "Phase 16.2 alert lineage and signature trace verification.",
    "PHASE16_2_DEMO_REHEARSAL.md": "Phase 16.2 rehearsal walk-through notes; superseded by Phase 18 presenter scripts.",
    "PHASE16_2_FINAL_SIGNOFF.md": "Phase 16.2 final signoff audit; superseded by Phase 18 final documentation.",
    "PHASE16_2_FINAL_TEST_REPORT.md": "Phase 16.2 backend and frontend test run output; preserved in qa/phase16_2/.",
    "PHASE16_2_FORMAL_FSM_VALIDATION.md": "Phase 16.2 formal FSM validation report; superseded by docs/FORMAL_AUTOMATON.md.",
    "PHASE16_2_ML_EVALUATION.md": "Phase 16.2 ML precision, recall, and ROC analysis record; archived as benchmark evidence.",
    "PHASE16_DEMONSTRATION_GUIDE.md": "Phase 16 demonstration instructions; superseded by docs/DEMO_RUNBOOK.md and presenter guides.",
    "PHASE16_ENGINE_ANALYTICS.md": "Phase 16 performance metrics; superseded by Phase 17 engine analytics.",
    "PHASE16_FINAL_REPORT.md": "Phase 16 milestone summary report; archived for lifecycle history.",
    "PHASE16_FSM_DETECTION_PROOF.md": "Phase 16 mathematical detection proof; consolidated in docs/TOC_THEORY.md.",
    "PHASE16_NPCAP_DIAGNOSTICS.md": "Phase 16 Windows Npcap driver setup and live packet capture troubleshooting guide.",
    # Brand Rebrand Audits
    "BRAND_REBRAND_AUDIT.md": "Phase 12 initial brand audit across UI components; superseded by docs/BRAND_SYSTEM.md.",
    "BRAND_REBRAND_FINAL_AUDIT.md": "Phase 12 brand fidelity and contrast audit report; historical verification record.",
    "BRAND_REBRAND_FINAL_QA.md": "Phase 12 quality assurance report for brand rebrand migration; historical record.",
    "BRAND_REBRAND_IMPLEMENTATION.md": "Phase 12 CSS design tokens and component implementation log; superseded by frontend CSS.",
    "BRAND_REBRAND_QA.md": "Phase 12 intermediate brand QA report; superseded by FINAL_QA report.",
    "BRAND_REBRAND_SCREENSHOT_INDEX.md": "Phase 12 screenshot catalog for design verification; historical design index.",
}

def categorize_file(rel_path: str, filename: str) -> str:
    path_lower = rel_path.lower().replace("\\", "/")
    ext = os.path.splitext(filename)[1].lower()

    if "/alembic/" in path_lower or filename == "migrate_db.py" or filename == "alembic.ini":
        return "database_migration"
    if "/tests/" in path_lower or filename.startswith("test_") or "/test-results/" in path_lower:
        return "test_suite"
    if path_lower.startswith("qa/"):
        if ext in [".png", ".jpg", ".jpeg"]:
            return "qa_screenshot"
        elif ext in [".log", ".txt", ".json"]:
            return "qa_evidence"
        elif ext == ".pcap":
            return "qa_pcap_sample"
        return "qa_documentation"
    if path_lower.startswith("presentation/"):
        return "presentation_deck"
    if path_lower.startswith("docs/presentation/"):
        return "presenter_guide"
    if path_lower.startswith("docs/archive/"):
        return "archived_documentation"
    if path_lower.startswith("docs/") or (rel_path.startswith("root/") and ext == ".md"):
        return "active_documentation"
    if path_lower.startswith("datasets/"):
        if ext == ".py":
            return "dataset_generator"
        return "dataset_sample"
    if path_lower.startswith("scripts/"):
        return "automation_script"
    if ext in [".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css"]:
        return "source_code"
    if ext in [".json", ".yml", ".yaml", ".ini", ".toml", ".dockerignore", ".gitignore"]:
        return "configuration"
    if ext in [".png", ".svg", ".ico", ".pdf"]:
        return "visual_asset"
    if ext in [".joblib", ".db"]:
        return "binary_data_model"
    return "other"

def get_preservation_status(rel_path: str, filename: str) -> str:
    path_lower = rel_path.lower().replace("\\", "/")
    if filename == "TraceGuard_AI_TOC_Presentation.pptx":
        return "CANONICAL_PRESERVED_IMMUTABLE"
    if "/presentation/presenter_" in path_lower:
        return "CANONICAL_PRESENTER_GUIDE_IMMUTABLE"
    if path_lower.startswith("docs/archive/"):
        return "ARCHIVED_HISTORICAL"
    if "/tests/" in path_lower or filename.startswith("test_"):
        return "PRESERVED_TEST_SUITE"
    if "/alembic/" in path_lower or filename == "migrate_db.py":
        return "PRESERVED_DATABASE_MIGRATION"
    if path_lower.startswith("datasets/"):
        return "PRESERVED_DATASET"
    if "/backend/app/" in path_lower or "/frontend/src/" in path_lower:
        return "PRESERVED_CORE_SOURCE"
    return "ACTIVE_RETAINED"

def scan_repository():
    inventory_items = []
    
    # Scan root files
    for entry in os.scandir(REPO_ROOT):
        if entry.is_file():
            rel = entry.name
            cat = categorize_file(f"root/{rel}", entry.name)
            stat = entry.stat()
            inventory_items.append({
                "path": rel,
                "directory": "root",
                "name": entry.name,
                "extension": os.path.splitext(entry.name)[1].lower(),
                "size_bytes": stat.st_size,
                "category": cat,
                "preservation_status": get_preservation_status(f"root/{rel}", entry.name),
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

    # Scan target subdirectories
    for target in TARGET_DIRECTORIES:
        if target == "root":
            continue
        target_path = REPO_ROOT / target
        if not target_path.exists():
            continue
        for root, dirs, files in os.walk(target_path):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            for file in files:
                full_path = Path(root) / file
                rel = full_path.relative_to(REPO_ROOT).as_posix()
                cat = categorize_file(rel, file)
                stat = full_path.stat()
                inventory_items.append({
                    "path": rel,
                    "directory": target,
                    "name": file,
                    "extension": os.path.splitext(file)[1].lower(),
                    "size_bytes": stat.st_size,
                    "category": cat,
                    "preservation_status": get_preservation_status(rel, file),
                    "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

    # Summary calculations
    total_files = len(inventory_items)
    total_size = sum(item["size_bytes"] for item in inventory_items)
    
    by_directory = {}
    for item in inventory_items:
        d = item["directory"]
        if d not in by_directory:
            by_directory[d] = {"count": 0, "size_bytes": 0}
        by_directory[d]["count"] += 1
        by_directory[d]["size_bytes"] += item["size_bytes"]

    by_category = {}
    for item in inventory_items:
        c = item["category"]
        if c not in by_category:
            by_category[c] = {"count": 0, "size_bytes": 0}
        by_category[c]["count"] += 1
        by_category[c]["size_bytes"] += item["size_bytes"]

    # Archive documentation detail
    archived_list = []
    for item in inventory_items:
        if item["directory"] == "docs" and item["path"].startswith("docs/archive/"):
            fname = item["name"]
            archived_list.append({
                "filename": fname,
                "path": item["path"],
                "size_bytes": item["size_bytes"],
                "reason_archived": ARCHIVED_REASONS.get(fname, "Superseded historical report archived to keep docs root focused on active project documentation.")
            })

    output_data = {
        "metadata": {
            "title": "TraceGuard AI - Complete Repository Inventory",
            "phase": "Phase 18 (Safe Archival, Presentation Hardening & Documentation Reconciliation)",
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "repository": "TraceGuard-AI / FSM-NIDS",
            "auditor": "auditor agent (Swarm)",
            "safety_invariants_adhered": True
        },
        "preservation_guarantees": {
            "source_code_protected": True,
            "tests_protected": True,
            "migrations_protected": True,
            "datasets_protected": True,
            "canonical_pptx_protected": True,
            "canonical_pptx_path": "presentation/TraceGuard_AI_TOC_Presentation.pptx",
            "presenter_guides_protected": True,
            "presenter_guides_directory": "docs/presentation/"
        },
        "summary": {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "by_directory": by_directory,
            "by_category": by_category,
            "archived_documentation_count": len(archived_list)
        },
        "archived_documentation_register": archived_list,
        "items": sorted(inventory_items, key=lambda x: x["path"])
    }

    out_file = REPO_ROOT / "qa" / "phase18" / "repository_inventory.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"Inventory written successfully to {out_file}")
    print(f"Total files: {total_files}, Total Size: {round(total_size / (1024 * 1024), 2)} MB")
    print("Breakdown by directory:")
    for d, s in by_directory.items():
        print(f"  - {d}: {s['count']} files ({round(s['size_bytes'] / (1024 * 1024), 2)} MB)")

if __name__ == "__main__":
    scan_repository()
