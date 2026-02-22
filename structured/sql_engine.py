from llm.llm_client import chat_completion
from llm.prompts import SQL_GENERATION_PROMPT, CLIENT360_SQL_PROMPT
from security.sql_validator import validate_sql



def generate_sql(question: str, schema: str, intent: str, error_feedback: str = None, conversation_history: list = None):
    """
    Generate SQL from a natural language question.

    Args:
        question:             The user's natural language query.
        schema:               Database schema context string.
        intent:               Classified intent (e.g. CLIENT360, STRUCTURED_DATA_QUERY).
        error_feedback:       If provided, the previous SQL + DB error are appended
                              so the LLM can self-correct on retry.
        conversation_history: Prior conversation turns passed to the LLM so it can
                              resolve follow-up references like "same customer",
                              "his account", "that loan" without re-asking the user.
    """
    if intent == "CLIENT360":
        prompt = CLIENT360_SQL_PROMPT.format(
            schema=schema,
            question=question
        )
    else:
        prompt = SQL_GENERATION_PROMPT.format(
            schema=schema,
            question=question
        )

    # On retries, tell the LLM exactly what went wrong so it doesn't repeat the same mistake
    if error_feedback:
        prompt += (
            f"\n\n--- PREVIOUS ATTEMPT FAILED ---\n"
            f"{error_feedback}\n"
            f"Please fix the SQL and return only the corrected query."
        )

    sql = chat_completion(
        "You are a Snowflake SQL generator.",
        prompt,
        temperature=0,
        conversation_history=conversation_history
    )

    sql = clean_sql(sql)
    sql = validate_sql(sql)

    return sql

def clean_sql(sql: str):
    # strip markdown fences and whitespace
    sql = sql.replace("```sql", "").replace("```", "").strip()
    # remove any trailing semicolons that may come from the LLM
    sql = sql.rstrip(";")
    return sql

# schema = """Table: LOANS
# Columns: LOAN_TYPE (TEXT), OUTSTANDING_AMOUNT (NUMBER), PRINCIPAL_AMOUNT (NUMBER), INTEREST_RATE (FLOAT), STATUS (TEXT), CUSTOMER_ID (NUMBER), EMI (NUMBER), LOAN_ID (NUMBER)

# Table: PLANS
# Columns: INVESTED_AMOUNT (NUMBER), PLAN_TYPE (TEXT), CUSTOMER_ID (NUMBER), MATURITY_DATE (DATE), RISK_CATEGORY (TEXT), PLAN_ID (NUMBER)

# Table: CUSTOMERS
# Columns: DOB (DATE), CUSTOMER_ID (NUMBER), FULL_NAME (TEXT), RISK_PROFILE (TEXT), CREATED_AT (TIMESTAMP_NTZ), GENDER (TEXT), PHONE (TEXT), EMAIL (TEXT)

# Table: ACCOUNTS
# Columns: ACCOUNT_TYPE (TEXT), ACCOUNT_ID (NUMBER), STATUS (TEXT), BALANCE (NUMBER), ACCOUNT_NUMBER (TEXT), CUSTOMER_ID (NUMBER), OPENED_DATE (DATE)

# Table: TRANSACTIONS
# Columns: AMOUNT (NUMBER), TRANSACTION_DATE (TIMESTAMP_NTZ), CATEGORY (TEXT), ACCOUNT_ID (NUMBER), TRANSACTION_ID (NUMBER), TRANSACTION_TYPE (TEXT)"""


# if __name__ == "__main__":
#     # example usage when running the module directly
#     generate_sql_result = generate_sql("delete the  customer 101?", schema)
#     print(generate_sql_result)