# Sample API Requests

## Create Claim

```bash
curl -X POST http://localhost:5000/api/claims \
  -H "Content-Type: application/json" \
  -d '{
    "claimant_name": "Jane Smith",
    "claimant_age": 35,
    "claim_amount": 8000,
    "claim_type": "auto",
    "policy_duration_months": 36,
    "previous_claims_count": 0,
    "claim_description": "Rear-end collision at intersection"
  }'
```

## Predict Fraud (without saving)

```bash
curl -X POST http://localhost:5000/api/predict-fraud \
  -H "Content-Type: application/json" \
  -d '{
    "claimant_name": "Jane Smith",
    "claimant_age": 35,
    "claim_amount": 8000,
    "claim_type": "auto",
    "policy_duration_months": 36,
    "previous_claims_count": 0,
    "claim_description": "Rear-end collision"
  }'
```

## Predict Fraud (with claim_id to save)

```bash
curl -X POST http://localhost:5000/api/predict-fraud \
  -H "Content-Type: application/json" \
  -d '{
    "claimant_name": "Jane Smith",
    "claimant_age": 35,
    "claim_amount": 8000,
    "claim_type": "auto",
    "policy_duration_months": 36,
    "previous_claims_count": 0,
    "claim_description": "Rear-end collision",
    "claim_id": "CLM-20240314-abc12345"
  }'
```

## Get All Claims

```bash
curl "http://localhost:5000/api/claims?page=1&per_page=10"
```

## Get Claims with Filters

```bash
curl "http://localhost:5000/api/claims?status=pending&claim_type=auto&sort_by=amount&sort_order=desc"
```

## Get Single Claim

```bash
curl http://localhost:5000/api/claims/CLM-20240314-abc12345
```

## Update Claim Status

```bash
curl -X PUT http://localhost:5000/api/claims/CLM-20240314-abc12345/status \
  -H "Content-Type: application/json" \
  -d '{"status": "approved"}'
```

## Get Statistics

```bash
curl http://localhost:5000/api/statistics
```

## Get Model Info

```bash
curl http://localhost:5000/api/model-info
```

## Export Claims CSV

```bash
curl -o claims_export.csv http://localhost:5000/api/export/claims/csv
```

## Health Check

```bash
curl http://localhost:5000/health
```
