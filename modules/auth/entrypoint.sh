#! /usr/bin/bash
set -e

# Wait for database to be online
/app/.venv/bin/python /app/src/initialize.py

# Start FastAPI
cd /app/src

echo "Running UVicorn "
if [ "$RUN_STAGE" = 'DEV' ]; then
  /app/.venv/bin/uvicorn main:app --host 0.0.0.0 --reload;
else
  /app/.venv/bin/uvicorn main:app --host 0.0.0.0;
fi;
