"""Lightweight automated SQLite migration script for Phase 3 SaaS columns."""
import sqlite3
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend", "traceguard.db"))
print(f"Migrating database: {db_path}")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

def add_col(table, col, col_type):
    try:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
        print(f"Added {col} to {table}")
    except Exception as e:
        print(f"Notice ({table}.{col}): {e}")

add_col("users", "full_name", "VARCHAR(100)")
add_col("network_events", "workspace_id", "VARCHAR(50) DEFAULT 'default-workspace'")
add_col("alerts", "workspace_id", "VARCHAR(50) DEFAULT 'default-workspace'")
add_col("datasets", "workspace_id", "VARCHAR(50) DEFAULT 'default-workspace'")
add_col("simulations", "workspace_id", "VARCHAR(50) DEFAULT 'default-workspace'")

conn.commit()
conn.close()
print("Migration script executed successfully.")
