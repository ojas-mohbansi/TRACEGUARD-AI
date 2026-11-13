"""
Model training script for TraceGuard AI.
Loads training_data.csv, extracts features, trains Isolation Forest,
and saves the model to models/isolation_forest.joblib.
"""
import os
import sys
import pandas as pd

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.detection.features.extractor import FeatureExtractor
from app.detection.ml.engine import MLEngine


def train():
    project_root = os.path.abspath(os.path.join(backend_dir, ".."))
    train_csv_path = os.path.join(project_root, "datasets", "synthetic", "training_data.csv")
    model_output_path = os.path.join(project_root, "models", "isolation_forest.joblib")

    if not os.path.exists(train_csv_path):
        print(f"Error: Training dataset not found at {train_csv_path}")
        print("Please run datasets/generate_synthetic.py first.")
        sys.exit(1)

    print(f"Loading training data from: {train_csv_path}")
    df_raw = pd.read_csv(train_csv_path)
    print(f"Total events: {len(df_raw)}, Unique sessions: {df_raw['session_id'].nunique()}")

    extractor = FeatureExtractor()
    print("Extracting 15 per-session features...")
    features_df = extractor.extract_batch(df_raw)
    print(f"Extracted features shape: {features_df.shape}")

    # Prepare ground truth labels per session if available for summary
    session_labels = df_raw.groupby("session_id")["label"].first()
    normal_count = sum(session_labels == "normal")
    anom_count = sum(session_labels == "anomalous")
    print(f"Class distribution: Normal={normal_count}, Anomalous={anom_count}")

    print("Training Isolation Forest (contamination=0.1, seed=42)...")
    ml_engine = MLEngine(contamination=0.1, random_state=42, model_path=model_output_path)
    train_summary = ml_engine.train(features_df, seed=42)
    print(f"Training completed: {train_summary}")

    print(f"Saving model bundle to: {model_output_path}")
    ml_engine.save_model(model_output_path)
    print(f"Model saved successfully. File size: {os.path.getsize(model_output_path)} bytes")

    # Quick sanity evaluation on training sessions
    print("Running sanity predictions...")
    preds = ml_engine.predict(features_df)
    anom_preds = sum(1 for p in preds if p["prediction"] == "anomalous")
    print(f"Predicted anomalous sessions on train set: {anom_preds}/{len(preds)}")
    print("=== Training complete ===")


if __name__ == "__main__":
    train()
