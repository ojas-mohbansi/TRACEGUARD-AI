"""Generate professional university presentation slides for TraceGuard AI Theory of Computation defense."""
import os
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Initialize Presentation
prs = pptx.Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

blank_layout = prs.slide_layouts[6]

# Theme Colors
BG_COLOR = RGBColor(13, 17, 23)        # #0d1117 (Dark Charcoal)
CARD_BG = RGBColor(22, 27, 34)         # #161b22 (Container BG)
BORDER_COLOR = RGBColor(48, 54, 61)    # #30363d (Border)
TEXT_WHITE = RGBColor(240, 246, 252)   # #f0f6fc (Primary White)
TEXT_MUTED = RGBColor(139, 148, 158)   # #8b949e (Muted Slate)
ACCENT_TEAL = RGBColor(66, 214, 178)   # #42d6b2 (Emerald Teal)
ACCENT_BLUE = RGBColor(84, 167, 255)   # #54a7ff (Formal Blue)
ACCENT_RED = RGBColor(255, 100, 124)   # #ff647c (Rejection Red)
ACCENT_GOLD = RGBColor(245, 184, 75)   # #f5b84b (Accepting Gold)

def add_header(slide, title, category="THEORY OF COMPUTATION — FORMAL AUTOMATA"):
    """Adds uniform dark background, category pill, and main slide title."""
    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_COLOR
    bg.line.color.rgb = BG_COLOR

    # Category Pill
    pill = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
    tf = pill.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = category.upper()
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_TEAL

    # Main Title
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
    tf_title = tb.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_WHITE

def add_notes(slide, notes_text):
    """Adds speaker notes to slide."""
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text

# ==========================================
# SLIDE 1: Title Slide
# ==========================================
s1 = prs.slides.add_slide(blank_layout)
bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
bg1.fill.solid()
bg1.fill.fore_color.rgb = BG_COLOR
bg1.line.color.rgb = BG_COLOR

# Accent top bar
bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(0.8), Inches(0.08))
bar.fill.solid()
bar.fill.fore_color.rgb = ACCENT_TEAL
bar.line.color.rgb = ACCENT_TEAL

tb = s1.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(3.0))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "TraceGuard AI"
p.font.size = Pt(44)
p.font.bold = True
p.font.color.rgb = TEXT_WHITE

p2 = tf.add_paragraph()
p2.text = "Network Intrusion Detection Using Finite-State Models & Machine Learning"
p2.font.size = Pt(20)
p2.font.color.rgb = ACCENT_TEAL
p2.space_before = Pt(8)

p3 = tf.add_paragraph()
p3.text = "A Formal Theory of Computation Project on Protocol Automata & Regular Languages"
p3.font.size = Pt(14)
p3.font.color.rgb = TEXT_MUTED
p3.space_before = Pt(14)

# Metadata Card
meta_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.8), Inches(11.7), Inches(1.8))
meta_box.fill.solid()
meta_box.fill.fore_color.rgb = CARD_BG
meta_box.line.color.rgb = BORDER_COLOR
meta_tf = meta_box.text_frame
meta_tf.word_wrap = True

mp1 = meta_tf.paragraphs[0]
mp1.text = "Academic Evaluation & Viva Defense"
mp1.font.size = Pt(13)
mp1.font.bold = True
mp1.font.color.rgb = ACCENT_BLUE

mp2 = meta_tf.add_paragraph()
mp2.text = "Subject: Theory of Computation / Formal Languages and Automata Theory"
mp2.font.size = Pt(11)
mp2.font.color.rgb = TEXT_WHITE
mp2.space_before = Pt(4)

mp3 = meta_tf.add_paragraph()
mp3.text = "Demonstration: Complete 9-State DFA | Total 117-Transition Matrix | Hybrid Consensus Engine"
mp3.font.size = Pt(11)
mp3.font.color.rgb = TEXT_MUTED
mp3.space_before = Pt(4)

add_notes(s1, 
"Good morning, respected professors and examiners. Today I am presenting TraceGuard AI, a project developed for the Theory of Computation course. "
"TraceGuard AI demonstrates how classical automata theory—specifically Complete Deterministic Finite Automata, transition systems, and regular languages—can be applied to network intrusion detection. "
"While modern cybersecurity often treats detection as an opaque statistical problem, we show that formal automata provide mathematical proof of protocol compliance with zero false positives. Let us examine the motivation behind this work."
)

# ==========================================
# SLIDE 2: Problem Statement
# ==========================================
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "Problem Statement: Protocol Invariants vs. Black-Box ML")

cols = [
    ("Stateful Protocol Vulnerabilities", 
     "Network protocols (HTTP, TLS, SSH) strictly govern transaction sequencing. Exploits routinely violate sequence invariants:\n\n"
     "• Out-of-Order Execution: Emitting responses before receiving client requests.\n"
     "• Authentication Bypass: Transitioning directly to secured resources without authentication verification.\n"
     "• Session Confusion: Illegitimate packet injection into terminated sessions.",
     ACCENT_RED),
    ("Limitations of Statistical ML",
     "Modern intrusion detection relies heavily on statistical machine learning (Deep Learning, Decision Forests):\n\n"
     "• High False Positive Rates: Normal but rare sequence variations are misclassified.\n"
     "• Opacity & Lack of Proof: Cannot provide a formal causal proof of protocol violation.\n"
     "• Latency Overhead: Ineffective at instantaneous packet-level verification.",
     ACCENT_GOLD),
    ("The Automata Theory Solution",
     "Model valid communication protocol flows as formal state machines:\n\n"
     "• Deterministic Decisions: Evaluates legality in O(1) time per event step.\n"
     "• Zero False Positives: Mathematical guarantee that invalid transitions violate protocol specifications.\n"
     "• Total Explainability: Pinpoints the exact state, symbol, and illegal transition.",
     ACCENT_TEAL)
]

