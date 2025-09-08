#!/usr/bin/env sh
set -e

BASEDIR=$(dirname $0)
NAMESPACE=auth
ROUTER_SCHEMA_DIR=$(dirname $BASEDIR)/router/schemas/$NAMESPACE

echo "Running Post-Sync Copy"
for podname in $(kubectl -n $NAMESPACE get pods -l app=backend -o json| jq -r '.items[].metadata.name'); do
  kubectl cp $NAMESPACE/"${podname}":/app/graphql/schema.graphql $BASEDIR/graphql/schema.graphql;
  if [[ -d "$ROUTER_SCHEMA_DIR" ]]
  then
    kubectl cp $NAMESPACE/"${podname}":/app/graphql/schema.graphql $ROUTER_SCHEMA_DIR/schema.graphql;
  fi
done