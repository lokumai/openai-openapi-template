#!/bin/bash
# deepwiki_scraping_runner.sh

# Scripts and requirements files directory
TOOL_DIR="scripts"
SCRIPT_NAME="deepwiki_scraping_script.py"
REQUIREMENTS_FILE="requirements_deepwiki_scraping.txt"
VENV_NAME=".venv-deepwiki-scraping-temp"

echo "Creating temporary virtual environment: $VENV_NAME"
uv venv "$VENV_NAME"

# Activate virtual environment
source "$VENV_NAME/bin/activate"

echo "Installing required packages..."
uv pip install -r "$TOOL_DIR/$REQUIREMENTS_FILE"

echo "Running scraping script..."
python "$TOOL_DIR/$SCRIPT_NAME"

echo "Deactivating virtual environment..."
deactivate

echo "Removing temporary virtual environment..."
rm -rf "$VENV_NAME"

echo "Process completed."