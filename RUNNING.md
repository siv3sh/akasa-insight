# Running the Combined Application

To run the Akasa Air Data Engineering application with the frontend:

```bash
# Make sure you're in the project root directory
cd /Users/siv3sh/Downloads/AkasaAir-DataEngineer\ 2

# Run the combined application
./start_combined.sh
```

The application will be available at:
- Frontend: http://localhost:8080
- API Server: http://localhost:3001

Press Ctrl+C to stop both servers.

## Prerequisites

Make sure you have run the data engineering pipeline to generate output files:

```bash
python src/main.py
```