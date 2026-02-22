import snowflake.connector
from datetime import datetime
import os
from dotenv import load_dotenv

# -----------------------------------------------------
# Load Environment Variables
# -----------------------------------------------------
load_dotenv()

SNOWFLAKE_CONFIG = {
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
    "database": os.getenv("SNOWFLAKE_DATABASE"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA"),
    "role": os.getenv("SNOWFLAKE_ROLE"),
}

# -----------------------------------------------------
# Snowflake Connection
# -----------------------------------------------------
def get_connection():
    return snowflake.connector.connect(**SNOWFLAKE_CONFIG)

# -----------------------------------------------------
# Main Setup Function
# -----------------------------------------------------
def setup_banking_data():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        print("Creating tables...")

        # -----------------------------------------------------
        # Create Tables
        # -----------------------------------------------------

        cursor.execute("""
        CREATE OR REPLACE TABLE customers (
            customer_id INT PRIMARY KEY,
            full_name STRING,
            dob DATE,
            gender STRING,
            phone STRING,
            email STRING,
            risk_profile STRING,
            created_at TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE OR REPLACE TABLE accounts (
            account_id INT PRIMARY KEY,
            customer_id INT,
            account_number STRING,
            account_type STRING,
            balance NUMBER(15,2),
            status STRING,
            opened_date DATE,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
        """)

        cursor.execute("""
        CREATE OR REPLACE TABLE transactions (
            transaction_id INT PRIMARY KEY,
            account_id INT,
            transaction_type STRING,
            amount NUMBER(15,2),
            transaction_date TIMESTAMP,
            category STRING,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        );
        """)

        cursor.execute("""
        CREATE OR REPLACE TABLE loans (
            loan_id INT PRIMARY KEY,
            customer_id INT,
            loan_type STRING,
            principal_amount NUMBER(15,2),
            outstanding_amount NUMBER(15,2),
            interest_rate FLOAT,
            emi NUMBER(15,2),
            status STRING,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
        """)

        cursor.execute("""
        CREATE OR REPLACE TABLE plans (
            plan_id INT PRIMARY KEY,
            customer_id INT,
            plan_type STRING,
            invested_amount NUMBER(15,2),
            maturity_date DATE,
            risk_category STRING,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
        """)

        print("Inserting data...")

        # -----------------------------------------------------
        # Insert Customers
        # -----------------------------------------------------

        customers_data = [
            (101, 'Rahul Sharma', '1988-05-12', 'Male', '9876543210', 'rahul@email.com', 'Medium', datetime.now()),
            (102, 'Ananya Reddy', '1992-11-03', 'Female', '9123456780', 'ananya@email.com', 'Low', datetime.now()),
            (103, 'Vikram Singh', '1985-07-21', 'Male', '9988776655', 'vikram@email.com', 'High', datetime.now()),
            (104, 'Priya Nair', '1995-02-18', 'Female', '9090909090', 'priya@email.com', 'Low', datetime.now()),
            (105, 'Arjun Mehta', '1990-09-09', 'Male', '9812345678', 'arjun@email.com', 'Medium', datetime.now()),
        ]

        cursor.executemany("""
        INSERT INTO customers VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, customers_data)

        # -----------------------------------------------------
        # Insert Accounts
        # -----------------------------------------------------

        accounts_data = [
            (201, 101, 'ACC5001', 'Savings', 250000.00, 'Active', '2020-01-15'),
            (202, 102, 'ACC5002', 'Current', 150000.00, 'Active', '2019-03-10'),
            (203, 103, 'ACC5003', 'Savings', 500000.00, 'Active', '2018-06-25'),
            (204, 104, 'ACC5004', 'Savings', 120000.00, 'Inactive', '2021-08-01'),
            (205, 105, 'ACC5005', 'Current', 300000.00, 'Active', '2017-12-12'),
        ]

        cursor.executemany("""
        INSERT INTO accounts VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, accounts_data)

        # -----------------------------------------------------
        # Insert Transactions
        # -----------------------------------------------------

        transactions_data = [
            (301, 201, 'Credit', 50000.00, '2026-02-20 10:30:00', 'Salary'),
            (302, 201, 'Debit', 12000.00, '2026-02-21 09:15:00', 'Shopping'),
            (303, 202, 'Debit', 25000.00, '2026-02-21 11:45:00', 'Business'),
            (304, 203, 'Credit', 75000.00, '2026-02-19 14:20:00', 'Investment'),
            (305, 203, 'Debit', 15000.00, '2026-02-20 16:10:00', 'Travel'),
            (306, 204, 'Debit', 8000.00, '2026-02-21 12:00:00', 'Groceries'),
            (307, 205, 'Credit', 100000.00, '2026-02-18 08:00:00', 'Client Payment'),
            (308, 205, 'Debit', 45000.00, '2026-02-21 15:30:00', 'Equipment'),
            (309, 202, 'Credit', 30000.00, '2026-02-19 13:00:00', 'Consulting'),
            (310, 201, 'Debit', 20000.00, '2026-02-22 17:45:00', 'Insurance'),
        ]

        cursor.executemany("""
        INSERT INTO transactions VALUES (%s,%s,%s,%s,%s,%s)
        """, transactions_data)

        # -----------------------------------------------------
        # Insert Loans
        # -----------------------------------------------------

        loans_data = [
            (401, 101, 'Home Loan', 2000000.00, 1500000.00, 7.5, 25000.00, 'Active'),
            (402, 103, 'Car Loan', 800000.00, 400000.00, 8.2, 18000.00, 'Active'),
            (403, 105, 'Personal Loan', 500000.00, 200000.00, 10.5, 15000.00, 'Closed'),
            (404, 101, 'Personal Loan', 400000.00, 100000.00, 10.5, 15000.00, 'Active'),
            (405, 102, 'Car Loan', 800000.00, 400000.00, 8.2, 18000.00, 'Active'),
            (406, 102, 'Home Loan', 2000000.00, 1500000.00, 8.2, 18000.00, 'Active'),

        ]

        cursor.executemany("""
        INSERT INTO loans VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, loans_data)

        # -----------------------------------------------------
        # Insert Plans
        # -----------------------------------------------------

        plans_data = [
            (501, 101, 'SIP', 300000.00, '2030-12-31', 'Medium'),
            (502, 102, 'FD', 200000.00, '2027-06-30', 'Low'),
            (503, 103, 'Insurance', 500000.00, '2035-01-01', 'High'),
            (504, 104, 'SIP', 150000.00, '2029-09-15', 'Medium'),
            (505, 105, 'FD', 250000.00, '2028-03-20', 'Low'),
        ]

        cursor.executemany("""
        INSERT INTO plans VALUES (%s,%s,%s,%s,%s,%s)
        """, plans_data)

        conn.commit()
        print("✅ Tables created and data inserted successfully!")

    except Exception as e:
        conn.rollback()
        print("❌ Error occurred:", e)

    finally:
        cursor.close()
        conn.close()


# -----------------------------------------------------
# Run Script
# -----------------------------------------------------
if __name__ == "__main__":
    setup_banking_data()