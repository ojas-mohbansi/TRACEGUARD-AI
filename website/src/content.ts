/*
  TraceGuard AI — Master Content Specification
  Academic Research Prototype: Formal HTTP Protocol DFA + Isolation Forest Machine Learning
  All metrics and statements strictly verified against backend/app and formal documentation.
*/

export const brand = {
  name: 'TraceGuard AI',
  short: 'TraceGuard',
  tagline: 'Formal protocol verification meets machine-learning anomaly detection.',
  course: 'Theory of Computation / Formal Languages and Automata Theory',
  department: 'Department of Computer Science & Engineering',
  academicYear: '2026',
  email: 'research@traceguard.academic',
  github: 'https://github.com/ojas-mohbansi/TRACEGUARD-AI',
}

export const nav = [
  { label: 'Technology', href: '/technology' },
  { label: 'Automaton Lab', href: '/automaton' },
  { label: 'Architecture', href: '/architecture' },
  { label: 'Research', href: '/research' },
  { label: 'Defense Deck', href: '/presentation' },
  { label: 'Academic Context', href: '/about' },
]

export const cta = { label: 'Automaton Lab', href: '/automaton' }

export const hero = {
  eyebrow: 'Theory of Computation · Capstone Research 2026',
  title: ['Detect threats with', 'formal protocol logic'],
  body: 'TraceGuard AI bridges mathematical language theory with network security by combining a deterministic 9-state HTTP protocol automaton with Isolation Forest machine learning to eliminate state-order bypasses and volumetric anomalies.',
  primary: { label: 'Explore Automaton', href: '/automaton' },
  secondary: { label: 'System Architecture', href: '/architecture' },
  stats: [
    { value: '9', unit: '', label: 'DFA States (1 Sink)' },
    { value: '13', unit: '', label: 'Input Symbols |Σ|' },
    { value: '117', unit: '', label: 'Total Transition Matrix' },
  ],
}

export const problem = {
  eyebrow: 'The State Blindspot in Network Security',
  title: ['Why signature scanners & black-box models', 'fail stateful protocols'],
  body: 'Application protocols like HTTP are fundamentally stateful machines. Attackers exploit sequence manipulation — injecting responses before authentication or accessing endpoints without handshakes. Neither packet-level regex nor deep-learning black boxes can formally prove whether a session is legal.',
  cards: [
    {
      id: 'out-of-order',
      title: 'Out-of-Order Execution',
      body: 'Authentication bypass and response injection exploit legal individual packets arriving in illegal order. Invisible to stateless packet inspection.',
      tag: 'Order Violation',
    },
    {
      id: 'state-injection',
      title: 'State Hijacking & Skipping',
      body: 'Attackers manipulate session tokens to skip handshake checkpoints. Signature databases miss novel sequence mutations that violate grammar.',
      tag: 'Semantic Bypass',
    },
    {
      id: 'black-box-opacity',
      title: 'Explainability Deficit',
      body: 'Neural anomaly detectors output uninterpretable probabilities. Incident response teams require constructive formal proofs of protocol violation.',
      tag: 'Zero Provenance',
    },
  ],
}

export const automatonSummary = {
  eyebrow: 'Formal Automaton Specification',
  title: 'Deterministic Finite Automaton M = (Q, Σ, δ, q₀, F)',
  body: 'TraceGuard AI models the complete HTTP session lifecycle as a Total Complete DFA. Every state-symbol pair has an explicit transition, providing deterministic O(1) step execution with zero ambiguity.',
  tuple: [
    { symbol: 'Q', name: 'State Space', detail: '9 States: IDLE, CONNECTED, REQUEST_RECEIVED, AUTH_CHECKED, AUTH_FAILED, RESPONSE_SENT, ERROR, CLOSED, TRAP' },
    { symbol: 'Σ', name: 'Input Alphabet', detail: '13 Symbols: CONNECT, REQUEST, AUTH_SUCCESS, AUTH_FAILURE, RESPONSE_200, RESPONSE_301, RESPONSE_401, RESPONSE_403, RESPONSE_500, CLOSE, TIMEOUT, MALFORMED, ERROR_RESPONSE' },
    { symbol: 'δ', name: 'Transition Function', detail: 'δ: Q × Σ → Q (117 total cells: 15 valid protocol edges, 102 routing directly to absorbing TRAP sink)' },
    { symbol: 'q₀', name: 'Initial State', detail: 'IDLE (Quiescent baseline before TCP session establishment)' },
    { symbol: 'F', name: 'Accepting States', detail: '{CLOSED} (Terminal clean connection teardown)' },
  ],
  statesList: [
    { id: 'IDLE', label: 'IDLE', type: 'initial', desc: 'Initial quiescent state awaiting client TCP handshake' },
    { id: 'CONNECTED', label: 'CONNECTED', type: 'operational', desc: 'TCP connection active; awaiting HTTP request' },
    { id: 'REQUEST_RECEIVED', label: 'REQUEST_RECEIVED', type: 'operational', desc: 'HTTP request headers received; awaiting auth validation' },
    { id: 'AUTH_CHECKED', label: 'AUTH_CHECKED', type: 'operational', desc: 'Credentials verified successfully; processing response' },
    { id: 'AUTH_FAILED', label: 'AUTH_FAILED', type: 'operational', desc: 'Authentication failed; dispatching 401/403' },
    { id: 'RESPONSE_SENT', label: 'RESPONSE_SENT', type: 'operational', desc: 'Server response dispatched; connection reusable or closing' },
    { id: 'ERROR', label: 'ERROR', type: 'operational', desc: 'Malformed protocol syntax or 500 server error' },
    { id: 'CLOSED', label: 'CLOSED', type: 'final', desc: 'Clean connection termination; formal accepting state' },
    { id: 'TRAP', label: 'TRAP', type: 'sink', desc: 'Absorbing dead state for all undefined transitions' },
  ],
  validTransitions: [
    { from: 'IDLE', symbol: 'CONNECT', to: 'CONNECTED' },
    { from: 'CONNECTED', symbol: 'REQUEST', to: 'REQUEST_RECEIVED' },
    { from: 'CONNECTED', symbol: 'TIMEOUT', to: 'CLOSED' },
    { from: 'REQUEST_RECEIVED', symbol: 'AUTH_SUCCESS', to: 'AUTH_CHECKED' },
    { from: 'REQUEST_RECEIVED', symbol: 'AUTH_FAILURE', to: 'AUTH_FAILED' },
    { from: 'REQUEST_RECEIVED', symbol: 'MALFORMED', to: 'ERROR' },
    { from: 'AUTH_CHECKED', symbol: 'RESPONSE_200', to: 'RESPONSE_SENT' },
    { from: 'AUTH_CHECKED', symbol: 'RESPONSE_301', to: 'RESPONSE_SENT' },
    { from: 'AUTH_CHECKED', symbol: 'RESPONSE_500', to: 'ERROR' },
    { from: 'AUTH_FAILED', symbol: 'RESPONSE_401', to: 'RESPONSE_SENT' },
    { from: 'AUTH_FAILED', symbol: 'RESPONSE_403', to: 'RESPONSE_SENT' },
    { from: 'RESPONSE_SENT', symbol: 'REQUEST', to: 'REQUEST_RECEIVED' },
    { from: 'RESPONSE_SENT', symbol: 'CLOSE', to: 'CLOSED' },
    { from: 'ERROR', symbol: 'CLOSE', to: 'CLOSED' },
    { from: 'ERROR', symbol: 'ERROR_RESPONSE', to: 'RESPONSE_SENT' },
  ],
  classifications: [
    {
      status: 'ACCEPTED',
      formal: 'δ*(q₀, w) ∈ F',
      description: 'Session terminated cleanly at CLOSED state without protocol errors.',
      score: '0 Risk Score',
      tone: 'ok',
    },
    {
      status: 'INCOMPLETE_VALID',
      formal: 'δ*(q₀, w) ∉ F ∧ δ*(q₀, w) ≠ TRAP',
      description: 'All transitions valid but connection remains open or unclosed.',
      score: '30 Risk Score',
      tone: 'warn',
    },
    {
      status: 'REJECTED',
      formal: 'δ*(q₀, w) = TRAP',
      description: 'Illegal protocol transition triggered absorbing sink state.',
      score: '60–100 Risk Score',
      tone: 'threat',
    },
  ],
}

