#!/bin/bash
# Entrypoint script for the Books Scraper Docker container.
# Starts Scrapyd server and deploys the spider automatically.

set -e

echo "Starting Scrapyd server..."
scrapyd &

# Wait for Scrapyd to be ready
echo "Waiting for Scrapyd to start..."
sleep 5

# Deploy the spider to Scrapyd
echo "Deploying spider to Scrapyd..."
scrapyd-deploy local -p books_scraper

echo "Spider deployed successfully!"
echo "Scrapyd is running at http://localhost:6800"
echo ""
echo "To run the spider, use:"
echo "curl http://localhost:6800/schedule.json -d project=books_scraper -d spider=books"

# Keep container running
wait