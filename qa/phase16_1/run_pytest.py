import subprocess
import sys
import os

def main():
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath("backend")
    
    cmd = [sys.executable, "-m", "pytest", "backend/tests", "-v"]
    print("Running:", " ".join(cmd))
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    
    with open("qa/phase16_1/pytest_full_run.txt", "w", encoding="utf-8") as f:
        f.write(res.stdout)
        if res.stderr:
            f.write("\n=== STDERR ===\n")
            f.write(res.stderr)
            
    print("Exit code:", res.returncode)
    # Print the summary lines
    lines = res.stdout.splitlines()
    summary_lines = [l for l in lines if "=" in l and ("passed" in l or "failed" in l or "error" in l)]
    for l in summary_lines:
        print(l)

if __name__ == "__main__":
    main()
