#!/bin/bash
echo "Running custom initialization script..."
# Add your custom commands here
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE EXTENSION IF NOT EXISTS vector;"