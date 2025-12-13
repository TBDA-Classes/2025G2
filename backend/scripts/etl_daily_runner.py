'''
Daily ETL Runner - Demonstration Script

Intended to run daily to keep aggregated tables up to date.
The ETL queries v_data_status for the latest processed date and runs all ETL scripts
from that date to the current date.

'''

import subprocess
from datetime import date, timedelta
from typing import Optional
from sqlalchemy import text

from backend.database import AggregationSession


# List of ETL modules to run
ETL_MODULES = [
    "backend.scripts.etl_agg_sensor_stats",
    "backend.scripts.etl_agg_utilization",
    "backend.scripts.etl_agg_program_history",
    "backend.scripts.etl_agg_alerts",
    "backend.scripts.etl_agg_energy_daily",
]


def get_last_processed_date() -> Optional[date]:
    """
    Query v_data_status to find the most recent date with data.
    
    Returns:
        The last_date from the view, or None if no data exists.
    """
    
    with AggregationSession() as session:
        result = session.execute(text("SELECT last_date FROM v_data_status")).fetchone()
        if result and result.last_date:
            return result.last_date
        return None


def run_all_etls(from_date: date, to_date: date):
    """
    Run all ETL scripts for the given date range using subprocess.
    
    Params:
        from_date: Start date for processing
        to_date: End date for processing
    """
    from_str = str(from_date)
    to_str = str(to_date)
    
    print(f"\n{'='*60}")
    print(f"Running all ETLs for: {from_str} to {to_str}")
    print(f"{'='*60}\n")
    
    for module in ETL_MODULES:
        print(f"\n--- {module} ---")
        try:
            # Run each ETL as a subprocess with date range arguments
            result = subprocess.run(
                ["python", "-m", module, from_str, to_str]
            )
            
            if result.returncode == 0:
                print(f"✓ {module} completed")
            else:
                print(f"✗ {module} failed (exit code {result.returncode})")
                    
        except Exception as e:
            print(f"✗ {module} failed: {e}")


def main():
    """Main entry point for daily ETL execution."""
    #today = date.today()

    # For test purposes we pretend today is 03/03/2022
    today =  date(2022, 2, 24)  
    last_date = get_last_processed_date()
    
    if last_date is None:
        print("No existing data found. Run individual ETL scripts for full backfill.")
        return
    
    # Start from the day after last processed date
    from_date = last_date + timedelta(days=1)
    
    if from_date > today:
        print(f"Already up to date! Last processed: {last_date}")
        return
    
    print(f"Last processed date: {last_date}")
    print(f"Processing new data: {from_date} → {today}")
    
    run_all_etls(from_date, today)
    
    print(f"\n{'='*60}")
    print("Daily ETL run complete!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()