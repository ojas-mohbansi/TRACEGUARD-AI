# TRACEGUARD AI — PHASE 16: ACADEMIC DEMONSTRATION & UNIVERSITY EVALUATION GUIDE

**Document ID:** `TG-DOC-P16-04`  
**Version:** `1.0.0`  
**Date:** `2026-11-17`  
**Target Audience:** `Faculty Evaluators, TOC Committee, Systems & Network Security Reviewers`  
**Project:** `TraceGuard AI`

---

## 1. Demonstration Overview & Academic Talking Points

TraceGuard AI is designed as a university capstone project bridging **Theory of Computation (Automata & Formal Languages)** and **Network Security Engineering (Machine Learning Intrusion Detection)**.

When presenting to evaluators, focus on these three core academic claims:
1. **Automata are Deterministic & Zero-Training:** A Finite State Machine evaluates protocol grammars in $O(1)$ per symbol and guarantees 100% precision on structural protocol violations (zero false alarms).
2. **Machine Learning Detects Volumetric Anomalies:** Isolation Forest excels at catching statistical outliers (e.g., credential stuffing loops, data exfiltration) where each individual packet may be syntactically valid.
3. **The Hybrid Consensus Engine Unifies Both:** The formula $S_h = 0.6 S_{FSM} + 0.4 S_{ML}$ with a 60% FSM risk floor ensures protocol violations are never ignored while elevating combined threats.

---

## 2. Step-by-Step Demonstration Script

### Step 1: Authentication & Navigation (1 Minute)
1. Open browser to `http://localhost:5174/login`.
2. Enter demonstration credentials:
   - **Username:** `demo`
   - **Password:** `traceguard2024`
3. Click **Sign In**.
4. Show that protected routes and session persistence operate cleanly.

---

### Step 2: Npcap Live Packet Capture Runtime (`/monitor`) (3 Minutes)
1. Navigate to **Live Monitor** (`/monitor`) in the sidebar.
2. Direct attention to the **Npcap Packet Capture Runtime** status card:
   - Point out the **`CAPTURE_READY`** badge in emerald green.
   - Show the **6-Step Diagnostic Checklist**:
     1. Driver Installed (`C:\Windows\System32\Npcap\wpcap.dll`)
     2. Service Running (`npcap` Windows kernel service)
     3. API Loaded (`Npcap 1.90 / libpcap 1.10.7`)
     4. Interfaces Enumerated (9 real hardware adapters detected)
     5. Handle Open Test (Passive promiscuous test passed)
     6. Ready
3. Click **"Re-check Diagnostic"**:
   - Demonstrate that the backend re-probes the Windows kernel service in real time and re-validates the capture handle without needing an application restart.
4. Interface Selection & Passive Capture:
   - Select the host **`Wi-Fi`** adapter (`Realtek 8852CE - 192.168.107.105`) or **`Loopback`**.
   - Click **"Start Live Capture"**.
   - Observe the live packet counter incrementing as real network packets arrive.
   - Click **"Stop Capture"**; point out the clean shutdown and zero-loss buffer flush.

---

### Step 3: Academic Showcase & The 4 Scenarios (`/detection`) (5 Minutes)
1. Navigate to **Detection Lab** (`/detection`) and click the **"Academic Showcase"** tab.
2. Explain the purpose of the 4 controlled scenarios:
   - They allow evaluators to isolate each engine and observe deterministic automaton behavior versus statistical ML behavior.

#### Scenario 1: Normal Legitimate Flow
- **Click "Run Scenario"** on Card 1.
- **Trace Analysis:**
  - Event sequence: `CONNECT → REQUEST → AUTH_SUCCESS → RESPONSE_200 → CLOSE`.
  - FSM Engine: Transitions cleanly through valid states ending in `CLOSED`. $S_{FSM} = 0$.
  - ML Engine: Benign payload and rates. $S_{ML} < 0.55$.
  - Result: No alert generated. System verdict is `NORMAL`.

