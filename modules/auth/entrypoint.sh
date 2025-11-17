#! /usr/bin/bash
set -e

# Wait for services to be online
python /app/src/initialize.py

# Run database migrations
echo "Running database migrations..."
cd /app
alembic upgrade head

# Start FastAPI
cd /app/src

echo "Running Uvicorn"
if [ "$RUN_STAGE" = 'DEV' ]; then
  uvicorn main:app --host 0.0.0.0 --reload;
else
  uvicorn main:app --host 0.0.0.0;
fi;
