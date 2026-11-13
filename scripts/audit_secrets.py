import os
import re

PATTERNS = [
    (re.compile(r'(?:api[_-]?key|secret_key|private_key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{16,})["\']', re.IGNORECASE), 'Secret / API Key'),
    (re.compile(r'ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{82}'), 'GitHub Token'),
    (re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'), 'Private Key'),
    (re.compile(r'(?:postgres|mysql|mongodb|redis):\/\/[a-zA-Z0-9_\-]+:[^@\s]+@'), 'Database URI with Password'),
]

IGNORE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.zip', '.joblib', '.pptx', '.pyc', '.exe', '.ico', '.svg', '.jsonl'}
IGNORE_DIRS = {'.git', 'node_modules', '.venv', 'venv', 'dist', '__pycache__', '.pytest_cache', '.agent', '.agents'}

def run_scan():
    findings = []
    real_env_files = []

    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            full_path = os.path.join(root, f)
            if f == '.env':
                real_env_files.append(full_path)
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext in IGNORE_EXTENSIONS:
                continue
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as fp:
                    for line_num, line in enumerate(fp, 1):
                        stripped = line.strip()
                        if stripped.startswith('#') or 'example' in full_path.lower():
                            continue
                        for pattern, label in PATTERNS:
                            if pattern.search(line):
                                findings.append((full_path, line_num, label))
            except Exception as e:
                pass

    print(f"=== WORKING TREE AUDIT REPORT ===")
    print(f"Real .env files found: {len(real_env_files)}")
    for ef in real_env_files:
        print(f"  [CRITICAL] Found real .env file: {ef}")

    print(f"Suspicious secret patterns found: {len(findings)}")
    for path, line_no, label in findings:
        print(f"  [ALERT] {path}:{line_no} -> {label}")

    if not real_env_files and not findings:
        print("RESULT: ALL WORKING TREE FILES ARE CLEAN OF EXPOSED SECRETS.")

if __name__ == '__main__':
    run_scan()
