import os
import pandas as pd
import psycopg2
from datetime import datetime
import logging

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
    def __init__(self, files, db_config):
        self.files = files
        self.db_config = db_config
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
        conn = psycopg2.connect(**self.db_config)
        try:
            cursor = conn.cursor()
            for _, row in self.data.iterrows():
                try:
                    cursor.execute(
                        """
                        INSERT INTO raw__sales.fct_sales (
                            saleid, productid, productname, brand, category, retailerid, retailername, 
                            channel, location, quantity, price, date, _etl_timestamp, sourcefilename
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (saleid) DO NOTHING;
                        """,
                        (
                            row["SaleID"], row["ProductID"], row["ProductName"], row["Brand"], row["Category"],
                            row["RetailerID"], row["RetailerName"], row["Channel"], row["Location"], row["Quantity"],
                            row["Price"], row["Date"], datetime.now(), file_path.split("/")[-1]
                        )
                    )
                except Exception as e:
                    logging.error(f"Error inserting row into database: {e}")
            conn.commit()
            logging.info(f"Successfully wrote data from {file_path} to the database.")
        except Exception as e:
            logging.error(f"Error writing to database for file {file_path}: {e}")
            raise
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

if __name__ == "__main__":
    csv_dir = "/Users/sarinravishanker/github-sarin/interview-data-engineer/csv_files"
    files = [os.path.join(csv_dir, file) for file in os.listdir(csv_dir) if file.endswith(".csv")]
    db_config = {
        "dbname": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "host": os.getenv("POSTGRES_HOST"),
        "port": 5432
    }

    processor = SalesDataProcessor(files, db_config)
    processor.process_files()
