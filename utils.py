def parse_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
    
def parse_float(value: str, default: float = 0) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return default