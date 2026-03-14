"""
Synthetic data generator for Insurance Fraud Detection model training.
Generates 500 sample claims with 20% fraud rate and realistic distributions.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# Reproducible randomness
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

CLAIM_TYPES = ["auto", "health", "property", "liability"]
OUTPUT_CSV = Path(__file__).parent / "data" / "synthetic_claims.csv"
OUTPUT_JSON = Path(__file__).parent / "data" / "sample_claims.json"
TOTAL_CLAIMS = 500
FRAUD_RATE = 0.20
FRAUD_COUNT = int(TOTAL_CLAIMS * FRAUD_RATE)


def generate_claimant_name() -> str:
    """Generate realistic claimant names."""
    first_names = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer",
        "Michael", "Linda", "William", "Elizabeth", "David", "Barbara",
        "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah"
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
        "Miller", "Davis", "Rodriguez", "Martinez", "Wilson", "Anderson"
    ]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def generate_description(claim_type: str, is_fraud: bool) -> str:
    """Generate claim description."""
    if claim_type == "auto":
        legit = ["Minor collision at intersection", "Rear-end accident on highway",
                 "Vehicle damaged in parking lot", "Side mirror damaged"]
        fraud_desc = ["Total loss claim - minor damage", "Exaggerated repair costs",
                      "Pre-existing damage reported as new"]
    elif claim_type == "health":
        legit = ["Emergency room visit for injury", "Surgery for condition",
                 "Physical therapy sessions", "Medication coverage"]
        fraud_desc = ["Duplicate billing claim", "Unnecessary procedures claimed",
                      "Fake medical documents"]
    elif claim_type == "property":
        legit = ["Water damage from pipe burst", "Storm damage to roof",
                 "Theft of belongings", "Fire damage in kitchen"]
        fraud_desc = ["Inflated property values", "Fake inventory list",
                      "Staged damage claim"]
    else:
        legit = ["Slip and fall incident", "Dog bite incident",
                 "Property damage from tenant", "Liability for accident"]
        fraud_desc = ["Exaggerated injury claim", "Fake witness statement",
                      "Fabricated incident details"]

    options = fraud_desc if is_fraud else legit
    return random.choice(options)


def generate_synthetic_claims() -> pd.DataFrame:
    """
    Generate 500 synthetic claims with 20% fraud and realistic distributions.
    """
    claims = []
    claim_ids = set()

    for i in range(TOTAL_CLAIMS):
        # Determine if fraudulent
        is_fraud = i < FRAUD_COUNT

        # Claim ID
        claim_id = f"CLM-{2024000001 + i}"
        while claim_id in claim_ids:
            claim_id = f"CLM-{random.randint(1000000, 9999999)}"
        claim_ids.add(claim_id)

        # Ages: normal distribution 30-60
        age = int(np.clip(np.random.normal(45, 12), 18, 80))

        # Amounts: log-normal 1000-100000 (fraud tends higher)
        if is_fraud:
            amount = np.random.lognormal(9.5, 1.2)  # Mean ~15k, skewed high
        else:
            amount = np.random.lognormal(8.5, 1.0)  # Mean ~5k
        amount = float(np.clip(amount, 500, 150000))

        # Policy duration: uniform 1-360 (fraud: shorter policies)
        if is_fraud:
            duration = random.randint(1, min(120, 360))
        else:
            duration = random.randint(12, 360)

        # Previous claims: fraud has more
        if is_fraud:
            prev_claims = random.choices([0, 1, 2, 3, 4, 5], weights=[1, 2, 3, 2, 1, 1])[0]
        else:
            prev_claims = random.choices([0, 1, 2, 3], weights=[5, 3, 1, 1])[0]

        # Claim type
        claim_type = random.choice(CLAIM_TYPES)

        # Fraud patterns: high amount + short duration
        if is_fraud and random.random() > 0.3:
            amount *= random.uniform(1.2, 2.0)
            duration = min(duration, 24)

        submission_date = (
            datetime(2023, 1, 1) + timedelta(days=random.randint(0, 400))
        ).strftime("%Y-%m-%d")

        claims.append({
            "claim_id": claim_id,
            "claimant_name": generate_claimant_name(),
            "claimant_age": age,
            "claim_amount": round(amount, 2),
            "claim_type": claim_type,
            "policy_duration_months": duration,
            "previous_claims_count": prev_claims,
            "claim_description": generate_description(claim_type, is_fraud),
            "submission_date": submission_date,
            "is_fraud": 1 if is_fraud else 0,
        })

    # Shuffle to mix fraud/non-fraud
    random.shuffle(claims)
    return pd.DataFrame(claims)


def main():
    """Generate and save synthetic data."""
    Path(OUTPUT_CSV).parent.mkdir(parents=True, exist_ok=True)

    df = generate_synthetic_claims()

    # Save full dataset for training
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Generated {len(df)} claims. Fraud rate: {df['is_fraud'].mean():.1%}")
    print(f"Saved to {OUTPUT_CSV}")

    # Save 50 samples for API testing (without is_fraud)
    sample = df.head(50).copy()
    sample.drop(columns=["is_fraud"], inplace=True)
    sample_list = sample.to_dict(orient="records")
    with open(OUTPUT_JSON, "w") as f:
        json.dump(sample_list, f, indent=2)
    print(f"Saved 50 sample claims to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