for idx, (col_title, col_text, col_accent) in enumerate(cols):
    left = Inches(0.8 + idx * 4.0)
    box = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.8), Inches(3.7), Inches(4.8))
    box.fill.solid()
    box.fill.fore_color.rgb = CARD_BG
    box.line.color.rgb = col_accent
    tf = box.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = col_title
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = col_accent
    
    p_body = tf.add_paragraph()
    p_body.text = col_text
    p_body.font.size = Pt(11)
    p_body.font.color.rgb = TEXT_WHITE
    p_body.space_before = Pt(8)

add_notes(s2,
"In modern computer networks, communication protocols operate as stateful dialogues. Attacks frequently exploit out-of-order execution, such as requesting secured endpoints before authenticating or injecting data after a session has closed. "
"Conventional machine learning detectors evaluate statistical features like packet sizes or arrival rates. However, statistical models cannot mathematically prove that a protocol specification was violated, and they frequently suffer from false positives. "
"Our solution is to ground detection in formal automata theory. A deterministic automaton evaluates every incoming packet in O(1) time and provides mathematical proof of sequence validity."
)

# ==========================================
# SLIDE 3: Project Objectives
# ==========================================
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "Project Objectives: Formal Theory Applied to Intrusion Detection")

objs = [
    ("1. Formal Protocol Modeling", "Formulate an educational HTTP communication model as a mathematically rigorous Deterministic Finite Automaton M = (Q, Sigma, delta, q0, F).", ACCENT_BLUE),
    ("2. Total Transition Completeness", "Implement a complete DFA with an explicit TRAP state guaranteeing total transition coverage: for all states and symbols, delta(q, sigma) in Q.", ACCENT_TEAL),
    ("3. Language Recognition & Stepper", "Build an interactive stepping engine that distinguishes accepted words, incomplete valid prefixes, and formally rejected strings.", ACCENT_GOLD),
    ("4. Comparative Detection Triad", "Integrate a supporting Isolation Forest ML detector and a Hybrid Arbiter to compare deterministic protocol rules against statistical anomaly scores.", ACCENT_RED),
]

for idx, (title_text, body_text, col_accent) in enumerate(objs):
    y_pos = Inches(1.8 + idx * 1.25)
    box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y_pos, Inches(11.7), Inches(1.05))
    box.fill.solid()
    box.fill.fore_color.rgb = CARD_BG
    box.line.color.rgb = BORDER_COLOR
    tf = box.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = col_accent
    
    p2 = tf.add_paragraph()
    p2.text = body_text
    p2.font.size = Pt(11)
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(4)

add_notes(s3,
"The primary objective of TraceGuard AI is to bridge formal language theory with applied cyber defense. "
"First, we formalize protocol interactions using the 5-tuple automaton notation. "
"Second, we enforce total transition completeness by adding an explicit TRAP state, turning a partial protocol map into a mathematically rigorous complete DFA. "
"Third, we build an interactive execution debugger that visually demonstrates language acceptance versus transition validity. "
"Finally, we implement a multi-detector comparison comparing our rule-based FSM against statistical machine learning."
)

# ==========================================
# SLIDE 4: TOC Foundations
# ==========================================
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "Theory of Computation Foundations: Regular Languages & DFAs")

toc_cards = [
    ("Chomsky Hierarchy: Regular Languages", 
     "Regular Languages (Type-3) represent the foundational class of formal languages.\n\n"
     "• Equivalent to languages accepted by Finite Automata (Kleene's Theorem).\n"
     "• Memoryless property: The next state depends strictly on current state and next input symbol.\n"
     "• Expressible as Regular Expressions over event alphabet Sigma.",
     ACCENT_BLUE),
    ("Deterministic Finite Automata (DFA)",
     "A DFA transitions deterministically between finite internal states.\n\n"
     "• Total Function: For every state q in Q and symbol sigma in Sigma, delta(q, sigma) yields exactly one state.\n"
     "• No Epsilon Transitions: Eliminates non-deterministic ambiguity.\n"
     "• Decision Procedure: Membership testing (w in L(M)) completes in linear time O(|w|).",
     ACCENT_TEAL),
    ("Application to Protocol Sequences",
     "Network protocol traces are formalized as strings w over alphabet Sigma.\n\n"
     "• Alphabet Symbols: Abstract protocol events (CONNECT, REQUEST, AUTH_SUCCESS).\n"
     "• Valid Sessions: Strings recognized by the automaton terminating in F.\n"
     "• Intrusion Detection: Rejection occurs when execution enters TRAP.",
     ACCENT_GOLD)
]

for idx, (title_c, text_c, col_c) in enumerate(toc_cards):
    left = Inches(0.8 + idx * 4.0)
    box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.8), Inches(3.7), Inches(4.8))
    box.fill.solid()
    box.fill.fore_color.rgb = CARD_BG
    box.line.color.rgb = BORDER_COLOR
    tf = box.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title_c
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = col_c
    
    p2 = tf.add_paragraph()
    p2.text = text_c
    p2.font.size = Pt(11)
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(8)

