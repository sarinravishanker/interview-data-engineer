import sys
import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from scripts.load_csv import SalesDataProcessor

# Add the parent directory of 'scripts' to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock database configuration
db_config = {
    "dbname": "testdb",
    "user": "testuser",
    "password": "testpass",
    "host": "localhost",
    "port": 5433
}

# Mock CSV data
mock_csv_data = pd.DataFrame({
    "SaleID": [1, 2, 3],
    "ProductID": ["P1", "P2", "P3"],
    "ProductName": ["Product1", "Product2", "Product3"],
    "Brand": ["BrandA", "BrandB", "BrandC"],
    "Category": ["Category1", "Category2", "Category3"],
    "RetailerID": [101, 102, 103],
    "RetailerName": ["Retailer1", "Retailer2", "Retailer3"],
    "Channel": ["Online", "Offline", "Online"],
    "Location": ["Location1", "Location2", "Location3"],
    "Quantity": [10, 20, 30],
    "Price": [100.0, 200.0, 300.0],
    "Date": ["2024-01-01", "2024-01-02", "2024-01-03"]
})

@pytest.fixture
def mock_csv_file(tmp_path):
    """Fixture to create a temporary CSV file."""
    csv_file = tmp_path / "test.csv"
    mock_csv_data.to_csv(csv_file, index=False)
    return str(csv_file)

@patch("psycopg2.connect")
def test_read_csv(mock_connect, mock_csv_file):
    """Test reading a CSV file."""
    processor = SalesDataProcessor([mock_csv_file], db_config)
    processor.read_csv(mock_csv_file)

    # Assert the data was read correctly
    assert not processor.data.empty
    assert len(processor.data) == len(mock_csv_data)
    assert list(processor.data.columns) == list(mock_csv_data.columns)

@patch("psycopg2.connect")
def test_write_to_db(mock_connect, mock_csv_file):
    """Test writing data to the database."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    processor = SalesDataProcessor([mock_csv_file], db_config)
    processor.read_csv(mock_csv_file)
    processor.write_to_db(mock_csv_file)

    # Assert database connection and cursor were called
    mock_connect.assert_called_once_with(**db_config)
    mock_conn.cursor.assert_called()

    # Assert data was inserted into the database
    assert mock_cursor.execute.call_count == len(mock_csv_data)

    # Ensure the transaction was committed
    mock_conn.commit.assert_called_once()

@patch("psycopg2.connect")
def test_process_files(mock_connect, mock_csv_file):
    """Test processing multiple CSV files."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    processor = SalesDataProcessor([mock_csv_file], db_config)
    processor.process_files()

    # Assert database connection and cursor were called
    mock_connect.assert_called_once_with(**db_config)
    mock_conn.cursor.assert_called()

    # Assert data was inserted into the database
    assert mock_cursor.execute.call_count == len(mock_csv_data)

    # Ensure the transaction was committed
    mock_conn.commit.assert_called_once()
