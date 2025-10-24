# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./src/

# Create directories for config and data
RUN mkdir -p /app/config /app/data

# Set Python path
ENV PYTHONPATH=/app/src

# Run the application
CMD ["python", "src/main.py"]
