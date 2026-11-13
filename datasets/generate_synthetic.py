"""
Synthetic dataset generator for TraceGuard AI.
Generates 500+ realistic sessions (70% normal, 30% anomalous) with seed 42.
Saves:
- datasets/synthetic/training_data.csv
- datasets/synthetic/test_data.csv
- datasets/synthetic/unseen_templates.csv
"""
import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Ensure deterministic generation
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

CSV_COLUMNS = [
    "event_id",
    "session_id",
    "timestamp",
    "protocol",
    "event_type",
    "source",
    "destination",
    "method",
    "path_category",
    "status_code",
    "bytes",
    "label",
]

CLIENT_IPS = [f"192.168.1.{i}" for i in range(10, 50)] + [f"10.0.0.{i}" for i in range(2, 30)]
SERVER_IPS = ["10.0.1.100", "10.0.1.101", "172.16.0.50"]
PATHS_AUTH = ["/api/v1/auth/login", "/api/v1/auth/token", "/login"]
PATHS_API = ["/api/v1/users", "/api/v1/metrics", "/api/v1/data", "/api/v1/reports", "/api/v1/settings"]
PATHS_STATIC = ["/static/app.js", "/static/style.css", "/assets/logo.png"]


class SessionGenerator:
    def __init__(self, start_time: datetime):
        self.current_time = start_time
        self.event_counter = 0

    def next_event_id(self) -> str:
        self.event_counter += 1
        return f"evt_{self.event_counter:07d}"

    def generate_event(
        self,
        session_id: str,
        event_type: str,
        source: str,
        destination: str,
        method: str = None,
        path_category: str = None,
        status_code: int = None,
        byte_count: int = 0,
        label: str = "normal",
        delta_seconds: float = 0.5,
    ) -> dict:
        self.current_time += timedelta(seconds=max(0.01, delta_seconds))
        return {
            "event_id": self.next_event_id(),
            "session_id": session_id,
            "timestamp": self.current_time.isoformat(),
            "protocol": "HTTP",
            "event_type": event_type,
            "source": source,
            "destination": destination,
            "method": method,
            "path_category": path_category,
            "status_code": status_code,
            "bytes": byte_count,
            "label": label,
        }

    # ================= NORMAL TEMPLATES =================
    def template_normal_successful(self, session_id: str, client_ip: str, server_ip: str) -> list:
        """Standard successful HTTP session: CONNECT -> REQUEST -> AUTH_SUCCESS -> RESPONSE_200 -> CLOSE"""
        events = []
        path = random.choice(PATHS_API)
        events.append(self.generate_event(session_id, "CONNECT", client_ip, server_ip, byte_count=64, delta_seconds=random.uniform(0.1, 0.5)))
        events.append(self.generate_event(session_id, "REQUEST", client_ip, server_ip, method="GET", path_category=path, byte_count=random.randint(200, 500), delta_seconds=random.uniform(0.05, 0.2)))
        events.append(self.generate_event(session_id, "AUTH_SUCCESS", client_ip, server_ip, byte_count=0, delta_seconds=random.uniform(0.01, 0.05)))
        events.append(self.generate_event(session_id, "RESPONSE_200", server_ip, client_ip, status_code=200, byte_count=random.randint(1000, 5000), delta_seconds=random.uniform(0.05, 0.3)))
        events.append(self.generate_event(session_id, "CLOSE", client_ip, server_ip, byte_count=32, delta_seconds=random.uniform(0.1, 0.4)))
        return events

    def template_normal_redirect(self, session_id: str, client_ip: str, server_ip: str) -> list:
        """Redirect session: CONNECT -> REQUEST -> AUTH_SUCCESS -> RESPONSE_301 -> CLOSE"""
        events = []
        events.append(self.generate_event(session_id, "CONNECT", client_ip, server_ip, byte_count=64, delta_seconds=random.uniform(0.1, 0.4)))
        events.append(self.generate_event(session_id, "REQUEST", client_ip, server_ip, method="GET", path_category="/old-path", byte_count=random.randint(150, 300), delta_seconds=random.uniform(0.05, 0.2)))
        events.append(self.generate_event(session_id, "AUTH_SUCCESS", client_ip, server_ip, byte_count=0, delta_seconds=random.uniform(0.01, 0.05)))
        events.append(self.generate_event(session_id, "RESPONSE_301", server_ip, client_ip, status_code=301, byte_count=random.randint(300, 600), delta_seconds=random.uniform(0.05, 0.2)))
        events.append(self.generate_event(session_id, "CLOSE", client_ip, server_ip, byte_count=32, delta_seconds=random.uniform(0.1, 0.3)))
        return events

    def template_normal_keepalive(self, session_id: str, client_ip: str, server_ip: str) -> list:
        """Keep-alive with multiple requests on single connection: CONNECT -> REQ -> AUTH -> 200 -> REQ -> AUTH -> 200 -> CLOSE"""
        events = []
        events.append(self.generate_event(session_id, "CONNECT", client_ip, server_ip, byte_count=64, delta_seconds=random.uniform(0.1, 0.5)))
        n_reqs = random.randint(2, 4)
        for _ in range(n_reqs):
            path = random.choice(PATHS_API + PATHS_STATIC)
            method = random.choice(["GET", "POST"])
            events.append(self.generate_event(session_id, "REQUEST", client_ip, server_ip, method=method, path_category=path, byte_count=random.randint(250, 700), delta_seconds=random.uniform(0.1, 0.8)))
            events.append(self.generate_event(session_id, "AUTH_SUCCESS", client_ip, server_ip, byte_count=0, delta_seconds=random.uniform(0.01, 0.05)))
            events.append(self.generate_event(session_id, "RESPONSE_200", server_ip, client_ip, status_code=200, byte_count=random.randint(800, 4000), delta_seconds=random.uniform(0.05, 0.3)))
        events.append(self.generate_event(session_id, "CLOSE", client_ip, server_ip, byte_count=32, delta_seconds=random.uniform(0.2, 0.5)))
        return events

    def template_normal_auth_retry(self, session_id: str, client_ip: str, server_ip: str) -> list:
        """Auth retry: CONNECT -> REQUEST -> AUTH_FAILURE -> RESPONSE_401 -> CLOSE"""
        events = []
        path = random.choice(PATHS_AUTH)
        events.append(self.generate_event(session_id, "CONNECT", client_ip, server_ip, byte_count=64, delta_seconds=random.uniform(0.1, 0.3)))
        events.append(self.generate_event(session_id, "REQUEST", client_ip, server_ip, method="POST", path_category=path, byte_count=random.randint(300, 600), delta_seconds=random.uniform(0.05, 0.2)))
        events.append(self.generate_event(session_id, "AUTH_FAILURE", client_ip, server_ip, byte_count=0, delta_seconds=random.uniform(0.02, 0.08)))
        events.append(self.generate_event(session_id, "RESPONSE_401", server_ip, client_ip, status_code=401, byte_count=random.randint(200, 400), delta_seconds=random.uniform(0.05, 0.2)))
        events.append(self.generate_event(session_id, "CLOSE", client_ip, server_ip, byte_count=32, delta_seconds=random.uniform(0.1, 0.3)))
        return events

    def template_normal_timeout(self, session_id: str, client_ip: str, server_ip: str) -> list:
        """Inactivity timeout: CONNECT -> TIMEOUT"""
        events = []
        events.append(self.generate_event(session_id, "CONNECT", client_ip, server_ip, byte_count=64, delta_seconds=random.uniform(0.1, 0.5)))
        events.append(self.generate_event(session_id, "TIMEOUT", server_ip, client_ip, byte_count=0, delta_seconds=random.uniform(15.0, 30.0)))
        return events

    # ================= ANOMALOUS TEMPLATES =================
    def template_anom_skipped_auth(self, session_id: str, client_ip: str, server_ip: str) -> list:
        """Skipped auth: CONNECT -> REQUEST -> RESPONSE_200 (violates FSM REQUEST_RECEIVED -> RESPONSE_200)"""
        events = []
        events.append(self.generate_event(session_id, "CONNECT", client_ip, server_ip, byte_count=64, delta_seconds=random.uniform(0.1, 0.3), label="anomalous"))
        events.append(self.generate_event(session_id, "REQUEST", client_ip, server_ip, method="GET", path_category="/admin/secrets", byte_count=random.randint(200, 450), delta_seconds=random.uniform(0.05, 0.1), label="anomalous"))
        events.append(self.generate_event(session_id, "RESPONSE_200", server_ip, client_ip, status_code=200, byte_count=random.randint(2000, 8000), delta_seconds=random.uniform(0.05, 0.2), label="anomalous"))
        events.append(self.generate_event(session_id, "CLOSE", client_ip, server_ip, byte_count=32, delta_seconds=random.uniform(0.1, 0.3), label="anomalous"))
        return events

    def template_anom_out_of_order(self, session_id: str, client_ip: str, server_ip: str) -> list:
        """Out of order: REQUEST sent before CONNECT: REQUEST -> CONNECT -> RESPONSE_200 -> CLOSE"""
        events = []
        events.append(self.generate_event(session_id, "REQUEST", client_ip, server_ip, method="POST", path_category="/data/upload", byte_count=random.randint(1000, 3000), delta_seconds=random.uniform(0.05, 0.1), label="anomalous"))
        events.append(self.generate_event(session_id, "CONNECT", client_ip, server_ip, byte_count=64, delta_seconds=random.uniform(0.05, 0.1), label="anomalous"))
        events.append(self.generate_event(session_id, "AUTH_SUCCESS", client_ip, server_ip, byte_count=0, delta_seconds=random.uniform(0.02, 0.05), label="anomalous"))
        events.append(self.generate_event(session_id, "RESPONSE_200", server_ip, client_ip, status_code=200, byte_count=random.randint(500, 1500), delta_seconds=random.uniform(0.05, 0.2), label="anomalous"))
        events.append(self.generate_event(session_id, "CLOSE", client_ip, server_ip, byte_count=32, delta_seconds=random.uniform(0.1, 0.3), label="anomalous"))
        return events

    def template_anom_repeated_errors(self, session_id: str, client_ip: str, server_ip: str) -> list:
        """Brute-force / repeated errors: CONNECT -> multiple (REQUEST -> AUTH_FAILURE -> RESPONSE_401) without proper close or exceeding limits"""
        events = []
        events.append(self.generate_event(session_id, "CONNECT", client_ip, server_ip, byte_count=64, delta_seconds=random.uniform(0.1, 0.3), label="anomalous"))
        for _ in range(random.randint(5, 8)):
            events.append(self.generate_event(session_id, "REQUEST", client_ip, server_ip, method="POST", path_category="/login", byte_count=random.randint(250, 400), delta_seconds=random.uniform(0.01, 0.05), label="anomalous"))
            events.append(self.generate_event(session_id, "AUTH_FAILURE", client_ip, server_ip, byte_count=0, delta_seconds=random.uniform(0.005, 0.02), label="anomalous"))
            events.append(self.generate_event(session_id, "RESPONSE_401", server_ip, client_ip, status_code=401, byte_count=random.randint(150, 300), delta_seconds=random.uniform(0.01, 0.05), label="anomalous"))
        events.append(self.generate_event(session_id, "CLOSE", client_ip, server_ip, byte_count=32, delta_seconds=random.uniform(0.05, 0.1), label="anomalous"))
        return events

    def template_anom_impossible_transition(self, session_id: str, client_ip: str, server_ip: str) -> list:
        """Impossible transition: IDLE -> RESPONSE_SENT (server responds without connect or request)"""
        events = []
        events.append(self.generate_event(session_id, "RESPONSE_SENT", server_ip, client_ip, status_code=200, byte_count=random.randint(500, 1000), delta_seconds=random.uniform(0.1, 0.3), label="anomalous"))
        events.append(self.generate_event(session_id, "CLOSE", client_ip, server_ip, byte_count=32, delta_seconds=random.uniform(0.1, 0.3), label="anomalous"))
        return events

    def template_anom_auth_bypass(self, session_id: str, client_ip: str, server_ip: str) -> list:
        """Auth bypass: CONNECT -> REQUEST -> AUTH_FAILURE -> RESPONSE_200 (violates FSM AUTH_FAILED -> RESPONSE_200)"""
        events = []
        events.append(self.generate_event(session_id, "CONNECT", client_ip, server_ip, byte_count=64, delta_seconds=random.uniform(0.1, 0.3), label="anomalous"))
        events.append(self.generate_event(session_id, "REQUEST", client_ip, server_ip, method="GET", path_category="/admin/dashboard", byte_count=random.randint(300, 600), delta_seconds=random.uniform(0.05, 0.1), label="anomalous"))
        events.append(self.generate_event(session_id, "AUTH_FAILURE", client_ip, server_ip, byte_count=0, delta_seconds=random.uniform(0.02, 0.05), label="anomalous"))
        events.append(self.generate_event(session_id, "RESPONSE_200", server_ip, client_ip, status_code=200, byte_count=random.randint(3000, 9000), delta_seconds=random.uniform(0.05, 0.2), label="anomalous"))
        events.append(self.generate_event(session_id, "CLOSE", client_ip, server_ip, byte_count=32, delta_seconds=random.uniform(0.1, 0.3), label="anomalous"))
        return events

    # ================= UNSEEN ANOMALOUS TEMPLATES (For generalization test) =================
    def template_unseen_rapid_malformed(self, session_id: str, client_ip: str, server_ip: str) -> list:
        """Unseen template 1: Flood of malformed requests directly to error and timeout"""
        events = []
        events.append(self.generate_event(session_id, "CONNECT", client_ip, server_ip, byte_count=64, delta_seconds=random.uniform(0.05, 0.1), label="anomalous"))
        for _ in range(4):
            events.append(self.generate_event(session_id, "REQUEST", client_ip, server_ip, method="PUT", path_category="/exploit/payload", byte_count=random.randint(5000, 15000), delta_seconds=0.01, label="anomalous"))
            events.append(self.generate_event(session_id, "MALFORMED", client_ip, server_ip, byte_count=0, delta_seconds=0.005, label="anomalous"))
            events.append(self.generate_event(session_id, "RESPONSE_500", server_ip, client_ip, status_code=500, byte_count=random.randint(100, 300), delta_seconds=0.01, label="anomalous"))
        return events

    def template_unseen_post_close_chatter(self, session_id: str, client_ip: str, server_ip: str) -> list:
        """Unseen template 2: Activity continued after connection CLOSE"""
        events = []
        events.append(self.generate_event(session_id, "CONNECT", client_ip, server_ip, byte_count=64, delta_seconds=random.uniform(0.1, 0.3), label="anomalous"))
        events.append(self.generate_event(session_id, "CLOSE", client_ip, server_ip, byte_count=32, delta_seconds=random.uniform(0.1, 0.2), label="anomalous"))
        events.append(self.generate_event(session_id, "REQUEST", client_ip, server_ip, method="GET", path_category="/leaked/data", byte_count=random.randint(200, 500), delta_seconds=random.uniform(0.05, 0.1), label="anomalous"))
        events.append(self.generate_event(session_id, "RESPONSE_200", server_ip, client_ip, status_code=200, byte_count=random.randint(1000, 4000), delta_seconds=random.uniform(0.05, 0.2), label="anomalous"))
        return events


