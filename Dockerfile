# syntax=docker/dockerfile:1.2
FROM --platform=linux/amd64 python:3.10-slim

# Set environment variables to prevent Python from writing pyc files and to ensure output is sent straight to the terminal
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
WORKDIR /app

# Copy the requirements.txt file into the working directory
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Copy the entire project into the working directory
COPY . /app/

# Expose port 8000
EXPOSE 8000

# Run Gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "campable_server.wsgi:application"]
