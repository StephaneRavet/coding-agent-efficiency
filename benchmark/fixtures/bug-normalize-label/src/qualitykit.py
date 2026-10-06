def normalize_label(value: str) -> str:
    """Trim a label and reduce repeated spaces."""
    return value.strip().replace("  ", " ")
