# Use an official Python runtime as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Set PYTHONBUFFERED to ensure unbuffered mode for Python I/O
ENV PYTHONBUFFERED 1

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Set working directory to the "project" directory
WORKDIR /app/project

# Specify the command to run on container startup
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
