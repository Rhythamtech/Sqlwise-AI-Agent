import os
import pandas as pd
from db_connect import get_db_connection, run_bcp

USD_TO_INR_RATE = 83.0

def ingest_refunds(csv_path):
    """
    Ingests refunds from CSV into MSSQL table with USD to INR conversion using BCP for maximum speed.
    """
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    # Read CSV
    print("Reading and cleaning data...")
    df = pd.read_csv(csv_path)

    # Convert created_at to datetime to ensure MSSQL compatibility
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')

    # Calculate INR values
    if 'refund_amount_usd' in df.columns:
        df['refund_amount_inr'] = df['refund_amount_usd'] * USD_TO_INR_RATE

    # Prepare columns to match table schema exactly
    insert_cols = [
        'refund_id', 'created_at', 'order_item_id', 'order_id', 
        'refund_amount_usd', 'refund_amount_inr'
    ]
    for col in insert_cols:
        if col not in df.columns:
            df[col] = None

    # Replace NaN/NaT with empty string for BCP compatibility
    df_clean = df[insert_cols].fillna('')

    # Save to temp file for BCP
    temp_csv = "temp_refunds_bcp.csv"
    print(f"Saving temporary data for BCP...")
    df_clean.to_csv(temp_csv, sep='|', index=False, header=False)

    # Run BCP
    try:
        success = run_bcp('refunds', temp_csv, separator='|')
        if success:
            print("Refunds ingestion completed via BCP.")
    finally:
        if os.path.exists(temp_csv):
            os.remove(temp_csv)

if __name__ == "__main__":
    # Get the directory of the current script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file = os.path.join(base_dir, 'files', 'refunds.csv')
    ingest_refunds(csv_file)