#### Scenario 2: Deterministic FSM Protocol Violation Only
- **Click "Run Scenario"** on Card 2.
- **Trace Analysis:**
  - Sequence: `CONNECT → REQUEST → AUTH_SUCCESS → RESPONSE_200 → CLOSE → REQUEST`.
  - Explain to the professor: *"Notice that after the session closed, the client transmitted an out-of-order GET request. In the HTTP DFA, state CLOSED has no transition for REQUEST. The automaton drops immediately into the absorbing TRAP state."*
  - FSM Engine: `Violation Detected`, State = `TRAP`, $S_{FSM} = 100$.
  - ML Engine: Benign payloads and standard intervals $\implies$ `Normal`.
  - Hybrid Attribution: Attributed exclusively to **`Deterministic FSM Engine`**. 60% risk floor enforced ($S_h \ge 60\%$).

#### Scenario 3: Statistical Machine Learning Anomaly Only
- **Click "Run Scenario"** on Card 3.
- **Trace Analysis:**
  - Sequence: `CONNECT → [REQUEST → AUTH_FAILURE → RESPONSE_401] × 6 → CLOSE`.
  - Explain to the professor: *"Notice that every single transition here is syntactically valid in our DFA. The FSM accepts the string without error ($S_{FSM} = 0$). However, repeating 6 authentication failures represents a statistical credential stuffing attack. The Isolation Forest flags this statistical anomaly ($S_{ML} \ge 0.55$)."*
  - Result: Alert attributed exclusively to **`Statistical ML Engine`**.

#### Scenario 4: Dual-Engine Hybrid Consensus
- **Click "Run Scenario"** on Card 4.
- **Trace Analysis:**
  - Sequence combines a direct response without request (FSM violation into TRAP) plus a 9.2MB burst volume outlier.
  - Both engines flag the session.
  - Hybrid combined score: $S_h = 0.6 \times 100 + 0.4 \times S_{ML} \ge 80\%$.
  - Result: Classified as **`Dual-Engine Hybrid Consensus`**.

#### Reset Demonstration Data Action
- Click **"Reset Demonstration Data"** in the top-right header.
- Demonstrate that all demonstration alerts and events are safely purged without altering background production traffic.

---

### Step 4: Alert Engine Analytics Reconciliation (`/dashboard`) (2 Minutes)
1. Navigate to **Dashboard** (`/dashboard`).
2. Point out the **Alert Engine Analytics** section:
   - **Left Pane:** Final Alert Attribution donut chart showing the exact proportion of alerts generated by FSM, ML, and Hybrid. Explain that these sum strictly to total alerts.
   - **Right Pane:** Engine Contribution & Detection Activity cards showing raw evaluation and detection rates for each component.
   - Highlight the informational callout explaining why component detections overlap while attribution is mutually exclusive.

---

### Step 5: Threat Forensics & FSM Violation Proof (`/threats`) (2 Minutes)
1. Navigate to **Threat Triage & Forensics** (`/threats`).
2. Scroll to the **Deterministic FSM Protocol Violation Evidence** table.
3. Show the exact state transitions: `IDLE → CONNECTED → ... → TRAP`.
4. Click **"Inspect"** on an FSM violation alert:
   - Show the Forensic Drawer with event metadata, rule violation details, and academic citation.

---

## 3. Anticipated Faculty Questions & Academic Answers

**Q: Why use an FSM when modern NIDS use deep learning?**  
*A: Deep learning models are probabilistic black boxes subject to adversarial evasion and false positives. An FSM provides deterministic verification: if a client sends a 200 OK before a request, it is mathematically invalid. An FSM guarantees zero false alarms on syntactic violations and executes in $O(1)$ time without GPU hardware.*

**Q: Why is the FSM weight 0.6 and the floor 60%?**  
*A: Structural protocol violations represent hard boundary breaches (e.g., authentication bypasses, state smuggling). Even if an attacker shapes packet sizes and intervals to look statistically benign to an ML model, the 60% risk floor ensures that a deterministic protocol violation cannot be masked by statistical trickery.*
