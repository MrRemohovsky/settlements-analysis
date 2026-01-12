

def format_number(n):
    """Форматирует число с пробелами: 12380664 → 12 380 664"""
    return f"{n:,}".replace(',', ' ')

def get_stats(df):
    return {
            'total': format_number(int(df.sum())),
            'mean': format_number(int(df.mean())),
            'median': format_number(int(df.median())),
            'max': format_number(int(df.max())),
            'min': format_number(int(df[df > 0].min()) if not df[df > 0].empty else 0),
        }