add_notes(s4,
"Let us review the theoretical foundation from our syllabus. Under the Chomsky hierarchy, regular languages are the simplest and most computationally tractable class of languages, recognizable by finite automata. "
"A Deterministic Finite Automaton possesses the memoryless property: all required historical context is encoded into the current state. "
"By treating network event logs as strings of symbols, verifying protocol compliance becomes identical to formal language recognition: deciding whether string w belongs to the regular language L(M)."
)

# ==========================================
# SLIDE 5: Formal 5-Tuple Definition
# ==========================================
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "Formal 5-Tuple Definition: M = (Q, Σ, δ, q₀, F)")

# Top Banner
tb5 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(0.9))
tb5.fill.solid()
tb5.fill.fore_color.rgb = CARD_BG
tb5.line.color.rgb = ACCENT_TEAL
tf5 = tb5.text_frame
p = tf5.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
p.text = "Complete DFA: M = ( Q,  Σ,  δ,  q₀,  F )"
p.font.size = Pt(22)
p.font.bold = True
p.font.color.rgb = ACCENT_TEAL

tuple_items = [
    ("Q (9 States)", "Q = { IDLE, CONNECTED, REQUEST_RECEIVED, AUTH_CHECKED,\n        AUTH_FAILED, RESPONSE_SENT, ERROR, CLOSED, TRAP }\n|Q| = 9 states (including explicit absorbing dead state TRAP).", ACCENT_BLUE),
    ("Σ (13 Event Symbols)", "Σ = { CONNECT, REQUEST, AUTH_SUCCESS, AUTH_FAILURE, RESPONSE_200,\n        RESPONSE_301, RESPONSE_401, RESPONSE_403, RESPONSE_500,\n        CLOSE, TIMEOUT, MALFORMED, ERROR_RESPONSE }   (|Σ| = 13)", ACCENT_TEAL),
    ("δ (Total Transition Function)", "Total Function: δ: Q × Σ → Q\nMatrix Dimension: |Q| × |Σ| = 9 × 13 = 117 explicitly defined entries.\nCompleteness Property: ∀ q ∈ Q, ∀ σ ∈ Σ, δ(q, σ) ∈ Q (No undefined cells).", ACCENT_GOLD),
    ("q₀ and F (Start & Accepting)", "Start State: q₀ = IDLE (Socket initialized, awaiting TCP SYN).\nAccepting Set: F = { CLOSED } (Terminal graceful teardown, TRAP ∉ F).", ACCENT_RED),
]

for idx, (t_title, t_desc, t_col) in enumerate(tuple_items):
    col_idx = idx % 2
    row_idx = idx // 2
    left = Inches(0.8 + col_idx * 6.0)
    top = Inches(2.9 + row_idx * 2.0)
    
    box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(5.7), Inches(1.8))
    box.fill.solid()
    box.fill.fore_color.rgb = CARD_BG
    box.line.color.rgb = BORDER_COLOR
    tf = box.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = t_title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = t_col
    
    p2 = tf.add_paragraph()
    p2.text = t_desc
    p2.font.size = Pt(10.5)
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(4)

add_notes(s5,
"This slide presents the exact formal mathematical 5-tuple of our automaton, matching the implementation in our backend. "
"Notice that Q contains 9 states. In Phase 4, the model had 8 states with partial transitions. In Phase 5, to satisfy the mathematical definition of a complete DFA, we added the TRAP state. "
"Our alphabet Sigma contains 13 protocol symbols. "
"The transition function delta is total, mapping every one of the 9 times 13, or 117 combinations, to a valid state in Q. "
"q0 is IDLE, and F contains only CLOSED."
)

# ==========================================
# SLIDE 6: State Transition Diagram & Topology
# ==========================================
s6 = prs.slides.add_slide(blank_layout)
add_header(s6, "State Transition Topology: Complete 9-State DFA")

flow_box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(3.2))
flow_box.fill.solid()
flow_box.fill.fore_color.rgb = CARD_BG
flow_box.line.color.rgb = BORDER_COLOR
tf = flow_box.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "Protocol Transition Graph Topology:"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = ACCENT_TEAL

diagram_text = (
    "  [ IDLE (q0) ]  --CONNECT-->  [ CONNECTED ]  --REQUEST-->  [ REQUEST_RECEIVED ]\n"
    "                                     |                            |            |\n"
    "                                  TIMEOUT                 AUTH_SUCCESS     AUTH_FAILURE\n"
    "                                     |                            |            |\n"
    "                                     v                            v            v\n"
    "                              [ CLOSED (F) ] <---CLOSE--- [ RESPONSE_SENT ] <--RESP_401/403-- [ AUTH_FAILED ]\n"
    "                                     ^                            ^ \n"
    "                                     |                            | (RESP_200/301)\n"
    "                                  CLOSE                           v\n"
    "                                     |                     [ AUTH_CHECKED ] --RESP_500--> [ ERROR ]\n"
    "                                  [ ERROR ] <---MALFORMED---------'                            |\n"
    "                                     |                                                  ERROR_RESPONSE\n"
    "                                     '---------------------------------------------------------'\n\n"
    "  [ ANY STATE ] -----(Undefined Sequence)-----> [ TRAP (Sink) ] <--(All 13 Symbols Self-Loop)--'"
)
p2 = tf.add_paragraph()
p2.text = diagram_text
p2.font.size = Pt(9.5)
p2.font.name = "Consolas"
p2.font.color.rgb = TEXT_WHITE
p2.space_before = Pt(6)

