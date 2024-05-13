#! /usr/bin/bash
set -e

echo "Running Post-Sync Copy"
for podname in $(kubectl -n auth get pods -l app=backend -o json| jq -r '.items[].metadata.name'); do
  kubectl cp auth/"${podname}":/app/graphql/schema.graphql modules/auth/graphql/schema.graphql;
done