export const hybridEngine = {
  eyebrow: 'Dual-Engine Architecture',
  title: 'Deterministic DFA Verification + Statistical Isolation Forest',
  body: 'The DFA guarantees zero false positives on protocol syntax rules, while Isolation Forest identifies anomalous session metrics across 15 behavioral dimensions.',
  formula: {
    equation: 'S_h = (0.6 × S_FSM) + (0.4 × S_ML)',
    floorRule: 'if fsm_violation then S_h = max(S_h, 60.0)',
    weights: [
      { label: 'FSM Weight', value: '0.6 (60%)', note: 'Rigorous deterministic grammar priority' },
      { label: 'ML Weight', value: '0.4 (40%)', note: 'Unsupervised volumetric anomaly scoring' },
      { label: 'Safety Floor', value: '60.0 Minimum', note: 'Guarantees High alert severity on any state violation' },
    ],
  },
  features: [
    { category: 'Timing Metrics', items: ['session_duration_seconds', 'avg_inter_event_time', 'std_inter_event_time'] },
    { category: 'Volume & Rate', items: ['event_count', 'avg_bytes', 'request_rate'] },
    { category: 'Event Diversity', items: ['unique_event_types', 'unique_methods', 'has_close'] },
    { category: 'State & Error Counts', items: ['invalid_transition_count', 'auth_failure_count', 'error_count'] },
    { category: 'Status Ratios', items: ['response_2xx_ratio', 'response_4xx_ratio', 'response_5xx_ratio'] },
  ],
  quadrants: [
    { name: 'Quadrant A: Normal', fsm: 'Valid Sequence', ml: 'Normal Distribution', risk: 'Risk < 40', verdict: 'Clean Traffic' },
    { name: 'Quadrant B: FSM Violation', fsm: 'Syntax/Order Break', ml: 'Low Volumetric Anomaly', risk: 'Risk ≥ 60 (Floor)', verdict: 'Targeted Protocol Attack' },
    { name: 'Quadrant C: ML Outlier', fsm: 'Grammar Conforming', ml: 'High Statistical Deviance', risk: 'Elevated Risk', verdict: 'Volumetric / Brute-Force' },
    { name: 'Quadrant D: Combined Alert', fsm: 'Syntax Break', ml: 'High Deviance', risk: 'Risk 80–100', verdict: 'Critical Multi-Stage Threat' },
  ],
}

export const pipeline = {
  eyebrow: 'Real-Time Ingestion & Processing',
  title: '8-Stage Sequential Detection Pipeline',
  stages: [
    { step: '01', name: 'Event Ingestion', desc: 'Streaming WebSocket (/ws/events) and batch REST upload (/api/datasets/upload).' },
    { step: '02', name: 'Session Aggregation', desc: 'Windowed session grouping by session_id preserving chronological order.' },
    { step: '03', name: 'FSM Verification (Tier 1)', desc: 'O(1) DFA transition verification; invalid transitions route to TRAP sink.' },
    { step: '04', name: 'Feature Extraction', desc: '15 session-level temporal, volumetric, and ratio features computed in-memory.' },
    { step: '05', name: 'Isolation Forest (Tier 2)', desc: 'Unsupervised 100-tree ensemble generates normalized anomaly score [0.0, 1.0].' },
    { step: '06', name: 'Hybrid Consensus (Tier 3)', desc: 'Weighted fusion S_h = 0.6 S_FSM + 0.4 S_ML with enforced 60% violation floor.' },
    { step: '07', name: 'Alert Storage', desc: 'SQLite persistence via SQLAlchemy ORM with full violation proof and audit trail.' },
    { step: '08', name: 'Telemetry Broadcast', desc: 'Live event dispatch to React dashboard with interactive state machine graph.' },
  ],
}

export const research = {
  eyebrow: 'Evaluation & Benchmark Methodology',
  title: 'Corpus Attribution & Transparent Academic Limits',
  attributionData: [
    { label: 'Hybrid Consensus', percent: '57.14%', count: '4/7 Alert Events', desc: 'Both FSM and ML flagged the incident concurrently.' },
    { label: 'FSM-Only Attribution', percent: '28.57%', count: '2/7 Alert Events', desc: 'Subtle sequence order violations invisible to ML volume scoring.' },
    { label: 'ML-Only Attribution', percent: '14.29%', count: '1/7 Alert Events', desc: 'High-frequency brute force attacks that follow valid HTTP grammar.' },
    { label: 'Unexplained Alerts', percent: '0.00%', count: '0/7 Alert Events', desc: 'Every alert maintains direct causal mathematical attribution.' },
  ],
  benchmarks: {
    note: 'Evaluated on controlled synthetic corpus (600 sessions, seed=42) per academic protocol standard.',
    metrics: [
      { label: 'Synthetic Training Set', value: '480 sessions', detail: 'Normal & anomalous distribution' },
      { label: 'Synthetic Test Set', value: '120 sessions', detail: 'Zero-leakage test validation' },
      { label: 'Model F1-Score', value: '0.5312', detail: 'Synthetic benchmark evaluation' },
      { label: 'Zero-Day Detection Rate', value: '68.0%', detail: 'Novel syntactic mutations detected via DFA' },
      { label: 'Pass Rate in CI', value: '149 / 149', detail: 'Unit, integration, and security tests' },
    ],
  },
  limitations: [
    {
      title: 'Regular Language Boundary',
      desc: 'DFA recognizes Type-3 regular grammars. HTTP payloads with recursive nested structures (deep JSON/XML) require Pushdown Automata.',
    },
    {
      title: 'Synthetic Training Baselines',
      desc: 'All ML benchmarks are computed on synthesized sessions. Live production deployment requires retraining on empirical enterprise traffic.',
    },
    {
      title: 'Markovian Ingestion Layer',
      desc: 'Traffic enters via simulated generators or formatted JSON/CSV uploads rather than direct raw promiscuous libpcap socket binding.',
    },
    {
      title: 'Single-Tenant SQLite Store',
      desc: 'Persistence architecture uses SQLite for local research inspection rather than distributed multi-region databases.',
    },
  ],
}

