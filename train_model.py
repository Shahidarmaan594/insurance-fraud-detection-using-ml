"""
Train the fraud detection model from synthetic data.
Run this after generating data with data_generator.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import MODEL_PATH
from fraud_model import train_model

DATA_CSV = Path(__file__).parent / "data" / "synthetic_claims.csv"


def main():
    if not DATA_CSV.exists():
        print("Synthetic data not found. Run: python data_generator.py")
        sys.exit(1)

    print("Training fraud detection model...")
    metrics = train_model(DATA_CSV, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    print("Metrics:", metrics)


if __name__ == "__main__":
    main()
