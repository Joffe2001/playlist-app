#Dockerfile- Flask backend

# Use the official Python base image
FROM python:3.12.3

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt /app/

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY backend /app/backend
COPY frontend /app/frontend

# Set the PYTHONPATH environment variable
ENV PYTHONPATH="/app/backend"

# Set the environment variable for Flask
ENV FLASK_APP=app.py

# Expose the port on which the Flask application will run
EXPOSE 5000

# Run the Flask application
CMD ["flask", "run", "--host=0.0.0.0"]