# Bottom Cards
b1 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.2), Inches(3.7), Inches(1.6))
b1.fill.solid()
b1.fill.fore_color.rgb = CARD_BG
b1.line.color.rgb = BORDER_COLOR
tf1 = b1.text_frame
tf1.word_wrap = True
tf1.paragraphs[0].text = "15 Valid Protocol Transitions"
tf1.paragraphs[0].font.size = Pt(12)
tf1.paragraphs[0].font.bold = True
tf1.paragraphs[0].font.color.rgb = ACCENT_TEAL
p_sub = tf1.add_paragraph()
p_sub.text = "Represent legitimate RFC-compliant operational transactions (handshake, request, auth, response, close)."
p_sub.font.size = Pt(10)
p_sub.font.color.rgb = TEXT_WHITE

b2 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.8), Inches(5.2), Inches(3.7), Inches(1.6))
b2.fill.solid()
b2.fill.fore_color.rgb = CARD_BG
b2.line.color.rgb = BORDER_COLOR
tf2 = b2.text_frame
tf2.word_wrap = True
tf2.paragraphs[0].text = "Keep-Alive Cyclic Loop"
tf2.paragraphs[0].font.size = Pt(12)
tf2.paragraphs[0].font.bold = True
tf2.paragraphs[0].font.color.rgb = ACCENT_BLUE
p_sub2 = tf2.add_paragraph()
p_sub2.text = "RESPONSE_SENT --REQUEST--> REQUEST_RECEIVED allows persistent HTTP connections with unbounded pipelined requests."
p_sub2.font.size = Pt(10)
p_sub2.font.color.rgb = TEXT_WHITE

b3 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), Inches(5.2), Inches(3.7), Inches(1.6))
b3.fill.solid()
b3.fill.fore_color.rgb = CARD_BG
b3.line.color.rgb = BORDER_COLOR
tf3 = b3.text_frame
tf3.word_wrap = True
tf3.paragraphs[0].text = "TRAP Absorbing Sink"
tf3.paragraphs[0].font.size = Pt(12)
tf3.paragraphs[0].font.bold = True
tf3.paragraphs[0].font.color.rgb = ACCENT_RED
p_sub3 = tf3.add_paragraph()
p_sub3.text = "Every illegal protocol transition (76 cells), post-closure events (13 cells), and trap inputs (13 cells) lead to TRAP."
p_sub3.font.size = Pt(10)
p_sub3.font.color.rgb = TEXT_WHITE

add_notes(s6,
"Here we see the structural topology of the protocol automaton. "
"Notice the clear flow: from IDLE through CONNECT, into REQUEST_RECEIVED, branching at authentication. "
"Observe the cycle from RESPONSE_SENT back to REQUEST_RECEIVED via REQUEST, which models HTTP Keep-Alive pipelining. "
"Finally, observe the TRAP state at the bottom. Any transition not explicitly shown on the main highway—such as sending RESPONSE_200 directly from CONNECTED—transitions immediately to TRAP, from which the automaton can never escape."
)

# ==========================================
# SLIDE 7: Step-by-Step Transition Execution
# ==========================================
s7 = prs.slides.add_slide(blank_layout)
add_header(s7, "Step-by-Step Transition Execution: Valid vs. Invalid Traces")

# Column 1: Valid Execution
v_box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0))
v_box.fill.solid()
v_box.fill.fore_color.rgb = CARD_BG
v_box.line.color.rgb = ACCENT_TEAL
v_tf = v_box.text_frame
v_tf.word_wrap = True

vp1 = v_tf.paragraphs[0]
vp1.text = "Example A: Valid Canonical Transaction"
vp1.font.size = Pt(13)
vp1.font.bold = True
vp1.font.color.rgb = ACCENT_TEAL

valid_steps = (
    "Input String w₁ = (CONNECT, REQUEST, AUTH_SUCCESS, RESPONSE_200, CLOSE)\n\n"
    "• Step 1: δ(IDLE, CONNECT) = CONNECTED           [Valid δ]\n"
    "• Step 2: δ(CONNECTED, REQUEST) = REQUEST_RECEIVED [Valid δ]\n"
    "• Step 3: δ(REQUEST_RECEIVED, AUTH_SUCCESS) = AUTH_CHECKED [Valid δ]\n"
    "• Step 4: δ(AUTH_CHECKED, RESPONSE_200) = RESPONSE_SENT    [Valid δ]\n"
    "• Step 5: δ(RESPONSE_SENT, CLOSE) = CLOSED          [Valid δ]\n\n"
    "Final State q = CLOSED ∈ F\n"
    "Formal Classification: ACCEPTED (w₁ ∈ L(M))"
)
vp2 = v_tf.add_paragraph()
vp2.text = valid_steps
vp2.font.size = Pt(10.5)
vp2.font.name = "Consolas"
vp2.font.color.rgb = TEXT_WHITE
vp2.space_before = Pt(8)

# Column 2: Invalid Execution
i_box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0))
i_box.fill.solid()
i_box.fill.fore_color.rgb = CARD_BG
i_box.line.color.rgb = ACCENT_RED
i_tf = i_box.text_frame
i_tf.word_wrap = True

