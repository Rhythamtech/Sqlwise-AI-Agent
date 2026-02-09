import os
import pandas as pd
from db_connect import get_db_connection

def ingest_products(csv_path):
    """
    Ingests products from CSV into MSSQL table.
    """
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    # Read CSV
    df = pd.read_csv(csv_path)

    # Convert created_at to datetime to ensure MSSQL compatibility
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')

    # Connect to MSSQL
    conn = get_db_connection()
    if not conn:
        return
        
    cursor = conn.cursor()
    cursor.fast_executemany = True

    # Prepare data for insertion (convert NaN/NaT to None for MSSQL compatibility)
    insert_cols = ['product_id', 'created_at', 'product_name']
    
    # Ensure all columns exist
    for col in insert_cols:
        if col not in df.columns:
            df[col] = None

    # Replace NaN/NaT with None
    df_clean = df[insert_cols].where(pd.notnull(df[insert_cols]), None)
    data = [tuple(row) for row in df_clean.values]

    # Insert data using executemany
    query = """
        INSERT INTO products (product_id, created_at, product_name)
        VALUES (?, ?, ?)
    """
    
    try:
        cursor.executemany(query, data)
        conn.commit()
        print(f"Successfully ingested {len(data)} products.")
    except Exception as e:
        print(f"Error during ingestion: {e}")
        conn.rollback()
    finally:
        conn.close()
    print("Products ingestion completed.")

if __name__ == "__main__":
    # Get the directory of the current script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file = os.path.join(base_dir, 'files', 'products.csv')
    ingest_products(csv_file)
