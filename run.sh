#!/bin/bash

# Önce eski uygulamaları durdur
echo "Stopping existing applications..."
pkill -f "uvicorn main:app"
pkill -f "python gradio_chatbot.py"

# 2 saniye bekle
sleep 2

# FastAPI uygulamasını arka planda başlat
echo "Starting FastAPI application..."
uv run uvicorn main:app --host 0.0.0.0 --port 7860 --reload &
FASTAPI_PID=$!

# 5 saniye bekle (FastAPI'nin başlaması için)
sleep 5

# Gradio uygulamasını başlat
echo "Starting Gradio application..."
uv run python gradio_chatbot.py &
GRADIO_PID=$!

# Uygulamaların çalışmasını bekle
echo "Applications are running..."
echo "FastAPI: http://localhost:7860"
echo "Gradio: http://localhost:7861"
echo "Press Ctrl+C to stop all applications"

# Ctrl+C ile durdurma işlemini yakala
trap "echo 'Stopping applications...'; kill $FASTAPI_PID $GRADIO_PID; exit" INT

# Uygulamaların çalışmasını bekle
wait