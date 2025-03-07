FROM python:3.9.18-bookworm

# Make /data, /videos, and port configurable with environment variables
ARG PORT=4000
ARG HOST=0.0.0.0

WORKDIR /app

# Copy your application code
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Set the environment variables
ENV PORT=$PORT
ENV HOST=$HOST

# Expose the specified port
EXPOSE $PORT

# Start the application
CMD ["python3", "src/api.py"]