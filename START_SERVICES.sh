#!/bin/bash

# Start both Streamlit and FastAPI in background
cd /app

# Start FastAPI in background
uvicorn src.web.app:app --host 0.0.0.0 --port 8000 &

# Wait a bit for FastAPI to start
sleep 5

# Start Streamlit (foreground)
streamlit run src/web/streamlit_app.py --server.port $PORT --server.headless true --server.address 0.0.0.0