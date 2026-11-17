# TraceGuard AI — Phase 21 Presentation Team Overview & Oral Defense Playbook

## 1. Master Team Roster & Slide Allocations

| Order | Presenter Name | Role / Subject Specialization | Assigned Slides | Slide Count | Target Duration |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **1** | **Tanmay** | Project Lead, Problem Statement & Research Scope | **1 – 4** | 4 Slides | ~2m 45s (165s) |
| **2** | **Karthik Sai** | Formal Foundations, Chomsky Hierarchy & Automaton Spec | **5 – 9** | 5 Slides | ~3m 15s (195s) |
| **3** | **Ojas Mohbansi** | Event Alphabet, 9-State Graph Topology & Empirical Trace Proofs | **10 – 14** | 5 Slides | ~3m 30s (210s) |
| **4** | **Darpan Jain** | Three-Way Language Classification, System Pipeline & ML Guard | **15 – 18** | 4 Slides | ~2m 50s (170s) |
| **5** | **Panda** | Consensus Arbitration, Live Software Lab, Chomsky Ascent & Q.E.D. | **19 – 22** | 4 Slides | ~3m 00s (180s) |
| **TOTAL** | **Full Team** | **Comprehensive Theory of Computation Viva Monograph** | **1 – 22** | **22 Slides** | **~15m 20s (920s)** |

---

## 2. Synchronized Verbal Transition & Handoff Cues

Smooth verbal transitions between presenters demonstrate teamwork, cohesion, and synchronized mastery. Every presenter must memorize their opening cue and closing handoff sentence:

### Handoff 1: Tanmay $\to$ Karthik Sai (Boundary: Slide 4 $\to$ Slide 5)
- **Tanmay (Closing Slide 4):**
  > "...And Objective 4: Hybrid Consensus Arbitration—benchmarking our deterministic FSM rules against unsupervised Isolation Forest machine learning and enforcing a 60% risk floor on any protocol violation. To present the formal mathematical foundations and Chomsky hierarchy governing our automaton, I now hand over the presentation to **Karthik Sai**."
- **Karthik Sai (Opening Slide 5):**
  > "Thank you, Tanmay. Respected professors and members of the examination committee, my name is Karthik Sai. I will be guiding you through Section 1: The Formal Mathematical Foundations of TraceGuard AI..."

### Handoff 2: Karthik Sai $\to$ Ojas Mohbansi (Boundary: Slide 9 $\to$ Slide 10)
- **Karthik Sai (Closing Slide 9):**
  > "...On the violation side, we have TRAP $\notin F$. TRAP is an absorbing dead-end state: once entered, all 13 transitions loop indefinitely back into TRAP. An attacker cannot escape TRAP by sending subsequent valid packets. To detail our 13-symbol event alphabet and walk you through our graph topology and empirical trace proofs, I now invite **Ojas Mohbansi** to the podium."
- **Ojas Mohbansi (Opening Slide 10):**
  > "Thank you, Karthik. Respected members of the evaluation committee, my name is Ojas Mohbansi. I will present the Input Alphabet, the State Graph Topology, and our Formal Trace Verification Proofs..."

### Handoff 3: Ojas Mohbansi $\to$ Darpan Jain (Boundary: Slide 14 $\to$ Slide 15)
- **Ojas Mohbansi (Closing Slide 14):**
  > "...The verdict is: REJECTED ($w_2 \notin L(M)$). We have not merely flagged an anomaly; we have established a deterministic causal proof of an exploit. To formalize this trace classification mathematically and present our system architecture and machine learning pipeline, I now hand over the presentation to **Darpan Jain**."
- **Darpan Jain (Opening Slide 15):**
  > "Thank you, Ojas. Respected professors and members of the examination committee, my name is Darpan Jain. I will present our Extended Transition Function, the System Architecture, and the Machine Learning Anomaly Guard..."

### Handoff 4: Darpan Jain $\to$ Panda (Boundary: Slide 18 $\to$ Slide 19)
- **Darpan Jain (Closing Slide 18):**
  > "...When volumetric floods or brute-force spikes occur, their path depths are significantly shorter, driving the score towards 1.0. To explain how our Consensus Arbiter combines these ML scores with our deterministic FSM proofs, I now invite **Panda** to the podium."
- **Panda (Opening Slide 19):**
  > "Thank you, Darpan. Respected faculty examiners and members of the committee, my name is Panda. I will conclude our presentation by covering Hybrid Consensus Arbitration, our Live Demonstration Laboratory, our Chomsky Roadmap, and our Final Academic Conclusions..."

---

## 3. Technical Invariant Cheat Sheet

Every presenter should be thoroughly prepared to cite these verified invariants under committee questioning:

1. **Formal 5-Tuple Definition**:
   $$M = (Q, \Sigma, \delta, q_0, F)$$
2. **State Space Partitioning ($|Q| = 9$)**:
   - $Q = \{\text{IDLE}, \text{CONNECTED}, \text{REQUEST\_RECEIVED}, \text{AUTH\_CHECKED}, \text{AUTH\_FAILED}, \text{RESPONSE\_SENT}, \text{ERROR}, \text{CLOSED}, \text{TRAP}\}$
   - Initial State: $q_0 = \text{IDLE}$
   - Accepting State Set: $F = \{\text{CLOSED}\}$ (Singleton set)
   - Absorbing Violation Sink: $\text{TRAP} \notin F$, where $\forall \sigma \in \Sigma, \delta(\text{TRAP}, \sigma) = \text{TRAP}$
