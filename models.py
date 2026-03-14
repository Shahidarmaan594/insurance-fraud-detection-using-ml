"""
Database models for Insurance Fraud Detection system.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from config import DATABASE_URL, BASE_DIR


def get_db_path() -> Path:
    """Extract SQLite file path from DATABASE_URL."""
    url = DATABASE_URL
    if url.startswith("sqlite:///"):
        path = url.replace("sqlite:///", "")
        if not Path(path).is_absolute():
            path = str(BASE_DIR / path)
        return Path(path)
    return BASE_DIR / "fraud_detection.db"


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """
    Initialize database with all tables and indexes.
    """
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Claims table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                claim_id TEXT PRIMARY KEY,
                claimant_name TEXT NOT NULL,
                claimant_age INTEGER NOT NULL,
                claim_amount REAL NOT NULL,
                claim_type TEXT NOT NULL,
                policy_duration_months INTEGER NOT NULL,
                previous_claims_count INTEGER DEFAULT 0,
                claim_description TEXT NOT NULL,
                submission_date TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id TEXT NOT NULL,
                fraud_probability REAL NOT NULL,
                risk_level TEXT NOT NULL,
                feature_importance_json TEXT,
                model_version TEXT NOT NULL,
                predicted_at TEXT NOT NULL,
                FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
            )
        """)

        # Create indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_claims_claim_type ON claims(claim_type)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_claims_created_at ON claims(created_at)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_claims_submission_date ON claims(submission_date)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_predictions_claim_id ON predictions(claim_id)"
        )


def generate_claim_id() -> str:
    """Generate unique claim ID."""
    import uuid
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d")
    short_uuid = str(uuid.uuid4())[:8]
    return f"CLM-{timestamp}-{short_uuid}"


def create_claim(claim_data: dict) -> dict:
    """
    Create a new claim in the database.
    """
    claim_id = generate_claim_id()
    now = datetime.utcnow().isoformat()

    submission_date = claim_data.get("submission_date")
    if not submission_date:
        submission_date = datetime.utcnow().strftime("%Y-%m-%d")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO claims (
                claim_id, claimant_name, claimant_age, claim_amount,
                claim_type, policy_duration_months, previous_claims_count,
                claim_description, submission_date, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)
            """,
            (
                claim_id,
                claim_data["claimant_name"],
                int(claim_data["claimant_age"]),
                float(claim_data["claim_amount"]),
                claim_data["claim_type"].lower(),
                int(claim_data["policy_duration_months"]),
                int(claim_data.get("previous_claims_count", 0)),
                claim_data["claim_description"],
                submission_date,
                now,
                now,
            ),
        )

    return {
        "claim_id": claim_id,
        "status": "pending",
    }


def get_claim(claim_id: str, include_prediction: bool = True) -> Optional[dict]:
    """
    Get a single claim by ID with optional prediction data.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM claims WHERE claim_id = ?", (claim_id,))
        row = cursor.fetchone()
        if not row:
            return None

        claim = dict(row)

        if include_prediction:
            cursor.execute(
                "SELECT * FROM predictions WHERE claim_id = ? ORDER BY predicted_at DESC LIMIT 1",
                (claim_id,),
            )
            pred_row = cursor.fetchone()
            if pred_row:
                pred = dict(pred_row)
                if pred.get("feature_importance_json"):
                    import json
                    try:
                        pred["feature_importance"] = json.loads(
                            pred["feature_importance_json"]
                        )
                    except json.JSONDecodeError:
                        pred["feature_importance"] = {}
                claim["prediction"] = pred

    return claim


def get_claims(
    page: int = 1,
    per_page: int = 10,
    status: Optional[str] = None,
    claim_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    search: Optional[str] = None,
) -> dict:
    """
    Get claims with pagination and filters.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Build query
        where_clauses = []
        params = []

        if status:
            where_clauses.append("c.status = ?")
            params.append(status)
        if claim_type:
            where_clauses.append("c.claim_type = ?")
            params.append(claim_type)
        if date_from:
            where_clauses.append("c.submission_date >= ?")
            params.append(date_from)
        if date_to:
            where_clauses.append("c.submission_date <= ?")
            params.append(date_to)
        if search:
            where_clauses.append(
                "(c.claimant_name LIKE ? OR c.claim_id LIKE ?)"
            )
            params.extend([f"%{search}%", f"%{search}%"])

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # Validate sort column
        valid_sort = {"amount": "claim_amount", "date": "created_at",
                      "risk_level": "fraud_probability", "submission_date": "submission_date"}
        sort_column = valid_sort.get(sort_by, "created_at")
        order = "DESC" if sort_order.lower() == "desc" else "ASC"

        count_sql = f"SELECT COUNT(*) FROM claims c WHERE {where_sql}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]

        offset = (page - 1) * per_page

        subquery = f"""
            SELECT c.*,
                   (SELECT fraud_probability FROM predictions
                    WHERE claim_id = c.claim_id ORDER BY predicted_at DESC LIMIT 1) as fraud_probability,
                   (SELECT risk_level FROM predictions
                    WHERE claim_id = c.claim_id ORDER BY predicted_at DESC LIMIT 1) as risk_level
            FROM claims c
            WHERE {where_sql}
        """
        if sort_column == "fraud_probability":
            order_clause = f"ORDER BY COALESCE(fraud_probability, -1) {order}, created_at DESC"
        else:
            order_clause = f"ORDER BY {sort_column} {order}"

        final_query = f"""
            SELECT * FROM ({subquery}) sub
            {order_clause}
            LIMIT ? OFFSET ?
        """
        cursor.execute(final_query, params + [per_page, offset])

        rows = cursor.fetchall()
        claims = [dict(row) for row in rows]

    pages = (total + per_page - 1) // per_page if total > 0 else 1
    return {
        "claims": claims,
        "total": total,
        "page": page,
        "pages": pages,
    }


def update_claim_status(claim_id: str, status: str) -> Optional[dict]:
    """
    Update claim status.
    """
    from config import CLAIM_STATUSES
    if status not in CLAIM_STATUSES:
        return None

    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE claims SET status = ?, updated_at = ? WHERE claim_id = ?",
            (status, now, claim_id),
        )
        if cursor.rowcount == 0:
            return None
        cursor.execute("SELECT * FROM claims WHERE claim_id = ?", (claim_id,))
        row = cursor.fetchone()
    return dict(row) if row else None


def save_prediction(
    claim_id: str,
    fraud_probability: float,
    risk_level: str,
    feature_importance: dict,
    model_version: str,
) -> int:
    """
    Save prediction to database.
    """
    import json
    now = datetime.utcnow().isoformat()
    fi_json = json.dumps(feature_importance) if feature_importance else "{}"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO predictions (claim_id, fraud_probability, risk_level, 
                                     feature_importance_json, model_version, predicted_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (claim_id, fraud_probability, risk_level, fi_json, model_version, now),
        )
        return cursor.lastrowid
