# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt .

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 4000

# Run the gunicorn server when the container launches
CMD ["gunicorn", "--bind", "0.0.0.0:4000", "--workers", "10", "--threads", "5", "message_queue:app"]
# CMD ["python3", "-u", "message_queue.py"]