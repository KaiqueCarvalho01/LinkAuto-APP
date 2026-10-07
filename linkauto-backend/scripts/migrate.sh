#!/bin/sh
# Release step: bring the database schema to the latest Alembic revision.
#
# Run it ONCE per deploy, before the new app version receives traffic (a CI/CD pre-deploy
# step, a Kubernetes Job or init container, or `docker compose run --rm migrate`). Do not
# run it from every app replica's startup: concurrent upgrades race on the same schema.
set -eu

cd "$(dirname "$0")/.."

echo "Applying migrations to the configured DATABASE_URL..."
alembic upgrade head
alembic current
