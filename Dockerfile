# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Update package lists and install system dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    tesseract-ocr \
    pkg-config \
    nginx \
    openssl \
    --no-install-recommends && \
    ldconfig && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY ./afsp_app /app/afsp_app

# Create SSL certificates for HTTPS
RUN mkdir -p /etc/nginx/ssl && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.crt \
    -subj "/CN=localhost"

# Copy Nginx configuration
COPY ./nginx.conf /etc/nginx/nginx.conf

# Expose ports for HTTP and HTTPS
EXPOSE 80 443

# Start Nginx and the FastAPI application
CMD ["/bin/bash", "-c", "nginx && uvicorn afsp_app.app.main:app --host 0.0.0.0 --port 8000"]
