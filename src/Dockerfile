FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# System dependencies for PostgreSQL and Firefox
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    firefox-esr \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scraper source code
COPY . .

# Run scraper
CMD ["python", "-m", "main"]
