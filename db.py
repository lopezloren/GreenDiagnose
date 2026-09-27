"""
db.py - Simple MySQL connection helper for GreenDiagnose.
Uses environment variables so credentials never get committed to git.

Create a .env file (not committed) with:
    DB_HOST=localhost
    DB_USER=your_mysql_user
    DB_PASSWORD=your_mysql_password
    DB_NAME=greendiagnose
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Returns a new MySQL connection. Caller is responsible for closing it."""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'greendiagnose')
        )
        return conn
    except Error as e:
        print(f"Database connection failed: {e}")
        raise


def fetch_all(query, params=None):
    """Run a SELECT query, return list of dict rows."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def execute(query, params=None):
    """Run an INSERT/UPDATE/DELETE, return the new row's id (for INSERTs)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id
