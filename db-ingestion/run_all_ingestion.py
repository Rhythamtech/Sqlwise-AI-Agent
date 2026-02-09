import os
import subprocess

def run_ingestion_scripts():
    """
    Runs all ingestion scripts in the current directory.
    """
    scripts = [
        # 'metadata.py',
        # 'products.py',
         'sessions.py',
        # 'pageviews.py',
        # 'orders.py',
        # 'order_items.py',
        # 'refunds.py'
    ]
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    for script in scripts:
        script_path = os.path.join(base_path, script)
        print(f"Running {script}...")
        try:
            # Run the script using the current python interpreter
            subprocess.run(['python3', script_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running {script}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while running {script}: {e}")

if __name__ == "__main__":
    run_ingestion_scripts()
