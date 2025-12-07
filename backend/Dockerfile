FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Initialize database if it doesn't exist
RUN python db.py

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
