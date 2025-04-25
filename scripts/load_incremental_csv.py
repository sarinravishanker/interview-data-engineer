import os
import pandas as pd
import psycopg2
from psycopg2 import sql
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("load_incremental_csv.log", mode="a")
    ]
)

class IncrementalSalesDataProcessor:
    def __init__(self, csv_paths, db_config):
        self.csv_paths = csv_paths
        self.db_config = db_config
        self.data = None

    def get_max_sale_id(self):
        """Fetch the maximum SaleID from the database."""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COALESCE(MAX(SaleID), 0) FROM raw__sales.fct_sales;")
                    max_sale_id = cur.fetchone()[0]
                    logging.info(f"Max SaleID in the database: {max_sale_id}")
                    return max_sale_id
        except Exception as e:
            logging.error(f"Error fetching max SaleID from the database: {e}")
            raise

    def read_csv(self, csv_path, max_sale_id):
        """Reads a CSV file into a Pandas DataFrame and filters for new records."""
        try:
            self.data = pd.read_csv(csv_path, sep=",", encoding="utf-8")
            self.data = self.data[self.data["SaleID"] > max_sale_id]
            logging.info(f"Filtered data from {csv_path} with SaleID > {max_sale_id}")
            logging.info(f"Preview of the filtered data:\n{self.data.head()}")
            logging.info(f"Shape of the filtered data: {self.data.shape}")
        except Exception as e:
            logging.error(f"Error reading or filtering CSV file {csv_path}: {e}")
            raise

    def write_to_db(self, csv_path):
        """Writes the DataFrame to the PostgreSQL database."""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    for _, row in self.data.iterrows():
                        try:
                            insert_query = sql.SQL("""
                                INSERT INTO raw__sales.fct_sales (
                                    saleid, productid, productname, brand, category, retailerid, retailername, 
                                    channel, location, quantity, price, date, _etl_timestamp, sourcefilename
                                ) VALUES (
                                    {saleid}, {productid}, {productname}, {brand}, {category}, {retailerid}, {retailername}, 
                                    {channel}, {location}, {quantity}, {price}, {date}, {etltimestamp}, {sourcefilename}
                                )
                                ON CONFLICT (saleid) DO NOTHING;
                            """).format(
                                saleid=sql.Literal(row["SaleID"]),
                                productid=sql.Literal(row["ProductID"]),
                                productname=sql.Literal(row["ProductName"]),
                                brand=sql.Literal(row["Brand"]),
                                category=sql.Literal(row["Category"]),
                                retailerid=sql.Literal(row["RetailerID"]),
                                retailername=sql.Literal(row["RetailerName"]),
                                channel=sql.Literal(row["Channel"]),
                                location=sql.Literal(row["Location"]),
                                quantity=sql.Literal(row["Quantity"]),
                                price=sql.Literal(row["Price"]),
                                date=sql.Literal(row["Date"]),
                                etltimestamp=sql.Literal(datetime.now()),
                                sourcefilename=sql.Literal(csv_path.split("/")[-1])
                            )
                            cur.execute(insert_query)
                        except Exception as e:
                            logging.error(f"Error inserting row into database: {e}")
                    conn.commit()
                    logging.info(f"Successfully wrote data from {csv_path} to the database.")
        except Exception as e:
            logging.error(f"Error writing to database for file {csv_path}: {e}")
            raise

    def process_files(self):
        """Processes all CSV files incrementally."""
        max_sale_id = self.get_max_sale_id()
        for csv_path in self.csv_paths:
            try:
                logging.info(f"Processing file: {csv_path}")
                self.read_csv(csv_path, max_sale_id)
                if not self.data.empty:
                    self.write_to_db(csv_path)
                else:
                    logging.info(f"No new records to process in file: {csv_path}")
            except Exception as e:
                logging.error(f"Failed to process file {csv_path}: {e}")

if __name__ == "__main__":
    csv_dir = "/Users/sarinravishanker/github-sarin/interview-data-engineer/csv_files"
    csv_paths = [os.path.join(csv_dir, file) for file in os.listdir(csv_dir) if file.endswith(".csv")]
    db_config = {
        "dbname": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "host": os.getenv("POSTGRES_HOST"),
        "port": 5432
    }

    processor = IncrementalSalesDataProcessor(csv_paths, db_config)
    processor.process_files()
