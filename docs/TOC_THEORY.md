# Theory of Computation Foundations: Automata & Formal Languages

## 1. Introduction to Formal Language Theory

The Theory of Computation provides the mathematical foundations for understanding what can be computed efficiently and modeled deterministically. Within Chomsky's hierarchy, the simplest class of formal languages is the class of **Regular Languages**, which are precisely the languages recognized by **Finite Automata**.

In modern computer systems, protocol specifications—such as TCP handshakes, TLS session negotiation, and HTTP transaction flows—define permissible sequences of operations. By modeling these communication protocols as formal automata, network intrusion detection systems (NIDS) can verify protocol compliance with mathematical rigor.

---

## 2. Deterministic Finite Automata (DFA)

A Deterministic Finite Automaton (DFA) is formally defined as a 5-tuple:

$$\mathcal{M} = (Q, \Sigma, \delta, q_0, F)$$

Where:
1. $Q$ is a non-empty, finite set of **states**.
2. $\Sigma$ is a non-empty, finite set of input symbols called the **alphabet**.
3. $\delta: Q \times \Sigma \to Q$ is the **transition function**, mapping each state and input symbol to exactly one subsequent state.
4. $q_0 \in Q$ is the designated **start state**.
5. $F \subseteq Q$ is the set of **accepting (or final) states**.

### Extended Transition Function ($\delta^*$)
To process strings of symbols rather than individual characters, we inductively define the extended transition function $\delta^*: Q \times \Sigma^* \to Q$:
- Basis: $\delta^*(q, \epsilon) = q$, where $\epsilon$ denotes the empty string.
- Induction: For $w \in \Sigma^*$ and $a \in \Sigma$, $\delta^*(q, wa) = \delta(\delta^*(q, w), a)$.

---

## 3. Regular Languages and Language Recognition

The language recognized (or accepted) by an automaton $\mathcal{M}$, denoted $L(\mathcal{M})$, is defined as:

$$L(\mathcal{M}) = \{ w \in \Sigma^* \mid \delta^*(q_0, w) \in F \}$$

According to **Kleene's Theorem**, a language $L$ is regular if and only if there exists a finite automaton that accepts $L$. Regular languages can equivalently be denoted by Regular Expressions (Regex).

### Regular Expression for TraceGuard HTTP Protocol:
The set of valid complete sessions accepted by TraceGuard's automaton corresponds to:

$$\mathcal{L}_{HTTP} = \text{CONNECT} \cdot \left( \text{TIMEOUT} \mid \text{REQUEST} \cdot \left( (\text{AUTH\_SUCCESS} \cdot (\text{RESP\_200} \mid \text{RESP\_301})) \mid (\text{AUTH\_FAILURE} \cdot (\text{RESP\_401} \mid \text{RESP\_403})) \mid (\text{MALFORMED} \cdot (\text{ERROR\_RESP} \mid \epsilon)) \mid (\text{AUTH\_SUCCESS} \cdot \text{RESP\_500} \cdot (\text{ERROR\_RESP} \mid \epsilon)) \right) \cdot (\text{REQUEST} \cdot \dots)^* \cdot \text{CLOSE} \right)$$

---

## 4. Acceptance vs. Validity vs. Incomplete Prefixes

In practical protocol verification, it is critical to distinguish three categories of string evaluations:

1. **Accepted Sequence ($w \in L(\mathcal{M})$)**:
   - Every transition in the sequence is defined in $\delta$.
   - The automaton terminates in an accepting state: $\delta^*(q_0, w) \in F$.
   - *Example*: `CONNECT` $\to$ `REQUEST` $\to$ `AUTH_SUCCESS` $\to$ `RESPONSE_200` $\to$ `CLOSE`.

2. **Valid Incomplete Prefix ($w \notin L(\mathcal{M})$, but $\exists v$ such that $wv \in L(\mathcal{M})$)**:
   - Every transition executed so far is completely valid according to $\delta$.
   - The input has paused or ended before reaching a terminal accepting state ($q \notin F$).
   - *Example*: `CONNECT` $\to$ `REQUEST` $\to$ `AUTH_SUCCESS`. (Valid protocol behavior in progress).

3. **Rejected Sequence ($w \notin L(\mathcal{M})$ and $\delta^*(q_0, w)$ is undefined)**:
   - There exists some prefix $u \cdot \sigma \sqsubseteq w$ where $\delta(\delta^*(q_0, u), \sigma) = \emptyset$.
   - This represents an explicit **protocol invariant violation**, indicative of unauthorized state tampering, packet injection, or implementation vulnerabilities.
   - *Example*: `CONNECT` $\to$ `RESPONSE_200` (Server emits response before request is ever transmitted).

---

## 5. Scope & Pedagogical Abstraction

> [!NOTE]
> The HTTP state machine implemented in TraceGuard AI is an **educational abstraction** of selected HTTP/1.1 session lifecycles designed for university-level demonstration. It models transport connection, basic authentication checkpoints, status code responses, and connection termination. It is not intended to represent the full RFC 7230/9112 specification (e.g. chunked transfer coding, multi-part bodies, or HTTP/2 frame multiplexing).
