# TRACEGUARD AI — PHASE 16: DETERMINISTIC FSM DETECTION PROOF & PROTOCOL VERIFICATION

**Document ID:** `TG-DOC-P16-02`  
**Version:** `1.0.0`  
**Date:** `2026-11-17`  
**Classification:** `Theory of Computation & Intrusion Detection Research Report`  
**Project:** `TraceGuard AI (Academic University TOC / NIDS Project)`

---

## 1. Executive Summary

In a Network Intrusion Detection System (NIDS), protocol parsing and syntactic compliance are traditionally relegated to ad-hoc regexes or generic statistical models. TraceGuard AI is grounded in the **Theory of Computation (TOC)**: it demonstrates that a **Deterministic Finite Automaton (DFA)** provides an exact, mathematically provable mechanism for detecting protocol violations with **zero false positives**, requiring zero training data, and operating with $O(1)$ state lookup complexity per event.

Prior to Phase 16, Threat Analytics reported approximately **85% Hybrid, 5% ML, and 0% FSM**, suggesting that the FSM was incapable of independently flagging intrusions. Workstream B identified the flaw in the classification thresholding logic, restored independent FSM detection recording (`engine="fsm"`), and provided rigorous mathematical and empirical proof of independent FSM detection.

---

## 2. Formal Automaton Definition ($M_{HTTP}$)

The HTTP protocol validator is formalized as a 5-tuple complete deterministic finite automaton:

$$M_{HTTP} = \langle Q, \Sigma, \delta, q_0, F \rangle$$

### 2.1 State Set ($Q$) — $|Q| = 9$
$$Q = \{ \text{IDLE}, \text{CONNECTED}, \text{REQUEST\_RECEIVED}, \text{AUTH\_CHECKED}, \text{AUTH\_FAILED}, \text{RESPONSE\_SENT}, \text{ERROR}, \text{CLOSED}, \text{TRAP} \}$$
- Operational States: 8 states
- Trap / Dead State: $\text{TRAP}$ (absorbing sink state enforcing total function completeness)

### 2.2 Alphabet ($\Sigma$) — $|\Sigma| = 13$
$$\Sigma = \{ \text{CONNECT}, \text{REQUEST}, \text{AUTH\_SUCCESS}, \text{AUTH\_FAILURE}, \text{RESPONSE\_200}, \text{RESPONSE\_301}, \text{RESPONSE\_401}, \text{RESPONSE\_403}, \text{RESPONSE\_500}, \text{CLOSE}, \text{TIMEOUT}, \text{MALFORMED}, \text{ERROR\_RESPONSE} \}$$

### 2.3 Initial State & Final States
- **Initial State:** $q_0 = \text{IDLE}$
- **Accepting / Final State Set:** $F = \{ \text{CLOSED} \}$

### 2.4 Transition Function Completeness ($\delta$)
To satisfy the formal definition of a DFA, $\delta$ must be a total function mapping every pair $(q, \sigma) \in Q \times \Sigma$ to a state $q' \in Q$:
$$|\delta| = |Q| \times |\Sigma| = 9 \times 13 = 117 \text{ transitions}$$

Any transition not defined in the valid operational protocol grammar transitions strictly to the absorbing state $\text{TRAP}$:
$$\forall \sigma \in \Sigma, \quad \delta(\text{TRAP}, \sigma) = \text{TRAP}$$

---

## 3. Root Cause: Why FSM Stood at 0% in Threat Analytics

Investigation into the detection pipeline revealed the root cause behind the 0% FSM detection rate:

```
+-----------------------------------------------------------------------------------------+
|                                    PRIOR FLAWED LOGIC                                   |
|                                                                                         |
|  1. Isolation Forest raw scores in sklearn center around ~0.50 for benign sessions.     |
|  2. In generator.py & pipeline.py:                                                      |
|        ml_anom = bool(res.get("ml_anomaly_score", 0) > 0.5 or ...)                      |
|  3. Attribution condition:                                                              |
|        if fsm_violation and ml_anom:                                                    |
|            engine = "hybrid"                                                            |
|  4. Consequence: 100% of FSM violations had ml_anomaly_score ~0.501, classifying every   |
|     single protocol violation as "hybrid". FSM alerts remained permanently at 0%!       |
+-----------------------------------------------------------------------------------------+
```

