FROM python:3.8-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Install additional dependencies or tools if needed
RUN apt-get update && apt-get install -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8501
EXPOSE 8000

# Run Streamlit
# CMD ["sh", "-c", "streamlit run app.py --server.port=8501 --server.address=0.0.0.0"]

# Run Uvicorn for FastAPI
CMD ["sh", "-c",  "uvicorn main:app --host 0.0.0.0 --port 8000"]