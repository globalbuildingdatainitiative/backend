#!/usr/bin/env sh
set -e

# Not Important
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

# Important
export POSTGRES_USER=postgresuser
export POSTGRES_PASSWORD=adgakj2354jhsklh78354
export POSTGRES_HOST=localhost
export POSTGRES_DB=meta_data
export POSTGRES_PORT=5434

alembic revision --autogenerate