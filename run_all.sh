#!/bin/bash

# check if mongodb docker container is running and start with docker compose docker/mongodb-docker-compose.yml
MONGO_CONTAINER_NAME="mongo"
echo "Starting MongoDB container..."
echo "Checking if MongoDB container is running..."
if ! docker ps | grep -q "$MONGO_CONTAINER_NAME"; then
    echo "Starting MongoDB container..."
    docker compose -f docker/mongodb-docker-compose.yaml up -d
    echo "MongoDB container started"
    echo "Waiting for MongoDB container to be ready..."
    sleep 10
    echo "MongoDB container is ready"
else
    echo "MongoDB container is already running"
fi

# stop existing application if running
echo "--------------------------------"
echo "checking if application is running..."
echo "Stopping existing application if running..."
pkill -f "uvicorn main:app"

# wait for the process to stop
sleep 2

# start FastAPI application with uvicorn integrated Gradio Application
echo "--------------------------------"
echo "Starting application..."
echo "--------------------------------"
uv run uvicorn main:app --host 0.0.0.0 --port 7860 --reload

# catch SIGINT (Ctrl+C) to stop the application gracefully
trap "echo 'Stopping application...'; pkill -f 'uvicorn main:app'; exit" INT

# wait for the application to run
wait