#!/bin/bash
set -e

cd /app

echo "Starting Scrapyd server..."
scrapyd &

echo "Waiting for Scrapyd to start..."
sleep 5

echo "Deploying spider to Scrapyd..."
scrapyd-deploy local -p books_scraper

echo "Spider deployed!"
echo "Scrapyd: http://0.0.0.0:6800"

wait