ip1 = i_tf.paragraphs[0]
ip1.text = "Example B: Out-of-Order Exploit (Rejection)"
ip1.font.size = Pt(13)
ip1.font.bold = True
ip1.font.color.rgb = ACCENT_RED

invalid_steps = (
    "Input String w₂ = (CONNECT, RESPONSE_200, REQUEST, CLOSE)\n\n"
    "• Step 1: δ(IDLE, CONNECT) = CONNECTED           [Valid δ]\n"
    "• Step 2: δ(CONNECTED, RESPONSE_200) = TRAP       [REJECTION]\n"
    "  ↳ Reason: Server emitted status before request payload was received!\n"
    "• Step 3: δ(TRAP, REQUEST) = TRAP                [Trapped]\n"
    "• Step 4: δ(TRAP, CLOSE) = TRAP                  [Trapped]\n\n"
    "Final State q = TRAP ∉ F\n"
    "Formal Classification: REJECTED (w₂ ∉ L(M))"
)
ip2 = i_tf.add_paragraph()
ip2.text = invalid_steps
ip2.font.size = Pt(10.5)
ip2.font.name = "Consolas"
ip2.font.color.rgb = TEXT_WHITE
ip2.space_before = Pt(8)

add_notes(s7,
"This slide contrasts two real execution traces evaluated by our backend engine. "
"In Example A, a legitimate HTTP transaction progresses through five valid transitions and halts in CLOSED. Because CLOSED belongs to F, the sequence is accepted. "
"In Example B, an attacker attempts an out-of-order response attack. At Step 2, the server encounters RESPONSE_200 while in CONNECTED. In our complete DFA, delta(CONNECTED, RESPONSE_200) transitions directly to TRAP. "
"Notice Steps 3 and 4: even though REQUEST and CLOSE follow, the automaton remains trapped in TRAP. The string is decisively rejected."
)

# ==========================================
# SLIDE 8: Regular Language Recognition
# ==========================================
s8 = prs.slides.add_slide(blank_layout)
add_header(s8, "Regular Language Recognition: δ*(q₀, w) and Three-Way Classification")

rl_box = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(1.4))
rl_box.fill.solid()
rl_box.fill.fore_color.rgb = CARD_BG
rl_box.line.color.rgb = ACCENT_BLUE
tf = rl_box.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Language Recognized by the Automaton: L(M) = { w ∈ Σ* | δ*(q₀, w) ∈ F }"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = ACCENT_BLUE

p2 = tf.add_paragraph()
p2.text = "Extended Transition Function δ*: Basis: δ*(q, ε) = q.  Inductive step: δ*(q, wa) = δ(δ*(q, w), a) for w ∈ Σ*, a ∈ Σ."
p2.font.size = Pt(11)
p2.font.color.rgb = TEXT_WHITE
p2.space_before = Pt(4)

class_items = [
    ("1. ACCEPTED (w ∈ L(M))",
     "• Every transition is defined and legitimate.\n"
     "• Terminal state δ*(q₀, w) = CLOSED ∈ F.\n"
     "• Example: CONNECT → REQUEST → AUTH_SUCCESS → RESPONSE_200 → CLOSE.\n"
     "• Significance: Fully completed, compliant session.",
     ACCENT_TEAL),
    ("2. INCOMPLETE_VALID (Prefix)",
     "• Every transition executed was valid.\n"
     "• Terminal state δ*(q₀, w) ∉ F (e.g. AUTH_CHECKED).\n"
     "• Empty sequence ε: δ*(q₀, ε) = IDLE ∉ F.\n"
     "• Significance: In-progress session; NOT a security violation.",
     ACCENT_GOLD),
    ("3. REJECTED (w ∉ L(M))",
     "• Encountered an invalid transition.\n"
     "• Automaton entered dead state TRAP (TRAP ∉ F).\n"
     "• Example: CONNECT → RESPONSE_200.\n"
     "• Significance: Proven protocol invariant violation.",
     ACCENT_RED),
]

for idx, (c_title, c_text, c_col) in enumerate(class_items):
    left = Inches(0.8 + idx * 4.0)
    box = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(3.5), Inches(3.7), Inches(3.3))
    box.fill.solid()
    box.fill.fore_color.rgb = CARD_BG
    box.line.color.rgb = c_col
    tf = box.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = c_title
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = c_col
    
    p_body = tf.add_paragraph()
    p_body.text = c_text
    p_body.font.size = Pt(10)
    p_body.font.color.rgb = TEXT_WHITE
    p_body.space_before = Pt(6)

add_notes(s8,
"One of the most important theoretical nuances emphasized in Phase 5 is the distinction between language acceptance and transition validity. "
"We define a strict three-way classification: "
"First, ACCEPTED means every transition was legal and the string finished in an accepting state F. "
"Second, INCOMPLETE_VALID: the string executed valid transitions, but terminated early before reaching F. An empty string epsilon is a classic example: it causes no violation, but IDLE is not in F. Therefore it is an incomplete prefix, not an attack. "
"Third, REJECTED: the execution stepped into TRAP."
)

# ==========================================
# SLIDE 9: System Architecture
# ==========================================
s9 = prs.slides.add_slide(blank_layout)
add_header(s9, "System Implementation Architecture: Triad Detection Pipeline")

