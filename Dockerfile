FROM apache/airflow:2.6.3-python3.9

# Set working directory
WORKDIR /opt/airflow

# Copy dependency files
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt



