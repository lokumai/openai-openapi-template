#!/bin/bash

# Önce eski uygulamayı durdur
echo "Stopping existing application..."
pkill -f "uvicorn main:app"

# 2 saniye bekle
sleep 2

# FastAPI uygulamasını başlat (Gradio entegre edilmiş)
echo "Starting application..."
uv run uvicorn main:app --host 0.0.0.0 --port 7860 --reload

# Ctrl+C ile durdurma işlemini yakala
trap "echo 'Stopping application...'; pkill -f 'uvicorn main:app'; exit" INT

# Uygulamanın çalışmasını bekle
wait