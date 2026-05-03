#!/bin/bash

# Exit on error
set -e

echo "--- Installing Test Dependencies ---"
# Ensure we have the latest dev dependencies
pip install -r requirements-dev.txt

echo "--- Running Backend Tests with Coverage ---"
# Set PYTHONPATH to root so tests can find backend module
export PYTHONPATH=$PYTHONPATH:.

# Run tests with:
# - verbose output
# - coverage for the backend directory
# - term-missing report (stdout)
# - xml report (for CI/CD pipelines)
# - fail-under 70% threshold
pytest tests/ -v \
    --cov=backend \
    --cov-report=term-missing \
    --cov-report=xml:coverage.xml \
    --cov-fail-under=100
