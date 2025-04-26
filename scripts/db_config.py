import os
import psycopg2

def get_db_config():
    """Retrieve database configuration from environment variables."""
    return {
        "dbname": os.getenv("POSTGRES_DB", "sales"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "mysecretpassword"),
        "host": os.getenv("POSTGRES_HOST", "postgres"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
    }

def get_db_connection():
    """Establish a connection to the database using the configuration."""
    config = get_db_config()
    return psycopg2.connect(**config)
