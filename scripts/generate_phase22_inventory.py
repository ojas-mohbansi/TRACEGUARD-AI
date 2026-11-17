#!/usr/bin/env python3
"""
TraceGuard AI — Phase 22 Repository Inventory & Minimization Analyzer
Crawls C:\Projects\FSM-NIDS, catalogues every file and directory,
computes metrics, detects duplicates, identifies generated/temp files,
and produces qa/phase22/repository_inventory.json and qa/phase22/repository_inventory.md
"""

import os
import sys
import json
import hashlib
import subprocess
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path("C:/Projects/FSM-NIDS").resolve()
OUT_JSON = REPO_ROOT / "qa/phase22/repository_inventory.json"
OUT_MD = REPO_ROOT / "qa/phase22/repository_inventory.md"

OUT_JSON.parent.mkdir(parents=True, exist_ok=True)

# 1. Fetch Git file states
def get_git_file_sets():
    try:
        tracked_out = subprocess.check_output(["git", "ls-files"], cwd=REPO_ROOT).decode("utf-8", errors="replace")
        tracked = set(os.path.normpath(line.strip()) for line in tracked_out.splitlines() if line.strip())
    except Exception:
        tracked = set()

    try:
        untracked_out = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=REPO_ROOT).decode("utf-8", errors="replace")
        untracked = set(os.path.normpath(line.strip()) for line in untracked_out.splitlines() if line.strip())
    except Exception:
        untracked = set()

    try:
        ignored_out = subprocess.check_output(["git", "ls-files", "--others", "-i", "--exclude-standard"], cwd=REPO_ROOT).decode("utf-8", errors="replace")
        ignored = set(os.path.normpath(line.strip()) for line in ignored_out.splitlines() if line.strip())
    except Exception:
        ignored = set()

    return tracked, untracked, ignored

print("Fetching Git file tracking status...")
tracked_files, untracked_files, ignored_files = get_git_file_sets()

# Helper for file hashing
def compute_hash(filepath, max_size=20*1024*1024):
    try:
        size = os.path.getsize(filepath)
        if size > max_size:
            return f"skipped_large_{size}"
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return f"error_{e}"

# Helper for subsystem ownership
def determine_subsystem(rel_path):
    parts = Path(rel_path).parts
    if not parts:
        return "root"
    first = parts[0]
    if first in ("backend", "frontend", "website", "docs", "presentation", "brand", "qa", "scripts"):
        return first
    if first.startswith("."):
        return "config_hidden"
    return "root"

