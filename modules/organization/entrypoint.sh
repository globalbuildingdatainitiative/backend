#! /usr/bin/bash
set -e

# Wait for database to be online
python /app/src/initialize.py

# Start FastAPI
cd /app/src

echo "Running UVicorn "
if [ "$RUN_STAGE" = 'DEV' ]; then
  uvicorn main:app --host 0.0.0.0 --reload;
else
  uvicorn main:app --host 0.0.0.0;
fi;
