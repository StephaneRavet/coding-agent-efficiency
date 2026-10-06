def deduplicate_names(names):
    """Keep the first spelling of every name, ignoring case and whitespace."""
    result = []
    for name in names:
        cleaned = name.strip()
        if cleaned and cleaned.lower() not in [item.lower() for item in result]:
            result.append(cleaned)
    return result