# Helper for generated/temporary classification
def classify_file(rel_path, filename, size, ext):
    norm = os.path.normpath(rel_path).replace("\\", "/")
    
    # OS / Editor clutter
    if filename in ("Thumbs.db", ".DS_Store", "desktop.ini"):
        return "SAFE_REMOVE", "OS metadata file", True, True
    if filename.endswith(".swp") or filename.endswith("~") or filename.endswith(".tmp"):
        return "SAFE_REMOVE", "Editor temporary file", True, True
        
    # Python caches
    if "__pycache__" in norm or ext == ".pyc":
        return "SAFE_REMOVE", "Python compiled bytecode", True, True
    if ".pytest_cache" in norm:
        return "SAFE_REMOVE", "Pytest cache artifact", True, True
        
    # Scratch inspection dumps in scripts/
    if norm in (
        "scripts/editorial_slides_dump.json",
        "scripts/editorial_slides_dump_full.json",
        "scripts/inspect_editorial_deck.py",
        "scripts/inspect_full_deck.py",
        "scripts/inspect_diagram_slides.py",
        "scripts/print_presenter_slides.py",
        "scripts/dump_slide_details.py",
        "scripts/test_git_files.py"
    ):
        return "SAFE_REMOVE", "Temporary slide inspection scratch script/dump", False, True

    # Node modules & build artifacts (Ignored reproducible)
    if "node_modules" in norm:
        return "KEEP_DEV_MAINTENANCE", "Node package dependency (active dev)", False, False
    if norm.startswith("website/dist") or norm.startswith("frontend/dist") or "/dist/" in norm:
        return "KEEP_DEV_MAINTENANCE", "Build output artifact (reproducible)", False, False
    if ".wrangler" in norm or ".vite" in norm:
        return "KEEP_DEV_MAINTENANCE", "Runtime dev server cache", False, False

    # Historical phase documents in docs/ (not in archive/)
    if norm.startswith("docs/") and not norm.startswith("docs/archive/") and not norm.startswith("docs/presentation/"):
        if filename in (
            "PHASE17_BENCHMARK_METHODOLOGY.md", "PHASE17_ENGINE_ANALYTICS.md",
            "PHASE17_FINAL_REPORT.md", "PHASE17_FSM_DETECTION_ANALYSIS.md",
            "PHASE17_LOCAL_ACADEMIC_MODE.md", "PHASE18_FINAL_REPORT.md",
            "PHASE19_2_FINAL_REPORT.md", "PHASE19_FINAL_REPORT.md",
            "PHASE20_FINAL_REPORT.md", "PHASE21_FINAL_REPORT.md",
            "PHASE5_AUDIT.md", "PHASE7_FINAL_AUDIT.md", "PHASE_9_FINAL_QA_REPORT.md",
            "UI_REDESIGN_REPORT.md"
        ):
            return "CONSOLIDATE_ARCHIVE", "Historical phase audit report (move to docs/archive/)", False, False

    # Old presentation versions in presentation/
    if norm == "presentation/TraceGuard_AI_TOC_Presentation.pptx":
        return "KEEP_DEV_MAINTENANCE", "Preserved legacy 14-slide prototype deck (reference)", False, False
    if norm == "presentation/TraceGuard AI — Editorial Theory of Computation Deck.pptx":
        return "KEEP_ESSENTIAL", "Authoritative 22-slide Theory of Computation deck", False, False

    # Core source files
    if norm.startswith("backend/app/") or norm.startswith("backend/tests/"):
        return "KEEP_ESSENTIAL", "Backend core application / test suite", False, False
    if norm.startswith("frontend/src/") or norm.startswith("website/src/"):
        return "KEEP_ESSENTIAL", "Frontend / Website source code", False, False
    if norm.startswith("docs/presentation/"):
        return "KEEP_ESSENTIAL", "Authoritative Phase 21 presenter speaking guides", False, False
    if norm.startswith("brand/"):
        return "KEEP_ESSENTIAL", "Official vector and PNG brand identity assets", False, False
    if norm.startswith("frontend/public/slides/"):
        return "KEEP_ESSENTIAL", "Authoritative 1920x1080 slide images for Presentation Mode", False, False

    # QA directories
    if norm.startswith("qa/"):
        if norm.startswith("qa/phase21/") or norm.startswith("qa/phase22/"):
            return "KEEP_ESSENTIAL", "Current phase verification evidence and audit manifests", False, False
        if norm.startswith("qa/phase20/"):
            return "KEEP_DEV_MAINTENANCE", "Phase 20 visual & Cloudflare release evidence", False, False
        return "CONSOLIDATE_ARCHIVE", "Historical phase QA screenshots / reports", False, False

    # Standard configs
    if filename in ("package.json", "bun.lock", "tsconfig.json", "vite.config.ts", "vite.config.js",
                    "wrangler.jsonc", "requirements.txt", "pyproject.toml", ".gitignore", "README.md",
                    "Dockerfile", "docker-compose.yml", ".env.example"):
        return "KEEP_ESSENTIAL", "Root project / deployment configuration", False, False

    return "KEEP_ESSENTIAL", "Active project file", False, False

print("Scanning all directories and cataloguing files...")
all_files = []
all_dirs = []
empty_dirs = []
dir_sizes = defaultdict(int)
dir_file_counts = defaultdict(int)
hash_to_files = defaultdict(list)

