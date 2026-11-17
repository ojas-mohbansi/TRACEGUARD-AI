# TraceGuard AI — Master Team Defense Agenda & Presentation Overview
## Academic Viva Monograph: Formal Protocol Automata & Hybrid NIDS
### Canonical Presentation Deck: `TraceGuard AI — Editorial Theory of Computation Deck.pptx` (22 Slides)
### Total Team Defense Duration: ~13 Minutes 30 Seconds (Target: 12–15 Minutes Slot)

---

## 1. Master Team Roster & Speaking Assignments

| Presenter | Student Name | University Roll No. | Role & Specialization | Assigned Slides | Est. Duration | File Link |
| :---: | :--- | :---: | :--- | :---: | :---: | :--- |
| **P1** | **Ojas Mohbansi** | **BT24CSE211** | Lead Speaker / Introduction & Scope Lead | Slides 1–4 | 2m 30s | [presenter_1.md](file:///c:/Projects/FSM-NIDS/docs/presentation/presenter_1.md) |
| **P2** | **Darpan Jain** | **BT24CSE212** | Formal Foundations Lead / Chomsky Hierarchy & Automaton Spec | Slides 5–9 | 3m 00s | [presenter_2.md](file:///c:/Projects/FSM-NIDS/docs/presentation/presenter_2.md) |
| **P3** | **Pranav Parsoan** | **BT24CSE205** | Automata Theory & Execution Trace Proof Lead | Slides 10–15 | 3m 30s | [presenter_3.md](file:///c:/Projects/FSM-NIDS/docs/presentation/presenter_3.md) |
| **P4** | **Tanmay** | **BT24CSE164** | Systems Implementation & Machine Learning Lead | Slides 16–19 | 2m 30s | [presenter_4.md](file:///c:/Projects/FSM-NIDS/docs/presentation/presenter_4.md) |
| **P5** | **Kartik Sai** | **BT24CSE203** | Academic Evaluation Lead / Live Demo & Defense Coordinator | Slides 20–22 | 2m 00s | [presenter_5.md](file:///c:/Projects/FSM-NIDS/docs/presentation/presenter_5.md) |
| **Total** | **5 Presenters** | — | **Full Monograph Defense** | **22 Slides** | **13m 30s** | — |

---

## 2. Seamless Speaker Transition Matrix

```
[Start Defense] 
      │
      ▼
Presenter 1 (Ojas Mohbansi) ─────────► Slides 1–4 (~2.5 mins)
      │
      ├─► Handoff Cue: "I now pass the podium to Darpan Jain, who will walk us through Section 1: The Formal Mathematical Foundations."
      ▼
Presenter 2 (Darpan Jain) ───────────► Slides 5–9 (~3.0 mins)
      │
      ├─► Handoff Cue: "I now hand over to Pranav Parsoan, who will detail our 13-symbol alphabet, state diagram topology, and execution trace proofs."
      ▼
Presenter 3 (Pranav Parsoan) ────────► Slides 10–15 (~3.5 mins)
      │
      ├─► Handoff Cue: "I now hand over to Tanmay, who will explain our system implementation, Isolation Forest ML, and hybrid consensus scoring."
      ▼
Presenter 4 (Tanmay) ────────────────► Slides 16–19 (~2.5 mins)
      │
      ├─► Handoff Cue: "I now invite Kartik Sai to walk us through our live laboratory demonstration, Chomsky hierarchy roadmap, and concluding defense remarks."
      ▼
Presenter 5 (Kartik Sai) ────────────► Slides 20–22 (~2.0 mins)
      │
      └─► Closing Cue: "Our automaton has reached its accepting halting state: CLOSED ∈ F. The team is now delighted to take your questions."
      ▼
[Faculty Viva Defense Q&A & Live Lab Demonstration]
```

---

## 3. Core Academic Invariants (Team Quick Reference)

All five presenters must strictly adhere to these established mathematical and engineering facts:

1. **Finite Automaton 5-Tuple**: $M = (Q, \Sigma, \delta, q_0, F)$.
2. **State Space ($|Q| = 9$)**: $Q = \{\text{IDLE}, \text{CONNECTED}, \text{REQUEST\_RECEIVED}, \text{AUTH\_CHECKED}, \text{AUTH\_FAILED}, \text{RESPONSE\_SENT}, \text{ERROR}, \text{CLOSED}, \text{TRAP}\}$.
3. **Alphabet ($|\Sigma| = 13$)**: 13 discrete symbols ($\text{CONNECT}, \text{CLOSE}, \text{TIMEOUT}, \text{REQUEST}, \text{AUTH\_SUCCESS}, \text{AUTH\_FAILURE}, \text{RESPONSE\_200}, \text{RESPONSE\_301}, \text{RESP\_401}, \text{RESP\_403}, \text{RESPONSE\_500}, \text{MALFORMED}, \text{ERROR\_RESPONSE}$).
4. **Total Function Completeness**: $9 \times 13 = 117$ total transitions. Zero undefined transitions.
5. **Start State**: $q_0 = \text{IDLE}$.
6. **Accepting Set**: $F = \{\text{CLOSED}\}$. Graceful teardown is the only accepting condition.
7. **Absorbing TRAP Invariant**: $\forall \sigma \in \Sigma, \delta(\text{TRAP}, \sigma) = \text{TRAP}$, and $\text{TRAP} \notin F$.
8. **Decidability**: Word membership $w \in L(M)$ is decided in constant step time $O(1)$ and linear sequence time $O(|w|)$.
9. **Hybrid Consensus Formula**:
   $$S_h = (0.60 \times S_{\text{FSM}}) + (0.40 \times S_{\text{ML}})$$
10. **Guaranteed Floor Rule**:
   $$\text{If } S_{\text{FSM}} > 0 \implies S_h \ge 60\% \quad (\text{Enforces that FSM violations are always High/Critical})$$
11. **Test Verification**: **149 / 149 automated test nodes passing at 100%**.

---

## 4. Rehearsal & Defense Checklist

- [x] All 22 slide PNGs verified at 1920×1080 resolution in `frontend/public/slides/`.
- [x] Canonical PowerPoint verified: `TraceGuard AI — Editorial Theory of Computation Deck.pptx`.
- [x] All 5 student names and roll numbers matched to Slide 1.
- [x] Spoken scripts prepared word-for-word (read-aloud tested).
- [x] Anticipated examiner questions prepared with mathematically concise answers.
- [x] Presentation Mode in web UI loads all 22 slides with Audience and Presenter View toggle.
- [x] Live Automata Laboratory operational for interactive transition stepping.
