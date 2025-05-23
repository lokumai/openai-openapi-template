#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Run the Python script
python3 scripts/api_key_genenerator.py "$@" 

# ./scripts/generate_api_key.sh <username> <secret-key>