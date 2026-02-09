import os
import pyodbc
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_db_connection():
    """
    Establishes a connection to the MSSQL Server using environment variables.
    """
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_NAME')
    username = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    driver = os.getenv('DB_DRIVER', '{ODBC Driver 17 for SQL Server}') # Default driver

    # Connection string for SQL Server Authentication
    conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def run_bcp(table_name, csv_path, separator='|'):
    """
    Uses the BCP utility for blazing fast data ingestion.
    """
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_NAME')
    username = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    
    # BCP command
    # -c: character type
    # -t: field terminator
    # -S: server
    # -d: database
    # -U: username
    # -P: password
    # -F: first row (2 because we might have a temp csv without header if we handle it in python)
    
    # We will use | as separator to avoid issues with commas in data
    # We'll use a temp file in the caller to ensure format matches table exactly
    
    cmd = [
        'bcp', f'{database}.dbo.{table_name}', 'in', csv_path,
        '-c', f'-t{separator}', 
        '-S', server,
        '-U', username,
        '-P', password,
        '-b', '100000', # Large batch size for BCP
    ]
    
    print(f"Executing BCP for {table_name}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"BCP successful for {table_name}.")
            print(result.stdout)
            return True
        else:
            print(f"BCP failed for {table_name}:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"An error occurred during BCP: {e}")
        return False

if __name__ == "__main__":
    # Test connection
    connection = get_db_connection()
    if connection:
        print("Successfully connected to MSSQL Server.")
        connection.close()
    else:
        print("Failed to connect to MSSQL Server.")
