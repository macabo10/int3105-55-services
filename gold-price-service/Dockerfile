# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /gold-price-service

# Copy the current directory contents into the container at /app
COPY . /gold-price-service

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Expose the port the app runs on (Flask default is 5001)
# EXPOSE 5001

# Run the Python script when the container launches
CMD ["python", "gold-price-service.py"]