arch_box = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(3.2))
arch_box.fill.solid()
arch_box.fill.fore_color.rgb = CARD_BG
arch_box.line.color.rgb = BORDER_COLOR
tf = arch_box.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "End-to-End Operational Pipeline:"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = ACCENT_TEAL

pipeline_text = (
    "  +---------------------------------------------------------------------------------+\n"
    "  |      Network Packet / Session Event Stream (WebSocket Generator / CSV Datasets) |  \n"
    "  +---------------------------------------------------------------------------------+\n"
    "                                           |\n"
    "                     +---------------------+---------------------+\n"
    "                     |                                           |\n"
    "                     v                                           v\n"
    "       +---------------------------+               +---------------------------+\n"
    "       |   Deterministic FSM Engine|               |   15-Feature Extractor    |\n"
    "       |   δ: Q × Σ → Q            |               |   Rates, Ratios, Bytes    |\n"
    "       |   O(1) Step Transition    |               +---------------------------+\n"
    "       +---------------------------+                             |\n"
    "                     | (Risk: 0-100, Violations)                 v\n"
    "                     |                             +---------------------------+\n"
    "                     |                             |   Isolation Forest ML     |\n"
    "                     |                             |   Tree Depth Anomaly Score|\n"
    "                     |                             +---------------------------+\n"
    "                     |                                           | (Score: 0.0 - 1.0)\n"
    "                     +---------------------+---------------------+\n"
    "                                           |\n"
    "                                           v\n"
    "                      +-----------------------------------------+\n"
    "                      |      Hybrid Arbiter Consensus Engine    |\n"
    "                      |   Score = 0.6·FSM + 0.4·ML  (Floor 60.0)|\n"
    "                      +-----------------------------------------+\n"
    "                                           |\n"
    "                                           v\n"
    "                      [ React 19 Automata Lab / Live Dashboard ]"
)
p2 = tf.add_paragraph()
p2.text = pipeline_text
p2.font.size = Pt(8.5)
p2.font.name = "Consolas"
p2.font.color.rgb = TEXT_WHITE
p2.space_before = Pt(4)

tech_specs = [
    ("Backend Core", "FastAPI (Python 3.11), SQLAlchemy, Uvicorn ASGI, Pytest (32/32 Passing).", ACCENT_BLUE),
    ("Frontend Lab", "React 19, Vite, ReactFlow graph visualizer, Tailwind CSS, Lucide icons.", ACCENT_TEAL),
    ("ML Toolchain", "Scikit-Learn IsolationForest, Pandas, NumPy, Joblib model persistence.", ACCENT_GOLD),
]

for idx, (spec_title, spec_desc, spec_col) in enumerate(tech_specs):
    left = Inches(0.8 + idx * 4.0)
    box = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(5.2), Inches(3.7), Inches(1.6))
    box.fill.solid()
    box.fill.fore_color.rgb = CARD_BG
    box.line.color.rgb = BORDER_COLOR
    tf_s = box.text_frame
    tf_s.word_wrap = True
    
    p = tf_s.paragraphs[0]
    p.text = spec_title
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = spec_col
    
    p2 = tf_s.add_paragraph()
    p2.text = spec_desc
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(4)

add_notes(s9,
"This slide illustrates our system architecture. "
"Incoming session events pass concurrently into two parallel pipelines: "
"The left branch feeds the deterministic FSM, which performs delta lookups in constant O(1) step time. "
"The right branch extracts 15 numerical session features and computes an anomaly score using Isolation Forest. "
"The Hybrid Arbiter synthesizes both signals, ensuring that any confirmed FSM violation enforces an immediate risk floor of 60. "
"The entire system is powered by FastAPI on the backend and React 19 on the frontend."
)

# ==========================================
# SLIDE 10: Machine Learning Integration
# ==========================================
s10 = prs.slides.add_slide(blank_layout)
add_header(s10, "Supporting Machine Learning: Unsupervised Isolation Forest")

ml_cards = [
    ("Why Isolation Forest?",
     "• Unsupervised Detection: Does not require labeled attack signatures.\n"
     "• Anomaly Isolation Principle: Anomalies require fewer random axis-aligned splits to isolate than normal points.\n"
     "• Mathematical Scoring: Anomaly score s(x, n) = 2^(-E(h(x)) / c(n)) where h(x) is tree path depth.",
     ACCENT_GOLD),
    ("15 Extracted Session Features",
     "Extracted per session across time windows:\n"
     "• Volumetric: event_count, total_bytes, avg_bytes_per_event.\n"
     "• Temporal: session_duration, inter_arrival_variance.\n"
     "• Error Profiles: error_ratio, auth_failure_count.\n"
     "• Method Distributions: get_ratio, post_ratio, connect_ratio.",
     ACCENT_BLUE),
    ("Role Alongside Formal FSM",
     "• The FSM is the Primary Protocol Guard.\n"
     "• The ML engine is a Supporting Statistical Guard: it catches volumetric floods, password brute-forcing, and anomalous payload spikes that follow legal transitions.\n"
     "• Trained on synthetic baseline traffic profiles.",
     ACCENT_TEAL)
]

for idx, (m_title, m_desc, m_col) in enumerate(ml_cards):
    left = Inches(0.8 + idx * 4.0)
    box = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.8), Inches(3.7), Inches(4.8))
    box.fill.solid()
    box.fill.fore_color.rgb = CARD_BG
    box.line.color.rgb = BORDER_COLOR
    tf = box.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = m_title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = m_col
    
    p2 = tf.add_paragraph()
    p2.text = m_desc
    p2.font.size = Pt(10.5)
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(8)

