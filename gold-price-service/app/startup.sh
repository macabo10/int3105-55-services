#!/bin/bash

# Get container name from environment variable
CONTAINER_NAME=$CONTAINER_NAME

# Define the sidecar URL for the backend monitor
SIDECAR_URL=$SIDECAR_URL

# Send the information to the backend monitor
curl -X POST -H "Content-Type: application/json" -d '{
  "container_name": "'"$CONTAINER_NAME"'",
  "sidecar_url": "'"$SIDECAR_URL"'",
  "service_id": "'"$SERVICE_ID"'"
}' http://host.docker.internal:8080/register

# Execute the main application
exec "$@"