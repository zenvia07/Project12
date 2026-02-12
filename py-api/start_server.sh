#!/bin/bash
echo "Starting Login API Server on port 3000..."
echo ""
echo "Server will be available at: http://localhost:3000"
echo "API Documentation: http://localhost:3000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
cd "$(dirname "$0")"
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 3000 --reload
