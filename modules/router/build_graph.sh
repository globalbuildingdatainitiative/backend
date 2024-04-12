#! /bin/bash
set -e

echo "Running Rover"
rover supergraph compose --elv2-license accept --config config/supergraph-config.yaml > /config/supergraph.graphql
echo "Moving Configs"
cp config/router.yaml /config/router.yaml