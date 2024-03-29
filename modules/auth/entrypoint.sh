#! /usr/bin/bash
set -e

# Start FastAPI
cd /app/src

echo "Running UVicorn "
if [ "$RUN_STAGE" = 'DEV' ]; then
  uvicorn main:app --host 0.0.0.0 --reload --no-access-log;
else
  uvicorn main:app --host 0.0.0.0;
fi;