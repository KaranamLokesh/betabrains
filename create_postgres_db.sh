#!/bin/bash
# Create local PostgreSQL database and user for Betabrains app
set -e

DB_NAME="betabrains_db"
DB_USER="betabrains_user"
DB_PASS="betabrains_pass"

# Create user if not exists
psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || \
  psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"

# Create database if not exists
psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || \
  psql -U postgres -c "CREATE DATABASE $DB_NAME;"

# Grant privileges
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo "Database '$DB_NAME' and user '$DB_USER' are ready." 