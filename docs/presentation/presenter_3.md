# Presenter 3 Speaking Guide: Alphabet, Topology & Trace Decidability
## Speaker: Pranav Parsoan (BT24CSE205)
### Assigned Slides: Slide 10 to Slide 15 (Total: 6 Slides)
### Target Speaking Duration: ~3 Minutes 30 Seconds

---

## 1. Presenter Profile & Core Responsibility
- **Role**: Automata Theory & Execution Trace Proof Lead
- **Focus**: Detail the 13-symbol input alphabet $\Sigma$, the 9-state transition topology, 117-cell matrix partitioning, canonical trace proof $w_1$, adversarial attack trace proof $w_2$, and the 3-way language classification via $\delta^*$.
- **Academic Invariant**: $\delta(\text{TRAP}, \sigma) = \text{TRAP} \quad \forall \sigma \in \Sigma$; $\delta^*(q_0, w) \in F \implies \text{Accepted}$, $\delta^*(q_0, w) = \text{TRAP} \implies \text{Rejected}$.

---

## 2. Slide-by-Slide Speaking Script

### Slide 10: 08 // Input Alphabet Σ (|Σ| = 13)
- **Slide Title**: 08 // Input Alphabet $\Sigma$: 13-Symbol Protocol Event Alphabet
- **Visual Display**: Alphabet breakdown into 4 functional classes: Session (3), Auth & Req (3), Status (4), Faults (3).
- **Spoken Script (Read Aloud)**:
> "Thank you, Darpan. Respected examiners, I am Pranav Parsoan (BT24CSE205). I will now present our 13-symbol alphabet, state topology, and formal execution trace proofs.
>
> In automata theory, the alphabet $\Sigma$ represents the set of discrete symbols over which input words are formed. In TraceGuard AI, network packets are parsed into 13 formal event symbols partitioned into four classes:
> 1. **Session Control (3 symbols)**: $\text{CONNECT}$, $\text{CLOSE}$, $\text{TIMEOUT}$.
> 2. **Authentication & Dispatch (3 symbols)**: $\text{REQUEST}$, $\text{AUTH\_SUCCESS}$, $\text{AUTH\_FAILURE}$.
> 3. **HTTP Status Emissions (4 symbols)**: $\text{RESPONSE\_200}$, $\text{RESPONSE\_301}$, $\text{RESP\_401}$, $\text{RESP\_403}$.
> 4. **Fault & Error Signals (3 symbols)**: $\text{RESPONSE\_500}$, $\text{MALFORMED}$, $\text{ERROR\_RESPONSE}$.
> This 13-symbol alphabet captures the complete functional vocabulary of HTTP session interactions."

---

### Slide 11: 09 // Complete Directed State Diagram
- **Slide Title**: 09 // Complete Directed State Diagram: 9-State Total DFA Topology
- **Visual Display**: Complete directed graph layout with colored states, canonical forward edges, keep-alive cycles, error branches, and absorbing TRAP transitions.
- **Spoken Script (Read Aloud)**:
> "Slide 11 shows the complete directed state transition graph of our 9-state HTTP DFA.
> Notice the clear paths through the automaton:
> The green canonical path flows from $\text{IDLE} \xrightarrow{\text{CONNECT}} \text{CONNECTED} \xrightarrow{\text{REQUEST}} \text{REQUEST\_RECEIVED} \xrightarrow{\text{AUTH\_SUCCESS}} \text{AUTH\_CHECKED} \xrightarrow{\text{RESPONSE\_200}} \text{RESPONSE\_SENT} \xrightarrow{\text{CLOSE}} \text{CLOSED}$.
> We also model HTTP/1.1 keep-alive cycles from $\text{RESPONSE\_SENT}$ back to $\text{REQUEST\_RECEIVED}$ on subsequent requests, error handling transitions into $\text{ERROR}$, and authentication retry loops.
> Crucially, notice the red sink node: $\text{TRAP}$. Every illegal transition from any state routes directly into $\text{TRAP}$."

---

### Slide 12: 10 // Matrix Partitioning: 117-Cell Distribution
- **Slide Title**: 10 // Matrix Partitioning: 117-Cell Total Function Distribution
- **Visual Display**: Matrix cell breakdown: Legal forward/cycle transitions vs. absorbing TRAP violation transitions.
- **Spoken Script (Read Aloud)**:
> "This slide illustrates the structural distribution of our 117 matrix entries.
> While a small subset of transitions represent valid protocol steps and cyclic reuse, the vast majority route into $\text{TRAP}$.
> For instance, from state $\text{IDLE}$, only $\text{CONNECT}$ is valid; the other 12 symbols route to $\text{TRAP}$. From $\text{CLOSED}$, no further operations are permitted—any event transitions into $\text{TRAP}$.
> This dense rejection coverage mathematically guarantees that arbitrary or malicious packet injections cannot traverse the state machine without triggering an immediate state trap."

---

