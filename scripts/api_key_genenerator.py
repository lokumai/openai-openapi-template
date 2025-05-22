"""
API Key Generator Script

This script is used to generate API keys for new users.
API keys are generated in the format sk-{username}-{base64_encoded_data}.
The encoded data includes username, creation timestamp, and HMAC signature.

Usage:
    python generate_api_key.py <username> <secret_key>

Example:
    python generate_api_key.py new_user mock-secret-key-123456789
"""

import base64
import json
import sys
import argparse
import hmac
import hashlib
from datetime import datetime
from loguru import logger

logger.add("logs/api_key_generator.log")

def generate_api_key(username: str, secret_key: str) -> str:
    """
    Generates an API key for the given username using a secret key.
    
    Args:
        username (str): Username to generate API key for
        secret_key (str): Secret key for API key generation
        
    Returns:
        str: Generated API_KEY (ACCESS_KEY, ACCESS_TOKEN)
    """
    # Create encoded API key with timestamp
    timestamp = int(datetime.now().timestamp())
    data = {
        "username": username,
        "created_at": timestamp
    }
    
    # Debug için JSON verilerini logla
    json_data = {"username": username, "created_at": timestamp}
    json_str = json.dumps(json_data)
    logger.debug(f"JSON data for signature: {json_str}")
    logger.debug(f"Secret key: {secret_key}")
    
    # Add HMAC signature for additional security
    signature = hmac.new(
        secret_key.encode(),
        json_str.encode(),
        hashlib.sha256
    ).hexdigest()
    
    logger.debug(f"Generated signature: {signature}")
    
    data["signature"] = signature
    
    # Create API key
    api_key = f"sk-{username}-" + base64.b64encode(
        json.dumps(data).encode()
    ).decode()
    
    return api_key, timestamp

def save_api_key(username: str, api_key: str, timestamp: int):
    """
    Save API key to api_keys.txt file in the same format as the shell script.
    
    Args:
        username (str): Username
        api_key (str): Generated API key
        timestamp (int): Creation timestamp
    """
    formatted_timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    with open("api_keys.txt", "a") as f:
        f.write(f"Username: {username}\n")
        f.write(f"API Key: {api_key}\n")
        f.write(f"Timestamp: {formatted_timestamp}\n")
        f.write("--------------------------------\n")

def main():
    parser = argparse.ArgumentParser(description="API Key Generator")
    parser.add_argument("username", help="Username to generate API key for")
    parser.add_argument("secret_key", help="Secret key for API key generation")
    args = parser.parse_args()
    
    try:
        api_key, timestamp = generate_api_key(args.username, args.secret_key)
        
        print("\nAPI Key generated:")
        print(f"Username: {args.username}")
        print(f"API Key: {api_key}")
        
        # Save to api_keys.txt
        save_api_key(args.username, api_key, timestamp)
        print("\nAPI Key saved to api_keys.txt")
        
        print("\nUsage example:")
        print('curl -X POST "http://localhost:8000/v1/chat/completions" \\')
        print(f'     -H "Authorization: Bearer {api_key}" \\')
        print('     -H "Content-Type: application/json" \\')
        print('     -d \'{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hello!"}]}\'')
    
    except argparse.ArgumentError as e:
        print("Please provide a username and secret key", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 