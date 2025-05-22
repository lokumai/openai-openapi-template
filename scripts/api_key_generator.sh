#!/bin/bash

# sudo apt install jq
# chmod +x scripts/api_key_generator.sh
# ./scripts/api_key_generator.sh admin

# Usage: ./generate_api_key.sh <username> <secret_key>

# Check arguments
if [ "$#" -ne 2 ]; then
    echo "Please provide a username and secret key."
    echo "Example usage: ./generate_api_key.sh admin your-secret-key"
    exit 1
fi

USERNAME="$1"
SECRET_KEY="$2"
TIMESTAMP=$(date +%s)

# Create JSON payload
JSON_PAYLOAD=$(jq -n \
    --arg username "$USERNAME" \
    --arg created_at "$TIMESTAMP" \
    '{username: $username, created_at: ($created_at | tonumber)}'
)

# Generate HMAC signature
SIGNATURE=$(echo -n "$JSON_PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET_KEY" | sed 's/^.* //')

# Add signature to JSON
JSON_WITH_SIG=$(echo "$JSON_PAYLOAD" | jq --arg sig "$SIGNATURE" '. + {signature: $sig}')

# Base64 encode the JSON
ENCODED=$(echo -n "$JSON_WITH_SIG" | base64 | tr -d '\n')

# Build the API key
API_KEY="sk-${USERNAME}-${ENCODED}"

# Output
echo
echo "API Key generated:"
echo "Username: $USERNAME"
echo "API Key: $API_KEY"

# Save to file
echo "Username: $USERNAME" >> api_key.txt
echo "API Key: $API_KEY" >> api_key.txt
echo "Timestamp: $TIMESTAMP" >> api_key.txt
echo "--------------------------------" >> api_key.txt
echo 
echo "API Key saved to api_key.txt"

# Usage example
cat <<EOF

Usage example:
curl -X POST "http://localhost:8000/v1/chat/completions" \\
     -H "Authorization: Bearer $API_KEY" \\
     -H "Content-Type: application/json" \\
     -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hello!"}]}'

EOF
