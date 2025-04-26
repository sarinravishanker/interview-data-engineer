import pandas as pd
import logging
from db_config import get_db_connection  # Import the reusable database configuration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

def execute_load_csv_incremental():
    try:
        conn = get_db_connection()  # Use the reusable database connection
        cursor = conn.cursor()
        logging.info("Connected to the database successfully.")

        # Load the new CSV file
        csv_file_path = "/opt/airflow/csv_files/incremental_load_test_file/new_sales_data.csv"
        logging.info(f"Reading CSV file from path: {csv_file_path}")
        df = pd.read_csv(csv_file_path)

        # Filter out records already present in the database
        cursor.execute("SELECT MAX(SaleID) FROM raw__sales.fct_sales;")
        max_sale_id = cursor.fetchone()[0] or 0
        logging.info(f"Maximum SaleID in the database: {max_sale_id}")

        new_records = df[df["SaleID"] > max_sale_id]
        logging.info(f"Number of new records to insert: {len(new_records)}")

        # Insert new records into the database
        for _, row in new_records.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO raw__sales.fct_sales (
                        SaleID, ProductID, ProductName, Brand, Category, RetailerID, RetailerName, Channel, Location, Quantity, Price, Date
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, tuple(row))
            except Exception as e:
                logging.error(f"Error inserting record {row['SaleID']}: {e}")
                raise  # Raise an exception to fail the task

        conn.commit()
        logging.info(f"Inserted {len(new_records)} new records into raw__sales.fct_sales.")

    except Exception as e:
        logging.error(f"An error occurred during the incremental load process: {e}")
        raise  # Re-raise the exception to ensure Airflow marks the task as FAILED
    finally:
        if 'cursor' in locals():
            cursor.close()
            logging.info("Database cursor closed.")
        if 'conn' in locals():
            conn.close()
            logging.info("Database connection closed.")
