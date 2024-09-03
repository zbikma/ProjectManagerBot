#!/bin/bash

# Load environment variables from .env file
if [ -f ../.env ]; then
    export $(cat ../.env | xargs)
else
    echo ".env file not found! Please make sure it exists."
    exit 1
fi

# Prompt user for project description
read -p "Enter the project description: " PROJECT_DESCRIPTION

# Call the Python script to generate issues from the LLM and create them on GitHub
python3 generate_issues.py "$PROJECT_DESCRIPTION"
