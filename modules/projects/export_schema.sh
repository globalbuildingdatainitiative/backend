#!/usr/bin/env sh
set -e
mkdir -p graphql

export SERVER_NAME=Organization Test
export SERVER_HOST=http://test.gbdi.io
export MONGO_HOST=localhost
export MONGO_USER=testuser
export MONGO_PASSWORD=mypassword
export MONGO_DB=organization
export MONGO_PORT=27017
export SUPERTOKENS_CONNECTION_URI=http://test.gbdi.io
export SUPERTOKENS_API_KEY=DHALFKJDHALFJHDAJF

strawberry export-schema --app-dir ./src schema > graphql/schema.graphql

