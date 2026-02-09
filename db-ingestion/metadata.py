import os
import pandas as pd
from db_connect import get_db_connection

def ingest_metadata(csv_path):
    """
    Ingests metadata from CSV into MSSQL table.
    """
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    # Read CSV
    df = pd.read_csv(csv_path)

    # Connect to MSSQL
    conn = get_db_connection()
    if not conn:
        return
        
    cursor = conn.cursor()
    cursor.fast_executemany = True

    # Prepare data for insertion (convert NaN to None for MSSQL compatibility)
    insert_cols = ['Table', 'Field', 'Description']
    
    # Ensure all columns exist
    for col in insert_cols:
        if col not in df.columns:
            df[col] = None

    # Replace NaN with None
    df_clean = df[insert_cols].where(pd.notnull(df[insert_cols]), None)
    data = [tuple(row) for row in df_clean.values]

    # Insert data using executemany
    query = """
        INSERT INTO metadata ([Table], [Field], [Description])
        VALUES (?, ?, ?)
    """
    
    try:
        cursor.executemany(query, data)
        conn.commit()
        print(f"Successfully ingested {len(data)} metadata rows.")
    except Exception as e:
        print(f"Error during ingestion: {e}")
        conn.rollback()
    finally:
        conn.close()
    print("Metadata ingestion completed.")

if __name__ == "__main__":
    # Get the directory of the current script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file = os.path.join(base_dir, 'files', 'metadata.csv')
    ingest_metadata(csv_file)
