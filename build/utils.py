def format_number(value):
    """Format a number with appropriate suffix (T, B, M, K). Returns 'N/A' if None. Negative values are in parentheses."""
    if value is None:
        return "N/A"

    abs_value = abs(value)

    if abs_value >= 1e12:
        formatted = f"{abs_value / 1e12:.1f}T"
    elif abs_value >= 1e9:
        formatted = f"{abs_value / 1e9:.1f}B"
    elif abs_value >= 1e6:
        formatted = f"{abs_value / 1e6:.1f}M"
    elif abs_value >= 1e3:
        formatted = f"{abs_value / 1e3:.1f}K"
    else:
        formatted = f"{abs_value:,.0f}"

    return formatted

def format_currency(value):
    """Format a number as currency. Returns 'N/A' if None. Negative values are in parentheses."""
    if value is None:
        return "N/A"

    abs_value = abs(value)
    formatted = f"{abs_value:,.1f}"

    return formatted

def format_percentage(value):
    """Format a number as percentage. Returns 'N/A' if None. Negative values are in parentheses."""
    if value is None:
        return "N/A"

    abs_value = abs(value)
    formatted = f"{abs_value * 100:.1f}%"

    return formatted

def safe_divide(a, b):
    return a / b if b != 0 else 0

def growth_rate(new, old):
    return safe_divide(new - old, abs(old))

