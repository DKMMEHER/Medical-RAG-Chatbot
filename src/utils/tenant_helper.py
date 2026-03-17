import re
from typing import Optional

def extract_tenant_id(email: str) -> str:
    """
    Extracts a tenant ID from an email address using its domain.
    E.g. 'doctor@mountsinai.org' -> 'mountsinai-org'
    
    Args:
        email: User's email address
        
    Returns:
        str: Sanitize tenant ID (alphanumeric and dashes only)
    """
    if not email or "@" not in email:
        return "default"
        
    domain = email.split("@")[-1].lower()
    
    # Replace dots and special chars with dashes
    tenant_id = re.sub(r"[^a-zA-Z0-9]", "-", domain)
    
    # Remove trailing/leading dashes
    tenant_id = tenant_id.strip("-")
    
    return tenant_id or "default"
