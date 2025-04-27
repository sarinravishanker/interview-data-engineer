import os
import pandas as pd
from datetime import datetime
import logging
from db_config import get_db_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("load_csv.log", mode="a")
    ]
)

class SalesDataProcessor:
    def __init__(self, files):
        self.files = files
        self.data = None

    def read_csv(self, file_path):
        """Read a CSV file into a DataFrame."""
        try:
            self.data = pd.read_csv(file_path, sep=",", encoding="utf-8")
            logging.info(f"Successfully read CSV file: {file_path}")
            logging.info(f"Preview of the data:\n{self.data.head()}")
            logging.info(f"Shape of the data: {self.data.shape}")
        except Exception as e:
            logging.error(f"Error reading CSV file {file_path}: {e}")
            raise

    def write_to_db(self, file_path):
        """Write the data to the database."""
        conn = get_db_connection()  # Use the reusable database connection
        try:
            cursor = conn.cursor()
            for _, row in self.data.iterrows():
                cursor.execute(
                    """
                    INSERT INTO raw__sales.fct_sales (
                        saleid, productid, productname, brand, category, retailerid, retailername, 
                        channel, location, quantity, price, date, _etl_timestamp, sourcefilename
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (saleid) DO NOTHING
                    """,
                    (
                        row["SaleID"], row["ProductID"], row["ProductName"], row["Brand"], row["Category"],
                        row["RetailerID"], row["RetailerName"], row["Channel"], row["Location"], row["Quantity"],
                        row["Price"], row["Date"], datetime.now(), file_path.split("/")[-1]
                    )
                )
            conn.commit()
            logging.info(f"Successfully wrote data from {file_path} to the database.")
        except Exception as e:
            conn.rollback()  # Roll back the entire transaction
            logging.error(f"Error writing to database for file {file_path}: {e}")
            raise  # Re-raise the exception to fail the task
        finally:
            cursor.close()
            conn.close()

    def process_files(self):
        """Process all files."""
        for file in self.files:
            try:
                logging.info(f"Processing file: {file}")
                self.read_csv(file)
                self.write_to_db(file)
            except Exception as e:
                logging.error(f"Failed to process file {file}: {e}")
                raise  # Re-raise the exception to ensure Airflow marks the task as FAILED

def execute_load_csv():
    """Encapsulate the logic to process CSV files."""
    csv_dir = "/opt/airflow/csv_files"
    files = [os.path.join(csv_dir, file) for file in os.listdir(csv_dir) if file.endswith(".csv")]
    processor = SalesDataProcessor(files)
    processor.process_files()

# Ensure the script can still be executed directly
if __name__ == "__main__":
    execute_load_csv()
