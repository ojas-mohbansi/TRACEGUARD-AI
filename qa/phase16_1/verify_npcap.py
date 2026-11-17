import os
import sys
import json

sys.path.insert(0, os.path.abspath("backend"))

from app.network.npcap_diagnostics import NpcapDiagnostics

def main():
    diag = NpcapDiagnostics.run_diagnostics()
    print("=== LIVE NPCAP DIAGNOSTICS RESULT ===")
    print(json.dumps(diag, indent=2))
    
    with open("qa/phase16_1/npcap_audit.json", "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)

if __name__ == "__main__":
    main()
