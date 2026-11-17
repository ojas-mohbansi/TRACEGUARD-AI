# Presenter 1 Speaking Guide: Project Overview, Problem Statement & Research Scope
## Speaker: Ojas Mohbansi (BT24CSE211)
### Assigned Slides: Slide 1 to Slide 4 (Total: 4 Slides)
### Target Speaking Duration: ~2 Minutes 30 Seconds

---

## 1. Presenter Profile & Core Responsibility
- **Role**: Lead Speaker & Introduction Specialist
- **Focus**: Introduce TraceGuard AI, state the cybersecurity and theoretical challenge, explain the paradigm shift from black-box ML to deterministic automata, and outline our research scope.
- **Academic Invariant**: Finite automata guarantee $O(1)$ step execution time and zero false positives on compliant RFC protocol grammar.

---

## 2. Slide-by-Slide Speaking Script

### Slide 1: Theory of Computation // Academic Viva Monograph: Title Slide
- **Slide Title**: TraceGuard AI: Formal Languages & Protocol Automata
- **Visual Display**: Monograph title, student names and roll numbers, 9-State Complete DFA badge ($9 \times 13 = 117$ Total Transitions).
- **Spoken Script (Read Aloud)**:
> "Good morning, respected professors, faculty examiners, and fellow scholars. I am Ojas Mohbansi (BT24CSE211). Along with my colleagues Darpan Jain, Pranav Parsoan, Tanmay, and Kartik Sai, we present our Theory of Computation final monograph: **TraceGuard AI: Network Intrusion Detection via Deterministic Finite-State Automata and Unsupervised Machine Learning**.
>
> In this defense, our team demonstrates that formal automata theory is not merely an abstract textbook concept, but an indispensable mathematical formalism for solving real-world cybersecurity vulnerabilities. By constructing a complete 9-state HTTP Deterministic Finite Automaton with 117 total transition mappings, we prove that protocol sequence attacks can be verified in constant $O(1)$ step time with mathematical certainty."

---

### Slide 2: 01 // Problem Statement: Stateful Protocol Vulnerabilities
- **Slide Title**: 01 // Problem Statement: Stateful Protocol Vulnerabilities
- **Visual Display**: Stateful protocol threat landscape: Out-of-Order Execution, Authentication Bypass, and Session Confusion.
- **Spoken Script (Read Aloud)**:
> "To understand why automata theory is necessary, we must examine how modern communication protocols operate. Protocols like HTTP, TLS, and SSH are fundamentally stateful systems: actions are only valid when executed in strict sequential order.
>
> Traditional signature-based firewalls inspect payload strings, while deep learning models compute statistical likelihoods. Neither mathematically verifies whether an observed sequence of protocol operations is legal according to specification. Attackers exploit this blind spot in three critical ways:
> First, **Out-of-Order Execution**: sending server responses before client requests are received.
> Second, **Authentication Bypass**: attempting direct resource access before traversing identity verification states.
> And third, **Session Confusion**: injecting packets into already closed or half-open connections.
> These are not payload anomalies—they are structural invariant violations."

---

### Slide 3: 02 // Paradigm Shift: Black-Box ML vs. Formal Automata
- **Slide Title**: 02 // Paradigm Shift: Black-Box ML vs. Formal Automata
- **Visual Display**: Side-by-side comparison matrix: Statistical ML Limits vs. Automata Theory Solution.
- **Spoken Script (Read Aloud)**:
> "This slide illustrates the core paradigm shift of TraceGuard AI. 
> Purely statistical machine learning suffers from three fundamental limitations in network intrusion detection:
> First, high false-positive rates, because rare but entirely legal protocol flows are flagged as anomalies.
> Second, zero formal proof: neural networks provide probability scores without causal explanations.
> And third, high inference latency that cannot keep pace with high-speed packet ingestion.
>
> By contrasting ML with formal automata theory, we achieve:
> First, **constant $O(1)$ step execution time**, where state transitions occur instantly via matrix lookup.
> Second, **mathematically proven zero false positives** on compliant protocol grammar.
> And third, **total explainability**, pinpointing the exact state, symbol, and transition rule violated."

---

### Slide 4: 03 // Research Scope: Four Core Project Objectives
- **Slide Title**: 03 // Research Scope: Four Core Project Objectives
- **Visual Display**: Four sequential objective cards: Protocol DFA, Total Matrix, Word Stepper, Hybrid Arbiter.
- **Spoken Script (Read Aloud)**:
> "To realize this paradigm shift, our team formulated four concrete engineering and mathematical objectives:
> 1. **Protocol DFA**: Formulate the canonical HTTP session lifecycle as a formal 5-tuple $M = (Q, \Sigma, \delta, q_0, F)$.
> 2. **Total Transition Matrix**: Guarantee complete mathematical decidability by routing all invalid state-symbol pairs into an absorbing TRAP sink across 117 cells.
> 3. **Word Stepper Engine**: Implement the extended transition function $\delta^*$ to classify observed network sessions into accepted languages, incomplete prefixes, and rejected exploit traces.
> 4. **Hybrid Consensus Arbiter**: Couple our deterministic FSM with an unsupervised Isolation Forest, ensuring protocol violations retain a guaranteed minimum 60% risk floor.
>
> I now pass the podium to **Darpan Jain**, who will walk us through Section 1: The Formal Mathematical Foundations."

---

## 3. Transition to Next Speaker
- **Handoff Sentence**: *"I now pass the podium to Darpan Jain, who will walk us through Section 1: The Formal Mathematical Foundations of our protocol automaton."*

---

## 4. Anticipated Examiner Defense Questions & Model Answers

### Question 1: Why is Theory of Computation relevant to modern network security?
- **Concise Answer**: *"Communication protocols are formally specified as state machines with strict sequencing invariants. In Theory of Computation, regular languages recognized by DFAs allow us to decide word membership $w \in L(M)$ in linear time $O(|w|)$. Applying this to network streams enables deterministic, zero-false-positive detection of structural attacks that bypass statistical filters."*

### Question 2: Why can't a signature-based firewall or regular expression engine solve this?
- **Concise Answer**: *"Standard regex engines inspect packet payloads in isolation without tracking session-level state transitions across time. Our DFA maintains an internal state register across multiple packets, verifying the chronological ordering of the entire multi-packet conversation."*