export const defense = {
  eyebrow: 'Oral Defense & Project Report',
  title: 'Theory of Computation Capstone Defense',
  summary: 'Complete academic presentation materials prepared for institutional committee evaluation and technical viva examination.',
  stats: [
    { value: '22', label: 'Slide Deck Panels' },
    { value: '13m 30s', label: 'Allocated Defense Time' },
    { value: '5', label: 'Presenter Rotations' },
    { value: '149/149', label: 'Automated Tests Passing' },
  ],
  speakers: [
    { role: 'Speaker 1 (0:00 - 2:30)', topic: 'Motivation, Threat Landscape, and Chomsky Hierarchy Placement' },
    { role: 'Speaker 2 (2:30 - 5:15)', topic: 'Formal 5-Tuple Definition, DFA Completeness, and TRAP State Proof' },
    { role: 'Speaker 3 (5:15 - 8:00)', topic: 'Isolation Forest Anomaly Detection, 15 Features, and ML Normalization' },
    { role: 'Speaker 4 (8:00 - 10:45)', topic: 'Hybrid Consensus Formula, 60% Safety Floor, and Live Architecture' },
    { role: 'Speaker 5 (10:45 - 13:30)', topic: 'Corpus Evaluation, Academic Limitations, and Committee Q&A' },
  ],
  documents: [
    { title: 'FORMAL_AUTOMATON.md', desc: 'Rigorous 5-tuple specification and completeness proof' },
    { title: 'TRANSITION_TABLE.md', desc: 'Exhaustive 9 × 13 transition matrix enumeration' },
    { title: 'TOC_THEORY.md', desc: 'Chomsky regular language classification and Myhill-Nerode context' },
    { title: 'ALGORITHM_EXPLANATION.md', desc: 'Mathematical derivation of hybrid consensus and anomaly score scaling' },
    { title: 'PROJECT_REPORT.md', desc: 'Comprehensive academic research manuscript and test benchmarks' },
    { title: 'VIVA_PREPARATION.md', desc: 'Defense guide with anticipated examiner questions and answers' },
  ],
}

export const about = {
  eyebrow: 'Institutional Affiliation',
  title: 'Academic Context & Research Scope',
  body: 'TraceGuard AI is an academic capstone research project developed under the curriculum of Theory of Computation and Formal Languages & Automata Theory. Built to demonstrate that abstract automata theory can serve as a high-performance, deterministic first-line defense in cybersecurity systems.',
  metadata: [
    { label: 'Curriculum Course', value: 'Theory of Computation / Formal Languages and Automata Theory' },
    { label: 'Department', value: 'Department of Computer Science & Engineering' },
    { label: 'Academic Term', value: 'Academic Year 2026' },
    { label: 'Project Classification', value: 'Capstone Research Prototype' },
    { label: 'Implementation License', value: 'Open Academic Research (MIT)' },
  ],
}

export const footer = {
  blurb: 'Academic cybersecurity research prototype demonstrating formal DFA HTTP protocol verification combined with Isolation Forest anomaly detection.',
  disclaimer: 'TraceGuard AI is an academic research prototype developed for educational and experimental evaluation. Not a commercial perimeter defense system.',
  columns: [
    {
      title: 'System',
      links: [
        { label: 'Technology', href: '/technology' },
        { label: 'Automaton Lab', href: '/automaton' },
        { label: 'Architecture', href: '/architecture' },
      ],
    },
    {
      title: 'Research',
      links: [
        { label: 'Research & Corpus', href: '/research' },
        { label: 'Defense Presentation', href: '/presentation' },
        { label: 'Academic Context', href: '/about' },
      ],
    },
    {
      title: 'Documentation',
      links: [
        { label: 'GitHub Repository', href: 'https://github.com/ojas-mohbansi/TRACEGUARD-AI' },
        { label: 'Design Tokens', href: '/styleguide' },
      ],
    },
  ],
  copyright: '© 2026 TraceGuard AI Academic Research Project · Department of Computer Science & Engineering',
}

export const notFound = {
  title: 'Protocol State: TRAP',
  body: 'The requested route does not exist in the navigation automaton. Returning to quiescent state (IDLE).',
}
