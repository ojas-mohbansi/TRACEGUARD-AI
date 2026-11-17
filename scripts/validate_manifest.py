#!/usr/bin/env python3
"""
TraceGuard AI — Phase 21 Manifest & Presenter Mapping Validator
Validates frontend/src/data/presentationManifest.json and qa/phase21/presentation_manifest.json
"""

import json
from pathlib import Path

REQUIRED_FIELDS = [
    "slideNumber", "title", "presenterId", "presenterName",
    "presenterStartSlide", "presenterEndSlide", "spokenScript",
    "slideNotes", "keyPoints", "defenseQuestions", "estimatedDuration"
]

EXPECTED_MAPPING = {
    1: ("P1", "Tanmay", 1, 4),
    2: ("P1", "Tanmay", 1, 4),
    3: ("P1", "Tanmay", 1, 4),
    4: ("P1", "Tanmay", 1, 4),
    5: ("P2", "Karthik Sai", 5, 9),
    6: ("P2", "Karthik Sai", 5, 9),
    7: ("P2", "Karthik Sai", 5, 9),
    8: ("P2", "Karthik Sai", 5, 9),
    9: ("P2", "Karthik Sai", 5, 9),
    10: ("P3", "Ojas Mohbansi", 10, 14),
    11: ("P3", "Ojas Mohbansi", 10, 14),
    12: ("P3", "Ojas Mohbansi", 10, 14),
    13: ("P3", "Ojas Mohbansi", 10, 14),
    14: ("P3", "Ojas Mohbansi", 10, 14),
    15: ("P4", "Darpan Jain", 15, 18),
    16: ("P4", "Darpan Jain", 15, 18),
    17: ("P4", "Darpan Jain", 15, 18),
    18: ("P4", "Darpan Jain", 15, 18),
    19: ("P5", "Panda", 19, 22),
    20: ("P5", "Panda", 19, 22),
    21: ("P5", "Panda", 19, 22),
    22: ("P5", "Panda", 19, 22),
}

frontend_path = Path("frontend/src/data/presentationManifest.json")
qa_path = Path("qa/phase21/presentation_manifest.json")

report = {
    "validationTimestamp": "2026-11-18T02:05:00Z",
    "filesChecked": [str(frontend_path), str(qa_path)],
    "manifestEquality": False,
    "slideCount": 0,
    "errors": [],
    "warnings": [],
    "presenterMappingChecks": [],
    "boundaryTransitions": []
}

# 1. Read files
with open(frontend_path, "r", encoding="utf-8") as f:
    fe_data = json.load(f)

with open(qa_path, "r", encoding="utf-8") as f:
    qa_data = json.load(f)

if fe_data == qa_data:
    report["manifestEquality"] = True
else:
    report["errors"].append("Frontend and QA manifests do not match.")

slides = fe_data.get("slides", [])
report["slideCount"] = len(slides)

if len(slides) != 22:
    report["errors"].append(f"Expected 22 slides, found {len(slides)}")

# 2. Inspect each slide
for s in slides:
    s_num = s.get("slideNumber")
    if s_num not in EXPECTED_MAPPING:
        report["errors"].append(f"Unexpected slide number: {s_num}")
        continue
    
    exp_pid, exp_name, exp_start, exp_end = EXPECTED_MAPPING[s_num]
    
    # Check fields
    for field in REQUIRED_FIELDS:
        val = s.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            report["errors"].append(f"Slide {s_num} missing required field '{field}'")
            
    # Check presenter mapping
    act_pid = s.get("presenterId")
    act_name = s.get("presenterName")
    act_start = s.get("presenterStartSlide")
    act_end = s.get("presenterEndSlide")
    
    mapping_ok = (act_pid == exp_pid and act_name == exp_name and act_start == exp_start and act_end == exp_end)
    if not mapping_ok:
        report["errors"].append(f"Slide {s_num} presenter mismatch: expected {exp_name} ({exp_pid}), got {act_name} ({act_pid})")
        
    report["presenterMappingChecks"].append({
        "slide": s_num,
        "title": s.get("title"),
        "expectedPresenter": f"{exp_name} ({exp_pid}) [{exp_start}..{exp_end}]",
        "actualPresenter": f"{act_name} ({act_pid}) [{act_start}..{act_end}]",
        "valid": mapping_ok
    })

# 3. Check boundaries
boundaries = [(4, 5), (9, 10), (14, 15), (18, 19)]
for s1, s2 in boundaries:
    slide1 = slides[s1 - 1]
    slide2 = slides[s2 - 1]
    p1 = slide1.get("presenterName")
    p2 = slide2.get("presenterName")
    changed = (p1 != p2)
    report["boundaryTransitions"].append({
        "fromSlide": s1,
        "fromPresenter": p1,
        "toSlide": s2,
        "toPresenter": p2,
        "changedCorrectly": changed
    })
    if not changed:
        report["errors"].append(f"Boundary transition failed between Slide {s1} and {s2}: presenter did not change from {p1}")

report["status"] = "PASSED" if not report["errors"] else "FAILED"

with open("qa/phase21/manifest_validation.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

print(f"Validation completed: Status = {report['status']} (Errors: {len(report['errors'])})")
