import subprocess
import sys

def main():
    cmd = [sys.executable, "-m", "pytest", "backend/tests", "--collect-only", "-q"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    lines = [line.strip() for line in proc.stdout.splitlines() if "::" in line]
    
    file_counts = {}
    for line in lines:
        filename = line.split("::")[0].replace("\\", "/")
        file_counts[filename] = file_counts.get(filename, 0) + 1
        
    print("=== TEST COLLECTION SUMMARY ===")
    total = 0
    for filename, count in sorted(file_counts.items()):
        print(f"{filename}: {count}")
        total += count
    print(f"TOTAL COLLECTED TESTS: {total}")

if __name__ == "__main__":
    main()
