# Dockerfile for HambaLang Interpreter
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy interpreter
COPY interpreter/ ./interpreter/
COPY examples/ ./examples/

# Set entry point
ENTRYPOINT ["python", "interpreter/hamba_v2.py"]

# Default: run demo
CMD ["examples/full_demo.hl"]
