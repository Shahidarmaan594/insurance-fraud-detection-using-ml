# Insurance Fraud Detection System

A production-ready Machine Learning system for detecting insurance fraud. Built with Python/Flask backend, React frontend, and Scikit-learn ensemble model.

## System Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  React Frontend │────▶│  Flask API       │────▶│  SQLite DB      │
│  (Tailwind CSS) │     │  (REST)          │     │  (claims,       │
└─────────────────┘     └────────┬─────────┘     │   predictions)   │
                                 │               └─────────────────┘
                                 ▼
                        ┌──────────────────┐
                        │  ML Model        │
                        │  (RF + LR        │
                        │   Ensemble)      │
                        └──────────────────┘
```

## Features

- **Claim Management**: Submit, view, filter, and update claims
- **Fraud Prediction**: Real-time fraud probability (0-100%) with risk levels
- **Dashboard**: Statistics, charts (claims over time, by type, status)
- **Model Info**: Performance metrics, feature importance
- **Dark Mode**: Toggle in navbar
- **Responsive Design**: Mobile, tablet, desktop
- **Data Export**: CSV export
- **Docker Support**: Deploy with docker-compose

## Installation

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm

### Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate synthetic data
python data_generator.py

# Initialize database
python -c "from models import init_database; init_database()"

# Train ML model
python train_model.py
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Quick Setup (Windows PowerShell)

```powershell
.\setup.ps1
```

### Quick Setup (Linux/Mac)

```bash
chmod +x setup.sh
./setup.sh
```

## Running Locally

**Terminal 1 - Backend:**
```bash
# Activate venv first
python app.py
```
API runs at http://localhost:5000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs at http://localhost:3000

## Docker Deployment

```bash
docker-compose up --build
```

- Backend: http://localhost:5000
- Frontend: http://localhost:3000

## API Documentation

### POST /api/claims
Create a new claim.

**Request:**
```json
{
  "claimant_name": "John Doe",
  "claimant_age": 45,
  "claim_amount": 15000,
  "claim_type": "auto",
  "policy_duration_months": 24,
  "previous_claims_count": 1,
  "claim_description": "Vehicle damage from accident"
}
```

**Response:**
```json
{
  "claim_id": "CLM-20240314-abc12345",
  "status": "pending",
  "message": "Claim submitted successfully"
}
```

### GET /api/claims
List claims with pagination, filters, and sorting.

**Query params:** `page`, `per_page`, `status`, `claim_type`, `date_from`, `date_to`, `sort_by`, `sort_order`, `search`

### GET /api/claims/:claim_id
Get single claim with prediction data.

### POST /api/predict-fraud
Get fraud prediction for claim data.

**Request:** Same as POST /api/claims, optionally include `claim_id` to save prediction.

**Response:**
```json
{
  "probability": 35.2,
  "risk_level": "medium",
  "feature_importance": {...},
  "explanation": {...}
}
```

### PUT /api/claims/:claim_id/status
Update claim status. Body: `{"status": "approved"}`

### GET /api/statistics
Get aggregate statistics.

### GET /api/model-info
Get model performance metrics and version.

## Sample cURL Commands

```bash
# Create claim
curl -X POST http://localhost:5000/api/claims -H "Content-Type: application/json" \
  -d '{"claimant_name":"Jane Smith","claimant_age":35,"claim_amount":8000,"claim_type":"auto","policy_duration_months":36,"previous_claims_count":0,"claim_description":"Rear-end collision"}'

# Predict fraud
curl -X POST http://localhost:5000/api/predict-fraud -H "Content-Type: application/json" \
  -d '{"claimant_name":"Jane Smith","claimant_age":35,"claim_amount":8000,"claim_type":"auto","policy_duration_months":36,"previous_claims_count":0,"claim_description":"Rear-end collision"}'

# Get claims
curl "http://localhost:5000/api/claims?page=1&per_page=10"
```

## File Structure

```
.
├── app.py              # Flask application
├── config.py           # Configuration
├── models.py           # Database models
├── validators.py       # Input validation
├── fraud_model.py      # ML model
├── data_generator.py   # Synthetic data
├── train_model.py      # Training script
├── requirements.txt
├── data/
│   ├── synthetic_claims.csv
│   └── sample_claims.json
├── models/
│   ├── fraud_model.pkl
│   └── model_metrics.json
├── logs/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   └── context/
│   └── package.json
└── README.md
```

## ML Model

- **Ensemble**: Random Forest (200 trees, max_depth=15) + Logistic Regression
- **Voting**: Soft voting, RF weighted 2:1
- **Features**: claim_amount_category, age_group, policy_ratio, normalized amounts, claim type one-hot
- **Risk levels**: Low (<30%), Medium (30-60%), High (60-80%), Critical (80%+)
- **Training**: Stratified 5-fold CV, synthetic data (500 claims, 20% fraud)

## Troubleshooting

- **Model not loaded**: Run `python train_model.py` after `python data_generator.py`
- **CORS errors**: Ensure backend runs on port 5000; frontend proxy in vite.config.js
- **Database errors**: Delete `fraud_detection.db` and run `python -c "from models import init_database; init_database()"`
- **Frontend API 404**: Set `VITE_API_URL=http://localhost:5000` in frontend `.env`

## Future Improvements

- User authentication
- Email alerts for critical fraud probability
- Batch CSV upload
- PDF report generation
- PostgreSQL for production
