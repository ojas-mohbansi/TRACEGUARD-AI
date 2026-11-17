# TraceGuard AI — Final University Submission Manifest

**Submission Archive Path:** `submission/TraceGuard_AI_Submission.zip`  
**Packaging Date:** November 2026  
**Archive Size:** 32,956,020 bytes (~31.4 MB)  
**Compression Algorithm:** Deflated (Level 9)  
**Total File Count:** 248 verified files  
**Top-Level Directory Root:** Exactly 1 directory: `TraceGuard_AI/`  

---

## 1. Directory Structure Overview (Inside Archive)

```
TraceGuard_AI/
├── backend/                  # 91 files: FastAPI service, FSM & ML engines, Alembic, tests
├── frontend/                 # 54 files: React 19 SPA, Tailwind CSS, components, assets
├── docs/                     # 34 files: Academic TOC theory proofs, viva prep, audit reports
├── qa/                       # 26 files: Visual QA verification screenshots matrix
├── brand/                    # 23 files: Official SVG brand book, vector logos, mockups
├── datasets/                 # 4 files: Benchmark CSV packet captures and generators
├── scripts/                  # 2 files: Dataset synthesis and secret auditing utilities
├── submission/               # 2 files: Submission README & verification documentation
├── presentation/             # 1 file: University defense PowerPoint presentation (14 slides)
├── models/                   # 1 file: Serialized Isolation Forest model weights (.joblib)
├── .dockerignore             # Production Docker container exclusion rules
├── .env.example              # Sanitized environment variable configuration template
├── alembic.ini               # Database migration configuration
├── docker-compose.yml        # Multi-container local execution manifest
├── Dockerfile                # Production multi-stage Docker build file
├── LICENSE                   # Open-source MIT licensing terms
├── migrate_db.py             # Database bootstrap and schema sync script
└── README.md                 # Primary project overview, architecture & setup guide
```

---

## 2. Excluded Non-Submission Content

To ensure maximum hygiene, academic compliance, and security, the following directories and artifacts were strictly filtered out during archive compilation:

1. **Version Control**: `.git/` directory, commit history, and git hooks.
2. **Dependencies & Environments**: `node_modules/`, `frontend/node_modules/`, `.venv/`, `venv/`.
3. **Local Databases & Telemetry**: `backend/traceguard.db`, `*.sqlite3`, local upload blobs.
4. **Build Caches & Bytecode**: `frontend/dist/`, `__pycache__/`, `*.pyc`, `*.pyo`, `.pytest_cache/`.
5. **Real Secrets**: `.env`, `.env.production`, `.env.local` (only `.env.example` included).
6. **Toolchain Scratch Directories**: `brand/.agents/`, `brand/skills/`, `.freebuff/`, `*.bak`.

---

## 3. Independent Extraction & Integrity Verification

The regenerated archive was extracted to a clean temporary operating system directory (`%TEMP%\tg_extract__*`) and validated:

1. **Top-Level Constraint Check**:
   - Exactly one top-level directory: `TraceGuard_AI/` — **CONFIRMED**.
   - Zero root-level loose files polluting the extraction root — **CONFIRMED**.
2. **File Integrity & CRC Check**:
   - `zipfile.testzip()` returned `None` (0 corrupted files or bad CRCs).
3. **Automata & FSM Test Execution from Clean Extraction**:
   - Executed `pytest` directly on the extracted backend source tree:
     ```text
     ..............                                                           [100%]
     14 passed, 9 warnings in 3.17s
     ```
   - Confirms that the extracted package is completely self-contained, reproducible, and runnable without host repo coupling.

---

## 4. Key Academic & Defense Assets Included

- **Presentation Slide Deck**: `TraceGuard_AI/presentation/TraceGuard_AI_TOC_Presentation.pptx` (76.4 kB, 14 professional slides with speaker notes).
- **Formal Theory Proofs**:
  - `TraceGuard_AI/docs/FORMAL_AUTOMATON.md` (Complete 5-tuple specification).
  - `TraceGuard_AI/docs/TRANSITION_TABLE.md` (117-cell deterministic matrix).
  - `TraceGuard_AI/docs/TOC_THEORY.md` (Regular languages & Chomsky hierarchy).
  - `TraceGuard_AI/docs/VIVA_PREPARATION.md` (60 defense questions and mathematical derivations).
- **Verification Evidence**:
  - `TraceGuard_AI/qa/screenshots/` (26 headless browser captures validating all 11 routes across 6 viewports).
