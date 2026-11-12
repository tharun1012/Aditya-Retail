def normalize_phone(phone: str) -> str:
    """
    Normalize a phone number for consistent storage/lookup.
    Strips all non-digit characters and keeps only the last 10 digits,
    so +918054214574, 918054214574, and 8054214574 all normalize to
    the same value: 8054214574
    """
    if not phone:
        return ""
    digits_only = "".join(ch for ch in phone if ch.isdigit())
    return digits_only[-10:] if len(digits_only) >= 10 else digits_only