add_notes(s10,
"Why include Machine Learning in a Theory of Computation project? "
"Because finite automata have a known boundary: if an attacker sends 10,000 valid requests per minute, every single transition is legal, so the FSM generates zero violations. "
"We integrated Isolation Forest as a secondary, supporting detector. It evaluates 15 numerical features such as request frequency, error ratios, and byte distributions. "
"This provides volumetric defense while leaving structural correctness to the automaton."
)

# ==========================================
# SLIDE 11: Detector Comparison
# ==========================================
s11 = prs.slides.add_slide(blank_layout)
add_header(s11, "Multi-Detector Comparison: FSM vs. ML vs. Hybrid")

# Comparison Table
table_shape = s11.shapes.add_table(5, 4, Inches(0.8), Inches(1.8), Inches(11.7), Inches(3.0))
table = table_shape.table
table.columns[0].width = Inches(2.5)
table.columns[1].width = Inches(3.0)
table.columns[2].width = Inches(3.1)
table.columns[3].width = Inches(3.1)

headers = ["Metric / Dimension", "Deterministic FSM", "Isolation Forest ML", "Hybrid Arbiter Engine"]
for i, h in enumerate(headers):
    cell = table.cell(0, i)
    cell.text = h
    cell.fill.solid()
    cell.fill.fore_color.rgb = CARD_BG
    p = cell.text_frame.paragraphs[0]
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = ACCENT_TEAL

rows = [
    ("Detection Basis", "Transition Function δ(q, σ)", "Feature Path Length in Trees", "Composite Risk Synthesis"),
    ("Protocol Violations", "100% Detection (O(1) Step)", "Probabilistic / Inconsistent", "Immediate Critical Alert"),
    ("Volumetric Floods", "Ineffective (Legal Transitions)", "Highly Effective", "Elevated Statistical Risk"),
    ("Explainability", "Exact Causal Proof (Invalid Step)", "Feature Importance Weights", "Root Cause + Statistical Score"),
]

for row_idx, data in enumerate(rows, start=1):
    for col_idx, text in enumerate(data):
        cell = table.cell(row_idx, col_idx)
        cell.text = text
        cell.fill.solid()
        cell.fill.fore_color.rgb = BG_COLOR
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_WHITE if col_idx > 0 else ACCENT_BLUE

# Bottom Formula Card
f_box = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.1), Inches(11.7), Inches(1.7))
f_box.fill.solid()
f_box.fill.fore_color.rgb = CARD_BG
f_box.line.color.rgb = ACCENT_GOLD
tf = f_box.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "Hybrid Consensus Formula & Invariant Risk Floor:"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = ACCENT_GOLD

f_desc = (
    "  Combined Risk = (0.6 × FSM_Score) + (0.4 × ML_Score)\n"
    "  Deterministic Floor Guarantee: If FSM_Violations > 0 ⟹ Combined Risk = max(Combined Risk, 60.0)\n"
    "  Ensures proven structural protocol violations can never be dismissed or diluted by statistical models."
)
p2 = tf.add_paragraph()
p2.text = f_desc
p2.font.size = Pt(10)
p2.font.name = "Consolas"
p2.font.color.rgb = TEXT_WHITE
p2.space_before = Pt(4)

add_notes(s11,
"This comparison matrix highlights the core academic takeaway of our project. "
"The deterministic FSM provides exact causal explanations and guarantees zero false positives for protocol syntax. "
"Isolation Forest provides probabilistic coverage for volumetric attacks. "
"The Hybrid Arbiter unites them: if the FSM detects an invalid transition, the risk floor automatically elevates the score to at least 60, ensuring mathematical safety invariants are never compromised."
)

# ==========================================
# SLIDE 12: Automata Laboratory Demonstration
# ==========================================
s12 = prs.slides.add_slide(blank_layout)
add_header(s12, "Interactive Automata Laboratory: Demonstration Capabilities")

lab_features = [
    ("Interactive Graph Visualizer", 
     "• Live ReactFlow canvas rendering all 9 states and directed edges.\n"
     "• Real-time active state glow, animated transitions, and dashed q₀/gold F borders.\n"
     "• Visual TRAP node displaying unrecoverable violation paths.",
     ACCENT_TEAL),
    ("Step-by-Step Transition Debugger",
     "• Step forward, backward, pause, and reset controls.\n"
     "• Inspects δ(q, σ) lookups and natural language explanations for every step.\n"
     "• Invariant auditing: immediately catches out-of-order and unauthorized packets.",
     ACCENT_BLUE),
    ("Complete Transition Matrix Explorer",
     "• 117-cell interactive matrix covering Q × Σ.\n"
     "• Instant search and state filtering.\n"
     "• Verifies total completeness proof directly in the browser UI.",
     ACCENT_GOLD),
    ("Automaton Edge-Case Test Suite",
     "• One-click presets for canonical flows, pipelined keep-alive loops, 401/403 exceptions, and malformed request traps.\n"
     "• Real-time classification: ACCEPTED vs. INCOMPLETE_VALID vs. REJECTED.",
     ACCENT_RED),
]

