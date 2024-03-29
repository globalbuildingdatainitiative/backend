#! /usr/bin/bash
set -e

echo "Running Post-Sync Copy"
for podname in $(kubectl -n ASYNC_STRAWBERRY get pods -l app=backend -o json| jq -r '.items[].metadata.name'); do
  kubectl cp ASYNC_STRAWBERRY/"${podname}":/app/graphql/schema.graphql graphql/schema.graphql;
done
