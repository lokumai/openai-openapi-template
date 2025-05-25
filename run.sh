#!/bin/bash

# stop existing application if running
echo "Stopping existing application..."
pkill -f "uvicorn main:app"

# wait for the process to stop
sleep 2

# start FastAPI application with uvicorn integrated Gradio Application
echo "Starting application..."
uv run uvicorn main:app --host 0.0.0.0 --port 7860 --reload

# catch SIGINT (Ctrl+C) to stop the application gracefully
trap "echo 'Stopping application...'; pkill -f 'uvicorn main:app'; exit" INT

# wait for the application to run
wait