FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    chromium chromium-driver && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY /src/script.py .

# Run script
CMD ["python", "script.py"]