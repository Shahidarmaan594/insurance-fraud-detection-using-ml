"""
Data validation module for claim submissions.
"""

from typing import Tuple, Optional, List
from datetime import datetime
from config import (
    CLAIM_TYPES,
    MIN_AGE,
    MAX_AGE,
    MIN_CLAIM_AMOUNT,
    MAX_CLAIM_AMOUNT,
    MIN_POLICY_DURATION,
    MAX_POLICY_DURATION,
    MIN_PREVIOUS_CLAIMS,
    MAX_PREVIOUS_CLAIMS,
    MAX_DESCRIPTION_LENGTH,
)


def validate_claim_amount(amount: any) -> Tuple[bool, Optional[str]]:
    """
    Validate claim amount is positive and within allowed range.
    """
    try:
        amount = float(amount)
        if amount < MIN_CLAIM_AMOUNT:
            return False, f"Claim amount must be at least {MIN_CLAIM_AMOUNT}"
        if amount > MAX_CLAIM_AMOUNT:
            return False, f"Claim amount cannot exceed {MAX_CLAIM_AMOUNT}"
        return True, None
    except (TypeError, ValueError):
        return False, "Claim amount must be a valid number"


def validate_age(age: any) -> Tuple[bool, Optional[str]]:
    """
    Validate claimant age is between 18 and 80.
    """
    try:
        age = int(age)
        if age < MIN_AGE:
            return False, f"Age must be at least {MIN_AGE}"
        if age > MAX_AGE:
            return False, f"Age cannot exceed {MAX_AGE}"
        return True, None
    except (TypeError, ValueError):
        return False, "Age must be a valid integer"


def validate_claim_type(claim_type: str) -> Tuple[bool, Optional[str]]:
    """
    Validate claim type is from allowed list.
    """
    if not claim_type or not isinstance(claim_type, str):
        return False, "Claim type is required"
    if claim_type.lower() not in CLAIM_TYPES:
        return False, f"Claim type must be one of: {', '.join(CLAIM_TYPES)}"
    return True, None


def validate_policy_duration(months: any) -> Tuple[bool, Optional[str]]:
    """
    Validate policy duration in months.
    """
    try:
        months = int(months)
        if months < MIN_POLICY_DURATION:
            return False, f"Policy duration must be at least {MIN_POLICY_DURATION} months"
        if months > MAX_POLICY_DURATION:
            return False, f"Policy duration cannot exceed {MAX_POLICY_DURATION} months"
        return True, None
    except (TypeError, ValueError):
        return False, "Policy duration must be a valid integer"


def validate_previous_claims_count(count: any) -> Tuple[bool, Optional[str]]:
    """
    Validate previous claims count.
    """
    try:
        count = int(count)
        if count < MIN_PREVIOUS_CLAIMS:
            return False, f"Previous claims must be at least {MIN_PREVIOUS_CLAIMS}"
        if count > MAX_PREVIOUS_CLAIMS:
            return False, f"Previous claims cannot exceed {MAX_PREVIOUS_CLAIMS}"
        return True, None
    except (TypeError, ValueError):
        return False, "Previous claims count must be a valid integer"


def validate_description(description: str) -> Tuple[bool, Optional[str]]:
    """
    Validate claim description - not empty, max 1000 chars.
    """
    if not description or not isinstance(description, str):
        return False, "Claim description is required"
    description = description.strip()
    if len(description) == 0:
        return False, "Claim description cannot be empty"
    if len(description) > MAX_DESCRIPTION_LENGTH:
        return False, f"Claim description cannot exceed {MAX_DESCRIPTION_LENGTH} characters"
    return True, None


def validate_claimant_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate claimant name is not empty.
    """
    if not name or not isinstance(name, str):
        return False, "Claimant name is required"
    if len(name.strip()) == 0:
        return False, "Claimant name cannot be empty"
    if len(name) > 255:
        return False, "Claimant name is too long"
    return True, None


def validate_submission_date(date_str: any) -> Tuple[bool, Optional[str]]:
    """
    Validate submission date format.
    """
    if date_str is None or date_str == "":
        return True, None  # Optional, will use current date
    try:
        if isinstance(date_str, str):
            datetime.fromisoformat(date_str.replace("Z", "+00:00")[:10])
        return True, None
    except (ValueError, TypeError):
        return False, "Invalid date format. Use YYYY-MM-DD"


def validate_claim_data(data: dict) -> Tuple[bool, Optional[dict]]:
    """
    Validate complete claim data.
    Returns (is_valid, errors_dict or None).
    """
    errors = {}
    
    # Required fields
    valid, msg = validate_claimant_name(data.get("claimant_name"))
    if not valid:
        errors["claimant_name"] = msg
    
    valid, msg = validate_age(data.get("claimant_age"))
    if not valid:
        errors["claimant_age"] = msg
    
    valid, msg = validate_claim_amount(data.get("claim_amount"))
    if not valid:
        errors["claim_amount"] = msg
    
    valid, msg = validate_claim_type(data.get("claim_type"))
    if not valid:
        errors["claim_type"] = msg
    
    valid, msg = validate_policy_duration(data.get("policy_duration_months"))
    if not valid:
        errors["policy_duration_months"] = msg
    
    valid, msg = validate_description(data.get("claim_description"))
    if not valid:
        errors["claim_description"] = msg
    
    # Optional field with default
    prev_claims = data.get("previous_claims_count", 0)
    valid, msg = validate_previous_claims_count(prev_claims)
    if not valid:
        errors["previous_claims_count"] = msg
    
    valid, msg = validate_submission_date(data.get("submission_date"))
    if not valid:
        errors["submission_date"] = msg
    
    return (len(errors) == 0, errors if errors else None)
