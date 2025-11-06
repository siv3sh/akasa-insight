#!/bin/bash

# Start the Akasa Air Combined Application

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Akasa Air Combined Application${NC}"

# Check if data engineering outputs exist
if [ ! -d "./outputs" ] || [ -z "$(ls -A ./outputs)" ]; then
  echo -e "${YELLOW}Warning: No output files found. Please run the data engineering pipeline first:${NC}"
  echo "  python src/main.py"
  echo ""
fi

# Function to clean up background processes on exit
cleanup() {
  echo -e "\n${YELLOW}Stopping servers...${NC}"
  kill $FRONTEND_PID $API_PID 2>/dev/null || true
  wait $FRONTEND_PID $API_PID 2>/dev/null
  echo -e "${GREEN}Servers stopped.${NC}"
  exit 0
}

# Set up cleanup function to run on script exit
trap cleanup EXIT INT TERM

# Start API server in background
echo -e "${GREEN}Starting API server...${NC}"
cd ./akasa-insight-nexus-main/server
npm start > /tmp/akasa-api.log 2>&1 &
API_PID=$!
cd ../../

# Start frontend in background
echo -e "${GREEN}Starting frontend...${NC}"
cd ./akasa-insight-nexus-main
npm run dev > /tmp/akasa-frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a moment for servers to start
sleep 3

# Check if servers are running
if kill -0 $API_PID 2>/dev/null && kill -0 $FRONTEND_PID 2>/dev/null; then
  echo -e "${GREEN}Both servers are running successfully!${NC}"
  echo ""
  echo -e "${YELLOW}Access the application:${NC}"
  echo -e "  Frontend: ${GREEN}http://localhost:8080${NC}"
  echo -e "  API Server: ${GREEN}http://localhost:3001${NC}"
  echo ""
  echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
  
  # Wait for both processes to complete or be terminated
  wait $API_PID $FRONTEND_PID
else
  echo -e "${RED}Error: One or both servers failed to start${NC}"
  echo "Check logs in /tmp/akasa-api.log and /tmp/akasa-frontend.log"
  exit 1
fi