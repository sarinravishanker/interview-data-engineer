import pandas as pd
import psycopg2
from psycopg2 import sql
from datetime import datetime

class SalesDataProcessor:
    def __init__(self, csv_path, db_config):
        self.csv_path = csv_path
        self.db_config = db_config
        self.data = None

    def read_csv(self):
        """Reads the CSV file into a Pandas DataFrame."""
        self.data = pd.read_csv(self.csv_path, sep=",", encoding="utf-8")
        print("Preview of the data:")
        print(self.data.head())
        print(self.data.shape)

    def create_schema_and_table(self):
        """Creates the schema, table, and index on SaleID if it does not exist."""
        create_schema_query = "CREATE SCHEMA IF NOT EXISTS raw__sales;"
        create_table_query = """
        CREATE TABLE IF NOT EXISTS raw__sales.fct_sales (
            SaleID INT PRIMARY KEY,
            ProductID TEXT,
            ProductName TEXT,
            Brand TEXT,
            Category TEXT,
            RetailerID INT,
            RetailerName TEXT,
            Channel TEXT,
            Location TEXT,
            Quantity TEXT,
            Price TEXT,
            Date DATE,
            _etl_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            filename TEXT
        );
        """
        create_index_query = """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_sale_id ON raw__sales.fct_sales (SaleID);
        """
        with psycopg2.connect(**self.db_config) as conn:
            with conn.cursor() as cur:
                cur.execute(create_schema_query)
                cur.execute(create_table_query)
                cur.execute(create_index_query)
                conn.commit()

    def write_to_db(self):
        """Writes the DataFrame to the PostgreSQL database."""
        with psycopg2.connect(**self.db_config) as conn:
            with conn.cursor() as cur:
                for _, row in self.data.iterrows():
                    insert_query = sql.SQL("""
                        INSERT INTO raw__sales.fct_sales (
                            saleid, productid, productname, brand, category, retailerid, retailername, 
                            channel, location, quantity, price, date, _etl_timestamp, filename
                        ) VALUES (
                            {saleid}, {productid}, {productname}, {brand}, {category}, {retailerid}, {retailername}, 
                            {channel}, {location}, {quantity}, {price}, {date}, {etltimestamp}, {filename}
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
                        filename=sql.Literal(self.csv_path.split("/")[-1])
                    )
                    cur.execute(insert_query)
                conn.commit()

if __name__ == "__main__":
    csv_path = "/Users/sarinravishanker/github-sarin/interview-data-engineer/generated_sales_data.csv"
    db_config = {
        "dbname": "sales",
        "user": "postgres",
        "password": "mysecretpassword",
        "host": "localhost",  # Use 'postgres' if running on Linux or custom Docker network
        "port": 5432
    }

    processor = SalesDataProcessor(csv_path, db_config)
    processor.read_csv()
    processor.create_schema_and_table()
    processor.write_to_db()
