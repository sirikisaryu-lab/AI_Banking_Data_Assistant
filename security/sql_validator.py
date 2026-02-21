import re

FORBIDDEN = ["insert", "update", "delete", "drop", "alter", "truncate"]

def validate_sql(sql: str):
    sql = sql.strip()
    sql_clean = sql.lower()

    # Only allow SELECT queries
    if not sql_clean.startswith("select"):
        return "Forbidden SQL operation detected. You can only perform read (SELECT) operations."

    # Check for forbidden keywords
    for word in FORBIDDEN:
        if re.search(rf"\b{word}\b", sql_clean):
            return "Forbidden SQL operation detected. You can only perform read (SELECT) operations."

    # Prevent multiple statements
    if ";" in sql_clean:
        return "Multiple SQL statements are not allowed. You can only perform read (SELECT) operations."

    # If everything is valid, return cleaned SQL
    return sql