from db.snowflake_connection import get_connection

def fetch_schema():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = CURRENT_SCHEMA()
    """)

    rows = cursor.fetchall()

    schema_dict = {}
    for table, column, dtype in rows:
        if table not in schema_dict:
            schema_dict[table] = []
        schema_dict[table].append(f"{column} ({dtype})")

    cursor.close()
    conn.close()

    schema_str = ""
    for table, columns in schema_dict.items():
        schema_str += f"\nTable: {table}\nColumns: {', '.join(columns)}\n"
    
    
    return schema_str

# fetch_schema_result = fetch_schema()
# print(fetch_schema_result)