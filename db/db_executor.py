from db.snowflake_connection import get_connection

def execute_query(sql: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    cursor.close()
    conn.close()

    return {
        "columns": columns,
        "rows": results
    }

# execute_query_result = execute_query("SELECT * FROM customers LIMIT 5;")
# print(execute_query_result)