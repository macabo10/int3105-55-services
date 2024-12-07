# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt .

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install curl
RUN apt-get update && apt-get install -y curl

# Copy the startup script into the container
COPY startup.sh /usr/local/bin/startup.sh

# Make the script executable
RUN chmod +x /usr/local/bin/startup.sh

# Set the entrypoint to the startup script
ENTRYPOINT ["/usr/local/bin/startup.sh"]

# Expose the port the app runs on
EXPOSE 4007

# Run the Python script when the container launches
CMD ["python", "-u" , "app.py"]