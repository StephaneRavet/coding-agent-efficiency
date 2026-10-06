def mean(values):
    """Return the arithmetic mean of a collection."""
    if len(values) == 0:
        raise ValueError("mean is undefined for empty input")
    return sum(values) / len(values)