### 3.1 The Remediation
The engine attribution condition was corrected across `backend/app/detection/hybrid/engine.py`, `backend/app/network/pipeline.py`, and `backend/app/simulator/generator.py`:

```python
# Authoritative attribution logic:
ml_anomalous = bool(ml_result and (ml_result.get("prediction") == "anomalous" or ml_anomaly_score >= 0.55))

if fsm_violation and ml_anomalous:
    attribution = "hybrid"
elif fsm_violation:
    attribution = "fsm"        # Protocol violation with normal statistical profile!
elif ml_anomalous:
    attribution = "ml"         # Conforming sequence with statistical volume anomaly!
else:
    attribution = "none"
```

---

## 4. Empirical Proof of Independent FSM Detection

### 4.1 Test Scenario: Post-Close Request Violation
A client establishes a session, performs authentication, completes an HTTP transaction, closes the session, and then transmits a subsequent HTTP GET request:
$$\text{IDLE} \xrightarrow{\text{CONNECT}} \text{CONNECTED} \xrightarrow{\text{REQUEST}} \text{REQUEST\_RECEIVED} \xrightarrow{\text{AUTH\_SUCCESS}} \text{AUTH\_CHECKED} \xrightarrow{\text{RESPONSE\_200}} \text{RESPONSE\_SENT} \xrightarrow{\text{CLOSE}} \text{CLOSED} \xrightarrow{\text{REQUEST}} \mathbf{TRAP}$$

#### Evaluation Results:
1. **FSM Engine ($S_{FSM}$):** Transition $(\text{CLOSED}, \text{REQUEST})$ is illegal. Machine transitions directly to $\text{TRAP}$. `fsm_violation = True`, $S_{FSM} = 100$.
2. **ML Engine ($S_{ML}$):** Payload sizes (64B, 320B, 128B, 1450B, 64B, 380B) and inter-arrival intervals are benign. Isolation Forest output: `prediction = "normal"`, `ml_anomaly_score = 0.38 < 0.55`.
3. **Hybrid Engine Combined Score:**
   $$S_h = \max(0.6 \times 100 + 0.4 \times 38, 60.0\%) = \max(75.2\%, 60.0\%) = 75\%$$
4. **Final Engine Attribution:** **`engine = "fsm"`** (Deterministic FSM Engine).

### 4.2 Mathematical Invariants Verified
1. **Determinism:** For every sequence $w \in \Sigma^*$, the state sequence is unique and repeatable:
   $$\forall w, \quad |\hat{\delta}(q_0, w)| = 1$$
2. **Sink State Trap-Door:** Once $\text{TRAP}$ is reached, no sequence of input symbols can leave $\text{TRAP}$:
   $$\forall w \in \Sigma^*, \quad \hat{\delta}(\text{TRAP}, w) = \text{TRAP}$$
3. **The 60% FSM Risk Floor:** Every sequence exhibiting an FSM violation guarantees $S_h \ge 60\%$, ensuring that no protocol violation is ever downgraded to low severity by an ambiguous statistical model.

---

## 5. Threat Triage & Forensic Integration

In `frontend/src/pages/Threats.jsx`, a dedicated **Deterministic FSM Protocol Violation Evidence** table renders real-time violation artifacts:

- **Source Type:** Marked as `Deterministic FSM Engine` with an indigo badge.
- **Rule Violated:** e.g., `Illegal transition from CLOSED on event REQUEST (HTTP DFA Rule #14)`.
- **State Path:** Interactive badge trail: `IDLE → CONNECTED → REQUEST_RECEIVED → AUTH_CHECKED → RESPONSE_SENT → CLOSED → TRAP`.
- **Forensic Drawer:** Clicking "Inspect" displays the exact timestamp, event ID, protocol method, responsible byte payload, and academic proof citation.

---

## 6. Verification Summary

- **Unit & Integration Suite (`test_phase16_diagnostics_and_proof.py`):**
  - `test_valid_dfa_sequence_acceptance_and_incomplete_prefix`: PASSED
  - `test_invalid_dfa_transition_reaches_trap_state`: PASSED
  - `test_fsm_only_protocol_violation_attribution`: PASSED
  - `test_component_findings_retain_accurate_provenance`: PASSED
- **Adversarial Regression (`test_adversarial_probes_56.py`):** All 56 formal automaton probes and trap tests PASSED.
