#use a slim Python base image
FROM python:3.11-slim

# Install system dependencies (GLPK)
RUN apt-get update && apt-get install -y \
    glpk-utils \
    libglpk-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment to avoid Streamlit asking for config
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of your app
COPY . /app
WORKDIR /app

# Start Streamlit
CMD ["streamlit", "run", "nirad_GUI.py"]
