#!/bin/bash
set -e

# create a new database genie
# create table events inside genie database with organization_id column

clickhouse client -n <<-EOSQL
    SET allow_experimental_json_type = 1;

    -- Create the database if it does not exist
    CREATE DATABASE IF NOT EXISTS genie;

    -- Create the new table with the updated schema
    CREATE TABLE IF NOT EXISTS genie.events (
    name LowCardinality(String),
    organization_id String,
    user_id String,
    payload Json,
    client_timestamp DateTime,
    server_timestamp DateTime
    ) ENGINE = MergeTree()
    ORDER BY (organization_id, user_id, name, client_timestamp);
EOSQL
