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
    data = {
        "username": username,
        "created_at": int(datetime.now().timestamp())
    }
    
    # Add HMAC signature for additional security
    signature = hmac.new(
        secret_key.encode(),
        json.dumps(data).encode(),
        hashlib.sha256
    ).hexdigest()
    
    data["signature"] = signature
    
    # Create API key
    api_key = f"sk-{username}-" + base64.b64encode(
        json.dumps(data).encode()
    ).decode()
    
    return api_key

def main():
    parser = argparse.ArgumentParser(description="API Key Generator")
    parser.add_argument("username", help="Username to generate API key for")
    parser.add_argument("secret_key", help="Secret key for API key generation")
    args = parser.parse_args()
    
    try:
        api_key = generate_api_key(args.username, args.secret_key)
        print("\nAPI Key generated:")
        print(f"Username: {args.username}")
        print(f"API Key: {api_key}")
        print("\nUsage example:")
        print('curl -X POST "http://localhost:8000/v1/chat/completions" \\')
        print(f'     -H "Authorization: Bearer {api_key}" \\')
        print('     -H "Content-Type: application/json" \\')
        print('     -d \'{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hello!"}]}\'')
    
        # Save the API key to a file
        with open("api_key.txt", "w") as f:
            f.write(api_key)
            print("\nAPI Key saved to api_key.txt")
    except argparse.ArgumentError as e:
        print("Please provide a username and secret key", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 