for idx, (l_title, l_desc, l_col) in enumerate(lab_features):
    col_idx = idx % 2
    row_idx = idx // 2
    left = Inches(0.8 + col_idx * 6.0)
    top = Inches(1.8 + row_idx * 2.6)
    
    box = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(5.7), Inches(2.3))
    box.fill.solid()
    box.fill.fore_color.rgb = CARD_BG
    box.line.color.rgb = BORDER_COLOR
    tf = box.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = l_title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = l_col
    
    p2 = tf.add_paragraph()
    p2.text = l_desc
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(6)

add_notes(s12,
"In our live demonstration following these slides, we will navigate to the Automata Laboratory at /automata. "
"The laboratory provides an interactive ReactFlow graph visualizer, a step-by-step transition debugger, the complete 117-cell transition matrix, and a test suite of preset sequences. "
"This allows examiners to construct arbitrary event sequences and observe the extended transition function execute live."
)

# ==========================================
# SLIDE 13: Limitations & Future Scope
# ==========================================
s13 = prs.slides.add_slide(blank_layout)
add_header(s13, "Academic Limitations & Realistic Future Scope")

lim_cards = [
    ("Current Scope & Academic Limitations",
     "• Synthetic Datasets: Generated synthetically to model HTTP session flows and attacks. Does not reflect multi-gigabit carrier traffic.\n"
     "• Simplified Protocol Abstraction: Models session sequencing (connect, auth, response, close); does not parse raw TCP flags or HTTP/2 multiplexed binary frames.\n"
     "• Educational Demonstration: Engineered for academic defense and algorithmic clarity rather than commercial deployment.",
     ACCENT_RED),
    ("Realistic Future Scope",
     "• Stack-Based Computation (Pushdown Automata): Parse context-free payload structures, such as validating balanced nested JSON or recursive XML delimiters (aⁿbⁿ).\n"
     "• Concurrency & Interleaving Semantics: Model concurrent multi-stream protocols (e.g. multiplexed HTTP/2 or WebSocket channels) using product-state transition systems.\n"
     "• Multi-Protocol State Machines: Expand formal automata beyond HTTP to TLS cryptographic handshakes and SSH session models.",
     ACCENT_BLUE),
]

for idx, (title_text, body_text, col_accent) in enumerate(lim_cards):
    left = Inches(0.8 + idx * 6.0)
    box = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.8), Inches(5.7), Inches(4.8))
    box.fill.solid()
    box.fill.fore_color.rgb = CARD_BG
    box.line.color.rgb = BORDER_COLOR
    tf = box.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = col_accent
    
    p2 = tf.add_paragraph()
    p2.text = body_text
    p2.font.size = Pt(11)
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(8)

add_notes(s13,
"In the interest of academic honesty and scientific rigor, we explicitly document our limitations. "
"TraceGuard AI is an educational prototype. We used synthetic datasets to model known protocol flows, and our HTTP state machine models session sequencing rather than full RFC 7230 header parsing. "
"For future work, higher-order automata like Pushdown Automata could be used to validate context-free payloads like nested balanced JSON, while product-state transition systems could model concurrent multi-stream protocol interleaving."
)

# ==========================================
# SLIDE 14: Conclusion
# ==========================================
s14 = prs.slides.add_slide(blank_layout)
add_header(s14, "Conclusion & Key Academic Contributions")

concl_box = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8))
concl_box.fill.solid()
concl_box.fill.fore_color.rgb = CARD_BG
concl_box.line.color.rgb = ACCENT_TEAL
tf = concl_box.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "Key Project Takeaways:"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = ACCENT_TEAL

concl_text = (
    "1. Automata Theory as an Engineering Tool:\n"
    "   Finite-state machines are not merely textbook mathematical exercises; they represent an unmatched formalism for enforcing protocol sequence invariants with zero false positives.\n\n"
    "2. Mathematical Rigor in Software Design:\n"
    "   By formalizing a complete 9-state DFA with 117 total transition mappings, the system guarantees determinism and complete language decidability in O(1) step time.\n\n"
    "3. The Symbiosis of Rules and Machine Learning:\n"
    "   Deterministic automata provide mathematical proofs of violation, while statistical models provide volumetric anomaly profiling. Hybrid architectures unite the best of both paradigms.\n\n"
    "4. Reproducibility & Integrity:\n"
    "   Verified with 32 automated tests, zero test failures, an interactive visualizer, and open documentation."
)
p2 = tf.add_paragraph()
p2.text = concl_text
p2.font.size = Pt(11.5)
p2.font.color.rgb = TEXT_WHITE
p2.space_before = Pt(10)

p3 = tf.add_paragraph()
p3.text = "Thank you. I am now ready for questions and the live demonstration."
p3.font.size = Pt(13)
p3.font.bold = True
p3.font.color.rgb = ACCENT_GOLD
p3.space_before = Pt(16)

add_notes(s14,
"To conclude: TraceGuard AI demonstrates that Theory of Computation principles are fundamental to robust software and cybersecurity engineering. "
"Finite automata provide mathematical proof of protocol compliance that statistical learning cannot match alone, while hybrid consensus bridges the gap between deterministic structure and statistical variance. "
"Thank you for your time and attention. I am now delighted to take your questions and demonstrate the live Automata Laboratory."
)

# Save presentation
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "presentation", "TraceGuard_AI_TOC_Presentation.pptx"))
prs.save(output_path)
print(f"Successfully generated PowerPoint presentation with {len(prs.slides)} slides at: {output_path}")
