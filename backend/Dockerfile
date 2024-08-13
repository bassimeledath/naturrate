# Use the official Python 3.10.9 image as the base image
FROM python:3.10.9-slim

# Set environment variables to ensure output is shown in the terminal immediately
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the relevant files into the container
COPY main.py .
COPY models.py .
COPY gcloud.json .
COPY .env .

# Set the Google Cloud credentials environment variable
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/gcloud.json"

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
