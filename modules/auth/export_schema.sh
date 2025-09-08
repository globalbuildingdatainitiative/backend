#!/usr/bin/env sh
set -e

export SERVER_NAME=Projects Test
export SERVER_HOST=http://test.gbdi.io
export CONNECTION_URI=http://test.gbdi.io
export ROUTER_URL=http://test.gbdi.io
export API_KEY=DHALFKJDHALFJHDAJF
export SMTP_HOST=email-smtp.eu-central-2.amazonaws.com
export SMTP_PORT=5897
export SMTP_EMAIL=noreply@noreply.io
export SMTP_NAME=Test
export SMTP_PASSWORD=BEPr8mQV7A/jtUv/MGIGherhrye789hyr9ehabrgPMJF
export SMTP_USERNAME=AKIAW3MEGUGUE7NP

mkdir -p graphql
strawberry export-schema --app-dir ./src schema > graphql/schema.graphql

