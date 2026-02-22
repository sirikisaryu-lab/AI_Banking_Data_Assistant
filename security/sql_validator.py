
import re

FORBIDDEN = ["insert", "update", "delete", "drop", "alter", "truncate"]

FORBIDDEN_MESSAGE = (
    "⚠️ This operation is not permitted. "
    "Only read queries are allowed. "
    "Please ask a question about retrieving data."
)


class ForbiddenSQLError(ValueError):
    """Raised when the generated SQL contains a forbidden or unsafe operation."""
    pass


def validate_sql(sql: str) -> str:
    """
    Validate that the SQL is a safe, read-only SELECT statement.

    Raises:
        ForbiddenSQLError: immediately if the SQL is not a SELECT or contains
                           forbidden keywords / multiple statements.
                           This stops the retry loop — there is no point
                           retrying a query the user was never allowed to run.
    Returns:
        str: The original SQL string if validation passes.
    """
    sql = sql.strip()
    sql_clean = sql.lower()

    # Only allow SELECT queries
    if not sql_clean.startswith("select"):
        raise ForbiddenSQLError(FORBIDDEN_MESSAGE)

    # Check for forbidden keywords anywhere in the query
    for word in FORBIDDEN:
        if re.search(rf"\b{word}\b", sql_clean):
            raise ForbiddenSQLError(FORBIDDEN_MESSAGE)

    # Prevent multiple statements
    if ";" in sql_clean:
        raise ForbiddenSQLError(FORBIDDEN_MESSAGE)

    return sql