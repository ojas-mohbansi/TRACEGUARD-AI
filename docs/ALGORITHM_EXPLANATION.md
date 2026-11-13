# Algorithmic Detection Engines: FSM, ML & Hybrid

## 1. Architectural Philosophy

TraceGuard AI implements three distinct paradigms of intrusion detection to demonstrate the strengths, limitations, and theoretical boundaries of different computational approaches:

```
                  +----------------------------------------------+
                  |           Raw Network Session Event Stream    |
                  +----------------------------------------------+
                                         |
                 +-----------------------+-----------------------+
                 |                                               |
                 v                                               v
    +--------------------------+                   +--------------------------+
    |   Deterministic FSM      |                   |    Statistical ML        |
    |   Automaton Engine       |                   |    Isolation Forest      |
    +--------------------------+                   +--------------------------+
                 |                                               |
                 | (fsm_score: 0-100)                            | (ml_score: 0-100)
                 | (violations: [delta violations])             | (anomaly_score: 0-1)
                 |                                               |
                 +-----------------------+-----------------------+
                                         |
                                         v
                         +-------------------------------+
                         |   Hybrid Arbiter Engine       |
                         |   Score: 0.6*FSM + 0.4*ML     |
                         |   Floor: max(Hybrid, 60.0)    |
                         +-------------------------------+
                                         |
                                         v
                         +-------------------------------+
                         |   Final Alert & Explanation   |
                         +-------------------------------+
```

---

## 2. Engine A: Deterministic Rule-Based FSM

### Theoretical Mechanism:
- Evaluates the session trace against the formal transition map $\delta: Q \times \Sigma \to Q$.
- **Time Complexity**: $\mathcal{O}(N)$ where $N$ is sequence length. Exact state transition lookup occurs in $\mathcal{O}(1)$ time.
- **Space Complexity**: $\mathcal{O}(|Q| \times |\Sigma|)$ footprint.

### Key Strengths:
1. **Zero False Positives for Protocol Invariants**: If a transition $\delta(q, \sigma)$ does not exist in the formal protocol specification, it is an unambiguous violation.
2. **Total Explainability**: Identifies the exact prior state $q$, incoming symbol $\sigma$, expected legal transitions, and the offending event.
3. **Instantaneous Detection**: Detects anomalies the exact moment an invalid packet arrives.

### Fundamental Limitation:
- **Blind to Volumetric Attacks**: An attacker executing thousands of valid logins per minute within legal state transitions produces zero FSM violations.

---

## 3. Engine B: Machine Learning (Isolation Forest)

### Theoretical Mechanism:
- Unsupervised anomaly detection partitioning 15 engineered session features (duration, event count, error ratios, timing variances, byte counts).
- Isolates anomalous instances by recursively generating random splits on feature sub-spaces.
- Anomaly score $s(x, n) \in [0, 1]$ represents mean path length $h(x)$ across decision trees:
  $$s(x, n) = 2^{-\frac{\mathbb{E}(h(x))}{c(n)}}$$

### Key Strengths:
1. **Detects Volumetric / Rate-Based Deviations**: Flags denial of service, burst traffic, or anomalous byte sizes.
2. **Generalization to Novel Patterns**: Flags unusual statistical profiles without requiring explicit hand-crafted rules.

### Fundamental Limitation:
- **Heuristic Nature**: Statistical variance does not equate to malicious intent. Cannot mathematically prove that a protocol sequence was violated.

---

## 4. Engine C: Hybrid Arbiter

### Theoretical Mechanism:
Combines formal automaton guarantees with statistical anomaly heuristics:

$$\text{Normalized FSM Score} = \text{Score}_{FSM} \in [0, 100]$$
$$\text{Normalized ML Score} = \min(100, \max(0, \text{Score}_{ML} \times 100))$$
$$\text{Hybrid Score}_{raw} = 0.6 \times \text{Score}_{FSM} + 0.4 \times \text{Score}_{ML}$$

### Deterministic Risk Floor:
If any formal FSM transition violation is detected:
$$\text{Hybrid Score} = \max(\text{Hybrid Score}_{raw}, 60.0)$$

This floor ensures that any confirmed protocol transition breach receives at least a medium-high severity rating, preventing an otherwise benign-looking packet from being classified as normal. Note: This is an architectural safety threshold, not a mathematical proof that all network attacks are prevented.

---

## 5. Comparative Matrix

| Feature | Deterministic FSM | Isolation Forest ML | Hybrid Engine |
|:---|:---:|:---:|:---:|
| **Paradigm** | Formal Automata Theory | Unsupervised Ensemble ML | Multi-Criterion Synthesis |
| **Verification Basis** | Transition Function $\delta(q, \sigma)$ | Feature Path Length in Trees | Composite Risk Synthesis |
| **Explainability** | Exact Causal Proof (Invalid Step) | Feature Importance Weights | Root Cause + Statistical Weight |
| **False Positive Rate** | 0% for Protocol Syntactics | Varies with Contamination (5-15%) | Minimized via Verification |
| **Zero-Day Protocol Attacks** | Instant Detection (Transition to TRAP) | Probabilistic Anomaly | Immediate Alert |
| **Brute Force / Flood** | Ineffective if transitions valid | Highly Effective | Highly Effective |
