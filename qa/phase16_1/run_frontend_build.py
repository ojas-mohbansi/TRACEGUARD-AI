import subprocess
import sys
import os

def main():
    frontend_dir = os.path.abspath("frontend")
    cmd = ["npm.cmd", "run", "build"]
    print(f"Running command: {' '.join(cmd)} in {frontend_dir}")
    
    proc = subprocess.run(cmd, cwd=frontend_dir, capture_output=True, text=True)
    
    out_file = os.path.abspath("qa/phase16_1/frontend_build.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("=== FRONTEND PRODUCTION BUILD AUDIT ===\n")
        f.write(f"Directory: {frontend_dir}\n")
        f.write(f"Command: {' '.join(cmd)}\n")
        f.write(f"Exit Code: {proc.returncode}\n\n")
        f.write("=== STDOUT ===\n")
        f.write(proc.stdout)
        f.write("\n=== STDERR ===\n")
        f.write(proc.stderr)
        f.write("\n=== ARTIFACT VERIFICATION (dist/) ===\n")
        dist_dir = os.path.join(frontend_dir, "dist")
        if os.path.exists(dist_dir):
            for root, dirs, files in os.walk(dist_dir):
                for file in files:
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, dist_dir)
                    size = os.path.getsize(full_p)
                    f.write(f"{rel_p} ({size:,} bytes)\n")
        else:
            f.write("dist/ directory DOES NOT EXIST!\n")

    print(f"Exit Code: {proc.returncode}")
    print(proc.stdout)
    if proc.stderr:
        print("STDERR:", proc.stderr)
    if proc.returncode != 0:
        sys.exit(proc.returncode)

if __name__ == "__main__":
    main()
