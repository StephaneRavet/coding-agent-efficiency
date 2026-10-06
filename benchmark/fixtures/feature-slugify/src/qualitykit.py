def slugify(text: str) -> str:
    """Create a lowercase, hyphen-separated label."""
    return "-".join(text.lower().split())
