
import re
import phonenumbers
from typing import Tuple, Optional
import usaddress
from loguru import logger

def normalize_phone_number(phone: str) -> Tuple[str, str]:
    """
    Normalize phone number using phonenumbers library
    Returns (normalized_number, country_code)
    """
    try:
        if not phone:
            return "", ""
        
        # Try to parse with default US country code
        try:
            parsed = phonenumbers.parse(phone, "US")
        except phonenumbers.NumberParseException:
            # Try without default country
            parsed = phonenumbers.parse(phone)
        
        # Format as E164 (standard international format)
        normalized = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        country_code = str(parsed.country_code)
        
        return normalized, country_code
    except Exception as e:
        logger.warning(f"Failed to parse phone number {phone}: {e}")
        return phone, ""

def parse_address(address: str) -> dict:
    """
    Parse address into components using usaddress library
    """
    try:
        if not address:
            return {}
        
        parsed = usaddress.tag(address)[0]
        return dict(parsed)
    except Exception as e:
        logger.warning(f"Failed to parse address {address}: {e}")
        return {}

def extract_email_username(email: str) -> str:
    """Extract and clean email username part"""
    if not email or '@' not in email:
        return ""
    
    username = email.split('@')[0].lower()
    # Remove common patterns that indicate variations
    username = re.sub(r'[0-9]+$', '', username)  # Remove trailing numbers
    username = re.sub(r'[_\-\.]+', '', username)  # Remove separators
    return username

def standardize_address_abbreviations(address: str, abbreviations: dict) -> str:
    """Standardize address abbreviations"""
    if not address:
        return ""
    
    address_lower = address.lower()
    for abbr, full in abbreviations.items():
        address_lower = re.sub(r'\b' + abbr + r'\b', full, address_lower)
    return address_lower