3. **Input Alphabet Cardinality ($|\Sigma| = 13$)**:
   - $\Sigma = \{\text{CONNECT}, \text{CLOSE}, \text{TIMEOUT}, \text{REQUEST}, \text{AUTH\_SUCCESS}, \text{AUTH\_FAILURE}, \text{RESPONSE\_200}, \text{RESPONSE\_301}, \text{RESP\_401\_403}, \text{RESPONSE\_500}, \text{MALFORMED}, \text{ERROR\_RESPONSE}\}$
4. **Total Transition Matrix Completeness**:
   - $|\delta| = |Q| \times |\Sigma| = 9 \times 13 = 117$ total defined cells
   - Breakdown: 41 legal forward/cycle/teardown transitions + 76 absorbing TRAP violation transitions
   - Formal Theorem: $\forall q \in Q, \forall \sigma \in \Sigma, \delta(q, \sigma) \in Q$ (Zero undefined transitions)
5. **Computational Complexity Guarantees**:
   - Per-packet step decision: $O(1)$ constant time (direct memory lookup)
   - String trace recognition: $O(|w|)$ linear time in string length
6. **Extended Transition Function & Three-Way Classification**:
   - $\delta^*(q, \epsilon) = q$; $\delta^*(q, wa) = \delta(\delta^*(q, w), a)$
   - Accepted: $\delta^*(q_0, w) \in F$
   - Incomplete Prefix: $\delta^*(q_0, w) \notin F \cup \{\text{TRAP}\}$
   - Rejected: $\delta^*(q_0, w) = \text{TRAP}$
7. **Hybrid Consensus Scoring Formula**:
   $$S_h = 0.6 \cdot S_{\text{FSM}} + 0.4 \cdot S_{\text{ML}}$$
   - **60% Risk Floor Rule**: If $\text{State} = \text{TRAP} \implies S_{\text{FSM}} = 1.0 \implies S_h \ge 0.60$ regardless of ML output
8. **Isolation Forest Path Depth Anomaly Metric**:
   $$s(x,n) = 2^{-\frac{E(h(x))}{c(n)}}$$
   - Evaluated across 15 numerical session features

---

## 4. Master Rehearsal Checklist

- [ ] **Slide Images Synchronized**: Confirm all 22 slide images in `frontend/public/slides/` are 1920×1080 and match Candidate B.
- [ ] **Presenter Order Memorized**: Tanmay $\to$ Karthik Sai $\to$ Ojas Mohbansi $\to$ Darpan Jain $\to$ Panda.
- [ ] **Slide Boundaries Enforced**:
  - Tanmay: Slides 1 to 4
  - Karthik Sai: Slides 5 to 9
  - Ojas Mohbansi: Slides 10 to 14
  - Darpan Jain: Slides 15 to 18
  - Panda: Slides 19 to 22
- [ ] **Handoffs Practiced**: Run 3 continuous dry-runs focusing exclusively on the 4 boundary handoffs without looking at notes.
- [ ] **Timing Strictness**: Ensure no speaker exceeds their allotted budget by more than 20 seconds.
- [ ] **SaaS Presentation Mode Familiarity**: Practice toggling between Audience View and Presenter View (`P` key), jumping to presenter first slides, and using arrow keys.
- [ ] **Live Automata Lab Rehearsal**: Have the Automata Lab (`http://localhost:5174/#/automata-lab` or website `/automaton`) pre-loaded on a backup browser tab for live demonstration.

---

## 5. Whole-Team Viva Examination Q&A

### Q1: "Why did you build your own FSM rather than configuring an existing tool like Zeek/Bro or Suricata?"
- **Team Answer (Any Member / Tanmay or Darpan)**: "Existing network security tools like Zeek or Suricata use protocol state machines internally, but they treat protocol state as an engineering implementation detail rather than an exposed, verifiable formal automaton. Their state transitions are coupled with imperative C/C++ event handlers, making formal mathematical verification, total transition proofs, and custom hybrid arbitration with machine learning impossible. TraceGuard AI decouples the formal 5-tuple into an explicit, verifiable mathematical object with guaranteed $O(1)$ transitions and explainable proofs."

### Q2: "What is the primary academic novelty of this project for a Theory of Computation capstone?"
- **Team Answer (Ojas or Panda)**: "Our primary academic contribution is demonstrating that formal automata theory provides the exact missing link in AI-driven cybersecurity: causal explainability and guaranteed zero false positives on compliant grammar. While the industry is rushing toward opaque black-box machine learning models that generate false alarms and cannot explain their reasoning, we prove that grounding network detection in Chomsky Type-3 regular languages delivers deterministic mathematical proofs of sequence violations at line-rate speed."

### Q3: "What happens if a network packet is retransmitted or delayed by TCP?"
- **Team Answer (Karthik Sai or Darpan)**: "TraceGuard AI operates on top of a TCP session reassembly layer (similar to `libpcap` connection tracking). Our protocol parser reassembles TCP byte streams into discrete application-level HTTP events before emitting symbols into the automaton's alphabet. Therefore, TCP-level packet fragmentation or retransmission does not produce spurious FSM transitions. If true connection corruption occurs, the parser maps the event to `MALFORMED`, which deterministically routes to `TRAP`."
