#! /usr/bin/bash
set -e
mkdir -p graphql
strawberry export-schema --app-dir ./src schema > graphql/schema.graphql