# Walk directory tree
for root, dirs, files in os.walk(REPO_ROOT):
    # Avoid descending into .git objects to keep scan fast
    norm_root = os.path.normpath(root)
    rel_root = os.path.relpath(norm_root, REPO_ROOT)
    
    if ".git" in Path(rel_root).parts:
        continue
        
    all_dirs.append(rel_root)
    if not dirs and not files and rel_root != ".":
        empty_dirs.append(rel_root)

    for f in files:
        full_path = os.path.join(root, f)
        rel_path = os.path.normpath(os.path.relpath(full_path, REPO_ROOT))
        
        try:
            stat = os.stat(full_path)
            size = stat.st_size
        except Exception:
            size = 0
            
        ext = os.path.splitext(f)[1].lower()
        subsystem = determine_subsystem(rel_path)
        
        # Git tracking status
        if rel_path in tracked_files:
            git_status = "tracked"
        elif rel_path in untracked_files:
            git_status = "untracked"
        elif rel_path in ignored_files or "node_modules" in rel_path or "dist" in rel_path or ".pytest_cache" in rel_path:
            git_status = "ignored"
        else:
            git_status = "untracked"
            
        disposition, reason, is_temp, is_safe_remove = classify_file(rel_path, f, size, ext)
        
        # Hash for duplicate detection (skip node_modules to keep fast)
        file_hash = None
        if "node_modules" not in rel_path and ".git" not in rel_path and size > 0:
            file_hash = compute_hash(full_path)
            if not file_hash.startswith("skipped") and not file_hash.startswith("error"):
                hash_to_files[file_hash].append({"path": rel_path, "size": size})

        file_entry = {
            "path": rel_path.replace("\\", "/"),
            "filename": f,
            "extension": ext,
            "sizeBytes": size,
            "gitStatus": git_status,
            "subsystem": subsystem,
            "disposition": disposition,
            "reason": reason,
            "isTemporary": is_temp,
            "isSafeRemove": is_safe_remove,
            "hash": file_hash
        }
        all_files.append(file_entry)
        
        # Aggregate directory sizes
        cur_dir = rel_root.replace("\\", "/")
        dir_sizes[cur_dir] += size
        dir_file_counts[cur_dir] += 1

# Identify duplicates
duplicates_list = []
for h, f_list in hash_to_files.items():
    if len(f_list) > 1:
        # Verify sizes are identical
        duplicates_list.append({
            "hash": h,
            "sizeBytes": f_list[0]["size"],
            "count": len(f_list),
            "files": [x["path"] for x in f_list]
        })

duplicates_list.sort(key=lambda x: x["sizeBytes"] * x["count"], reverse=True)

# Sort largest files
largest_files = sorted(all_files, key=lambda x: x["sizeBytes"], reverse=True)[:50]

# Sort largest directories
largest_dirs = sorted([{"directory": d, "sizeBytes": dir_sizes[d], "fileCount": dir_file_counts[d]} for d in dir_sizes],
                      key=lambda x: x["sizeBytes"], reverse=True)[:30]

total_repo_size = sum(f["sizeBytes"] for f in all_files)
tracked_count = sum(1 for f in all_files if f["gitStatus"] == "tracked")
untracked_count = sum(1 for f in all_files if f["gitStatus"] == "untracked")
ignored_count = sum(1 for f in all_files if f["gitStatus"] == "ignored")

safe_remove_candidates = [f for f in all_files if f["disposition"] == "SAFE_REMOVE"]
archive_candidates = [f for f in all_files if f["disposition"] == "CONSOLIDATE_ARCHIVE"]

inventory_summary = {
    "generatedAt": "2026-11-18T02:15:00Z",
    "totalFiles": len(all_files),
    "totalDirectories": len(all_dirs),
    "emptyDirectoriesCount": len(empty_dirs),
    "emptyDirectories": empty_dirs,
    "totalRepositorySizeBytes": total_repo_size,
    "totalRepositorySizeMB": round(total_repo_size / (1024 * 1024), 2),
    "trackedFilesCount": tracked_count,
    "untrackedFilesCount": untracked_count,
    "ignoredFilesCount": ignored_count,
    "duplicateGroupsCount": len(duplicates_list),
    "duplicateCandidates": duplicates_list[:25],
    "safeRemoveCandidatesCount": len(safe_remove_candidates),
    "archiveCandidatesCount": len(archive_candidates),
    "largestFiles": largest_files,
    "largestDirectories": largest_dirs
}

