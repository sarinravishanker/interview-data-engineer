-- Create Airflow database
CREATE DATABASE airflow;

-- Create Airflow user
CREATE USER airflow WITH PASSWORD 'airflow';

-- Grant privileges to Airflow user
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;

-- Connect to the Airflow database
\connect airflow

-- Create a dedicated schema for Airflow
CREATE SCHEMA airflow AUTHORIZATION airflow;

-- Grant usage and create privileges on the Airflow schema
GRANT USAGE ON SCHEMA airflow TO airflow;
GRANT CREATE ON SCHEMA airflow TO airflow;

-- Set the default schema for the Airflow user
ALTER ROLE airflow SET search_path TO airflow;