def generate_all_datasets(total_sessions: int = 600, output_dir: str = "c:/Projects/FSM-NIDS/datasets/synthetic"):
    os.makedirs(output_dir, exist_ok=True)
    generator = SessionGenerator(datetime(2026, 11, 1, 8, 0, 0))

    normal_templates = [
        generator.template_normal_successful,
        generator.template_normal_redirect,
        generator.template_normal_keepalive,
        generator.template_normal_auth_retry,
        generator.template_normal_timeout,
    ]
    # Weights for normal templates
    normal_weights = [0.45, 0.15, 0.20, 0.10, 0.10]

    anom_templates = [
        generator.template_anom_skipped_auth,
        generator.template_anom_out_of_order,
        generator.template_anom_repeated_errors,
        generator.template_anom_impossible_transition,
        generator.template_anom_auth_bypass,
    ]
    anom_weights = [0.25, 0.20, 0.25, 0.15, 0.15]

    sessions = []
    session_labels = []

    # 70% normal, 30% anomalous
    n_normal = int(total_sessions * 0.70)
    n_anom = total_sessions - n_normal

    session_counter = 0

    # Generate normal sessions
    for _ in range(n_normal):
        session_counter += 1
        sid = f"sess_{session_counter:05d}"
        client_ip = random.choice(CLIENT_IPS)
        server_ip = random.choice(SERVER_IPS)
        tmpl = random.choices(normal_templates, weights=normal_weights)[0]
        evs = tmpl(sid, client_ip, server_ip)
        sessions.append((sid, "normal", evs))
        session_labels.append("normal")

    # Generate anomalous sessions
    for _ in range(n_anom):
        session_counter += 1
        sid = f"sess_{session_counter:05d}"
        client_ip = random.choice(CLIENT_IPS)
        server_ip = random.choice(SERVER_IPS)
        tmpl = random.choices(anom_templates, weights=anom_weights)[0]
        evs = tmpl(sid, client_ip, server_ip)
        sessions.append((sid, "anomalous", evs))
        session_labels.append("anomalous")

    # Shuffle sessions so normal and anomalous are interspersed
    random.shuffle(sessions)

    # Split train/test (80% train, 20% test) by session to prevent data leakage
    n_train = int(len(sessions) * 0.80)
    train_sessions = sessions[:n_train]
    test_sessions = sessions[n_train:]

    train_events = [ev for _, _, evs in train_sessions for ev in evs]
    test_events = [ev for _, _, evs in test_sessions for ev in evs]

    train_df = pd.DataFrame(train_events, columns=CSV_COLUMNS)
    test_df = pd.DataFrame(test_events, columns=CSV_COLUMNS)

    train_path = os.path.join(output_dir, "training_data.csv")
    test_path = os.path.join(output_dir, "test_data.csv")

    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    # Generate unseen templates for generalization testing
    unseen_sessions = []
    unseen_templates = [
        generator.template_unseen_rapid_malformed,
        generator.template_unseen_post_close_chatter,
    ]
    for i in range(50):
        session_counter += 1
        sid = f"sess_unseen_{session_counter:05d}"
        client_ip = random.choice(CLIENT_IPS)
        server_ip = random.choice(SERVER_IPS)
        tmpl = random.choice(unseen_templates)
        evs = tmpl(sid, client_ip, server_ip)
        unseen_sessions.append((sid, "anomalous", evs))

    unseen_events = [ev for _, _, evs in unseen_sessions for ev in evs]
    unseen_df = pd.DataFrame(unseen_events, columns=CSV_COLUMNS)
    unseen_path = os.path.join(output_dir, "unseen_templates.csv")
    unseen_df.to_csv(unseen_path, index=False)

    print(f"Total sessions generated: {len(sessions)}")
    print(f"Train sessions: {len(train_sessions)}, Train events: {len(train_events)}")
    print(f"Test sessions: {len(test_sessions)}, Test events: {len(test_events)}")
    print(f"Unseen test sessions: {len(unseen_sessions)}, Unseen events: {len(unseen_events)}")
    print(f"Saved to: {train_path}, {test_path}, {unseen_path}")


if __name__ == "__main__":
    generate_all_datasets()