print(f"Total files catalogued: {len(all_files)}")
print(f"Total repository size: {inventory_summary['totalRepositorySizeMB']} MB")
print(f"Duplicate groups found: {len(duplicates_list)}")
print(f"Safe removal candidates: {len(safe_remove_candidates)}")
print(f"Archive candidates: {len(archive_candidates)}")

# Write JSON
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump({"summary": inventory_summary, "files": all_files}, f, indent=2, ensure_ascii=False)
print(f"Saved JSON inventory to {OUT_JSON}")

# Write Markdown report
with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("# TraceGuard AI — Phase 22 Complete Repository Inventory\n\n")
    f.write("## 1. High-Level Repository Metrics\n\n")
    f.write(f"- **Total Files Catalogued**: {len(all_files):,}\n")
    f.write(f"- **Total Directories**: {len(all_dirs):,}\n")
    f.write(f"- **Total Repository Size**: {inventory_summary['totalRepositorySizeMB']:,} MB ({total_repo_size:,} bytes)\n")
    f.write(f"- **Tracked Files in Git**: {tracked_count:,}\n")
    f.write(f"- **Untracked Files**: {untracked_count:,}\n")
    f.write(f"- **Ignored / Build Files**: {ignored_count:,}\n")
    f.write(f"- **Empty Directories**: {len(empty_dirs)}\n")
    f.write(f"- **Duplicate Content Groups**: {len(duplicates_list)}\n")
    f.write(f"- **Safe Removal Candidates (Category D)**: {len(safe_remove_candidates)}\n")
    f.write(f"- **Consolidate & Archive Candidates (Category C)**: {len(archive_candidates)}\n\n")

    f.write("## 2. Largest 30 Directories\n\n")
    f.write("| # | Directory | Size (MB) | File Count |\n| :---: | :--- | :---: | :---: |\n")
    for i, d in enumerate(largest_dirs, 1):
        mb = round(d["sizeBytes"] / (1024 * 1024), 2)
        f.write(f"| {i} | `{d['directory']}` | {mb} MB | {d['fileCount']} |\n")
    f.write("\n")

    f.write("## 3. Largest 50 Files\n\n")
    f.write("| # | Relative Path | Size (KB) | Subsystem | Git Status | Disposition |\n| :---: | :--- | :---: | :--- | :---: | :--- |\n")
    for i, file_obj in enumerate(largest_files, 1):
        kb = round(file_obj["sizeBytes"] / 1024, 1)
        f.write(f"| {i} | `{file_obj['path']}` | {kb:,} KB | `{file_obj['subsystem']}` | `{file_obj['gitStatus']}` | `{file_obj['disposition']}` |\n")
    f.write("\n")

    f.write("## 4. Notable Content Duplicates (Identical SHA-256)\n\n")
    f.write("| Hash (Prefix) | Size (Bytes) | Count | Duplicate File Paths |\n| :--- | :---: | :---: | :--- |\n")
    for dup in duplicates_list[:15]:
        paths = "<br>".join([f"`{p}`" for p in dup["files"]])
        f.write(f"| `{dup['hash'][:12]}` | {dup['sizeBytes']:,} | {dup['count']} | {paths} |\n")
    f.write("\n")

    f.write("## 5. Candidate Disposition Classifications\n\n")
    f.write("### Category D: Safe Removal Candidates\n")
    for c in safe_remove_candidates:
        f.write(f"- `{c['path']}` ({round(c['sizeBytes']/1024, 1)} KB): {c['reason']}\n")
    f.write("\n")

    f.write("### Category C: Consolidate & Archive Candidates\n")
    for a in archive_candidates:
        f.write(f"- `{a['path']}` ({round(a['sizeBytes']/1024, 1)} KB): {a['reason']}\n")
    f.write("\n")

print(f"Saved Markdown inventory to {OUT_MD}")
