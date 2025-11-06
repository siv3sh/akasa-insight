#!/bin/bash

# Script to run the Streamlit dashboard for Akasa Air

echo "Starting Akasa Air Streamlit Dashboard..."

# Start the Streamlit service using docker-compose
docker-compose up -d streamlit

echo "Dashboard is now running at http://localhost:8501"
echo "Press Ctrl+C to stop the dashboard"

# Keep the script running to show logs
docker-compose logs -f streamlit