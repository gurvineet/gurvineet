FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Make scripts executable
RUN chmod +x src/execution_harness.py src/test_kitchen.py

# Set Python path
ENV PYTHONPATH=/app/src

# Default command
CMD ["python", "src/execution_harness.py", "--help"]