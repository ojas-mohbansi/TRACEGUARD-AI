# Presenter 4 Speaking Guide: System Implementation, ML & Hybrid Scoring
## Speaker: Tanmay (BT24CSE164)
### Assigned Slides: Slide 16 to Slide 19 (Total: 4 Slides)
### Target Speaking Duration: ~2 Minutes 30 Seconds

---

## 1. Presenter Profile & Core Responsibility
- **Role**: Systems Implementation & Machine Learning Lead
- **Focus**: Present the system pipeline, unsupervised Isolation Forest ML (15 numerical features, anomaly path depth formula), and the hybrid consensus scoring formula with the guaranteed 60% risk floor.
- **Academic Invariant**: $S_h = \max(0.60 \cdot S_{\text{FSM}} + 0.40 \cdot S_{\text{ML}}, \; \mathbb{I}_{\text{FSM}} \cdot 60)$; $S_{\text{ML}} = 2^{-E(h(x))/c(n)}$.

---

## 2. Slide-by-Slide Speaking Script

### Slide 16: Section 02 // System Implementation: Hybrid Triad Detection Engine
- **Slide Title**: Section 02 // System Implementation: Hybrid Triad Detection Engine
- **Visual Display**: Section divider: Hybrid Triad Detection Engine (Deterministic FSM Guard + Isolation Forest ML + Consensus Arbiter).
- **Spoken Script (Read Aloud)**:
> "Thank you, Pranav. Respected examiners, I am Tanmay (BT24CSE164). I will now present Section 2: System Implementation and Hybrid Detection.
>
> While finite state machines guarantee deterministic sequence correctness, real-world network attacks also include volumetric threats that strictly obey protocol rules—such as authentication brute-force retries and slow-rate data exfiltration.
> To address this, TraceGuard AI implements a **Hybrid Triad Architecture** uniting formal automata with unsupervised machine learning."

---

### Slide 17: 14 // End-to-End Visual Architecture: Ingestion Pipeline
- **Slide Title**: 14 // End-to-End Visual Architecture: End-to-End Triad System Pipeline
- **Visual Display**: System pipeline diagram: Packet Sniffer (Npcap/PCAP) -> Protocol Parser -> Session Bus -> Parallel FSM & ML Engines -> Consensus Arbiter -> SOC Dashboard.
- **Spoken Script (Read Aloud)**:
> "Slide 17 illustrates our end-to-end data processing pipeline:
> 1. **Ingestion**: Raw network packets are captured in real-time via Npcap or replayed from offline PCAP captures.
> 2. **Parsing & Privacy**: Packets are parsed into discrete HTTP events while sensitive credentials (passwords, JWTs, API tokens) are strictly redacted.
> 3. **Dual Dispatch**: Every session event stream is fed concurrently to our two analysis engines:
>    - The **FSM Engine** evaluates sequential transition membership $\delta(q, \sigma)$.
>    - The **Feature Extractor** aggregates 15 statistical metrics across the session and feeds them to our **Isolation Forest ML model**.
> 4. **Consensus Arbitration**: The outputs are merged by our scoring arbiter and surfaced in real-time to the SOC Dashboard."

---

### Slide 18: 15 // Statistical Anomaly Guard: Unsupervised Isolation Forest
- **Slide Title**: 15 // Statistical Anomaly Guard: Unsupervised Isolation Forest ML
- **Visual Display**: Isolation Forest math card: 15 extracted session features; anomaly score formula $s(x,n) = 2^{-E(h(x))/c(n)}$; path depth explanation.
- **Spoken Script (Read Aloud)**:
> "Our statistical component uses an unsupervised Isolation Forest. Unlike traditional classifiers that model normal data density, Isolation Forest explicitly isolates anomalous instances using random decision trees.
>
> We extract 15 numerical features per session:
> - **Volumetric**: Event count, total bytes, average payload size.
> - **Temporal**: Session duration, inter-arrival time variance.
> - **Error Ratios**: HTTP error response ratios and authentication failure counts.
>
> The anomaly score is computed as:
> $$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$
> Where $h(x)$ is the tree path length and $c(n)$ is the average path length of unsuccessful searches in a Binary Search Tree. Anomalous volumetric spikes require fewer random splits to isolate, resulting in short tree paths and elevated anomaly scores without requiring labeled attack datasets."

---

### Slide 19: 16 // Hybrid Consensus Arbitration: Multi-Detector Benchmark & 60% Floor
- **Slide Title**: 16 // Hybrid Consensus Arbitration: Detector Benchmark & Risk Floor Rule
- **Visual Display**: Hybrid formula card: $S_h = 0.6 \cdot S_{\text{FSM}} + 0.4 \cdot S_{\text{ML}}$; 60% minimum floor rule; 4-quadrant attribution breakdown.
- **Spoken Script (Read Aloud)**:
> "Slide 19 details our hybrid consensus arbitration formula:
> $$S_h = (0.60 \times S_{\text{FSM}}) + (0.40 \times S_{\text{ML}})$$
> 
> However, an arithmetic weighted average poses a critical security hazard: if an attacker executes a severe protocol sequence violation but keeps payload volume tiny, a low ML score could dilute the combined risk score below the detection threshold.
> 
> To prevent this, we enforce a **Mandatory Academic Invariant**:
> $$\text{If } S_{\text{FSM}} > 0 \implies S_h \ge 60\% \quad (\text{Guaranteed Invariant Floor})$$
> Any sequence that triggers an invalid DFA transition is mathematically guaranteed a minimum combined risk score of 60%, ensuring protocol violations can never be dismissed by statistical models.
>
> I now invite **Kartik Sai** to walk us through our live laboratory demonstration, Chomsky roadmap, and defense conclusions."

---

## 3. Transition to Next Speaker
- **Handoff Sentence**: *"I now invite Kartik Sai to walk us through our live laboratory demonstration, Chomsky hierarchy roadmap, and concluding defense remarks."*

---

## 4. Anticipated Examiner Defense Questions & Model Answers

### Question 1: Why did you choose Isolation Forest over Deep Learning (e.g. LSTM or Autoencoders)?
- **Concise Answer**: *"Isolation Forest is completely unsupervised, requires no expensive GPU training, and runs with $O(n \log n)$ training and $O(t \cdot \text{depth})$ inference complexity. In our hybrid model, sequence tracking is already proven by the DFA in $O(1)$ time, so ML only needs to detect volumetric statistical outliers."*

### Question 2: What is the justification for the 0.6 / 0.4 weight distribution?
- **Concise Answer**: *"Automata theory provides deterministic mathematical proof of non-compliance, whereas machine learning provides probabilistic anomaly estimation. We weight the deterministic FSM higher (0.60) to prioritize formal language proofs, while giving statistical evidence a substantial secondary voice (0.40)."*