### Slide 13: 11 // Canonical Execution Trace w₁ (Accepted)
- **Slide Title**: 11 // Canonical Execution Trace $w_1$: Valid Protocol Sequence
- **Visual Display**: Sequential trace table: $w_1 = \langle \text{CONNECT}, \text{REQUEST}, \text{AUTH\_SUCCESS}, \text{RESPONSE\_200}, \text{CLOSE} \rangle$; final state: CLOSED in F; Verdict: ACCEPTED.
- **Spoken Script (Read Aloud)**:
> "Let us examine a formal trace execution proof for a legitimate session, word $w_1$:
> The session begins at $q_0 = \text{IDLE}$.
> Step 1: $\delta(\text{IDLE}, \text{CONNECT}) = \text{CONNECTED}$.
> Step 2: $\delta(\text{CONNECTED}, \text{REQUEST}) = \text{REQUEST\_RECEIVED}$.
> Step 3: $\delta(\text{REQUEST\_RECEIVED}, \text{AUTH\_SUCCESS}) = \text{AUTH\_CHECKED}$.
> Step 4: $\delta(\text{AUTH\_CHECKED}, \text{RESPONSE\_200}) = \text{RESPONSE\_SENT}$.
> Step 5: $\delta(\text{RESPONSE\_SENT}, \text{CLOSE}) = \text{CLOSED}$.
> The word $w_1$ is consumed completely. The final state is $\text{CLOSED}$, which belongs to $F$. Therefore, the formal mathematical verdict is: **ACCEPTED**, $w_1 \in L(M)$. Zero false alerts generated."

---

### Slide 14: 12 // Adversarial Trace w₂ (Rejected)
- **Slide Title**: 12 // Adversarial Trace $w_2$: Out-of-Order Exploit Rejection
- **Visual Display**: Adversarial trace: $w_2 = \langle \text{CONNECT}, \text{RESPONSE\_200}, \text{REQUEST}, \text{CLOSE} \rangle$; step 2 triggers TRAP; subsequent symbols absorbed; Verdict: REJECTED.
- **Spoken Script (Read Aloud)**:
> "Now observe an adversarial attack trace, word $w_2$. In this scenario, an attacker injects an unprompted HTTP 200 response immediately after connection, attempting an out-of-order execution exploit:
> Step 1: $\delta(\text{IDLE}, \text{CONNECT}) = \text{CONNECTED}$.
> Step 2: In state $\text{CONNECTED}$, the symbol $\text{RESPONSE\_200}$ is received. In our transition matrix:
> $$\delta(\text{CONNECTED}, \text{RESPONSE\_200}) = \text{TRAP}$$
> The automaton instantly enters $\text{TRAP}$.
> Steps 3 and 4: Subsequent symbols like $\text{REQUEST}$ and $\text{CLOSE}$ are absorbed by the TRAP self-loop: $\delta(\text{TRAP}, \sigma) = \text{TRAP}$.
> At sequence termination, the state is $\text{TRAP} \notin F$. We obtain an indisputable mathematical proof: $w_2 \notin L(M)$. The attack is rejected with zero false positives."

---

### Slide 15: 13 // Extended Transition δ*(q₀, w): Three-Way Classification
- **Slide Title**: 13 // Extended Transition Function $\delta^*(q_0, w)$: Three-Way Language Classification
- **Visual Display**: Three-way verdict diagram: 1. Accepted ($\delta^* \in F$), 2. Incomplete Valid ($\delta^* \notin F \cup \{\text{TRAP}\}$), 3. Rejected ($\delta^* = \text{TRAP}$).
- **Spoken Script (Read Aloud)**:
> "Using the formal extended transition function $\delta^*: Q \times \Sigma^* \to Q$, TraceGuard AI classifies any observed session string $w$ into one of three mutually exclusive categories:
> 1. **Accepted ($w \in L(M)$)**: $\delta^*(q_0, w) \in F$. The session has executed gracefully and terminated at $\text{CLOSED}$.
> 2. **Incomplete Valid Prefix**: $\delta^*(q_0, w) \notin F \cup \{\text{TRAP}\}$. The session is valid so far and actively communicating.
> 3. **Rejected Violation**: $\delta^*(q_0, w) = \text{TRAP}$. A protocol sequence rule was violated, locking the session into the dead sink state.
>
> I now hand over to **Tanmay**, who will explain our system implementation, Isolation Forest ML, and hybrid consensus scoring."

---

## 3. Transition to Next Speaker
- **Handoff Sentence**: *"I now hand over to Tanmay, who will explain our system implementation, Isolation Forest ML, and hybrid consensus scoring."*

---

## 4. Anticipated Examiner Defense Questions & Model Answers

### Question 1: What is the formal inductive definition of the extended transition function delta*?
- **Concise Answer**: *"$\delta^*$ is defined inductively over string length: Base step: $\delta^*(q, \epsilon) = q$, where $\epsilon$ is the empty string. Inductive step: For any string $w \in \Sigma^*$ and symbol $a \in \Sigma$, $\delta^*(q, wa) = \delta(\delta^*(q, w), a)$."*

### Question 2: Why can't an attacker escape the TRAP state by sending a valid CLOSE packet?
- **Concise Answer**: *"Because TRAP is an absorbing sink state. In our transition matrix, for all $\sigma \in \Sigma$, $\delta(\text{TRAP}, \sigma) = \text{TRAP}$. Even if an attacker emits a syntactically valid CLOSE, $\delta(\text{TRAP}, \text{CLOSE})$ evaluates strictly to TRAP. The session can never return to an accepting state."*
