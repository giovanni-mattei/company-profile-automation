def format_number(value):
    """Format a number with appropriate suffix (T, B, M, K). Returns 'N/A' if None."""
    if value is None:
        return "N/A"
    if abs(value) >= 1e12:
        return f"{value / 1e12:.1f}T"
    elif abs(value) >= 1e9:
        return f"{value / 1e9:.1f}B"
    elif abs(value) >= 1e6:
        return f"{value / 1e6:.1f}M"
    elif abs(value) >= 1e3:
        return f"{value / 1e3:.1f}K"
    else:
        return f"{value:,.0f}"

def format_currency(value):
    """Format a number as currency. Returns 'N/A' if None."""
    if value is None:
        return "N/A"
    return f"{value:,.1f}"

def format_percentage(value):
    """Format a number as percentage. Returns 'N/A' if None."""
    if value is None:
        return "N/A"
    return f"{value * 100:.1f}%"

def get_metric(metric, source):
    try:
        return source.loc[metric, financials.columns[:3]].values
    except:
        return [0, 0, 0]

def safe_divide(a, b):
    return a / b if b != 0 else 0

def growth_rate(new, old):
    return safe_divide(new - old, abs(old))

