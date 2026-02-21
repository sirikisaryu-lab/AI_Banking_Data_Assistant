from llm.llm_client import chat_completion
from llm.prompts import SQL_GENERATION_PROMPT
from security.sql_validator import validate_sql

def generate_sql(question: str, schema: str):
    prompt = SQL_GENERATION_PROMPT.format(schema=schema, question=question)
    sql = chat_completion("You are a SQL generator.", prompt, temperature=0)
    # print(sql)
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
