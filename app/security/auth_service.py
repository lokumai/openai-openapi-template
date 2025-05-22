from app.config.secret import secret_config as secret
from fastapi import HTTPException, status, Security
from fastapi.security import APIKeyHeader 
from loguru import logger
import base64
import hmac
import hashlib
import json


api_key_header = APIKeyHeader(
            name="Authorization",
            scheme_name="ApiKeyAuth",
            description="API key in the format: sk-{username}-{base64_encoded_data}",
        )

class AuthService:
    def __init__(self):
        self.secret = secret
        self.api_key_header = api_key_header

    def decode_api_key(self, api_key: str) -> str:
        """Decode API key to extract username and verify signature."""
        logger.trace(f"BEGIN: api_key: {api_key}")
        try:
            if api_key.startswith("Bearer "):
                api_key = api_key[7:]

            if not api_key.startswith("sk-"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key format. Must start with 'sk-'",
                )

            parts = api_key.split("-", 2)
            if len(parts) != 3:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key format. Must be in format: sk-{username}-{base64_encoded_data}",
                )

            encoded_data = parts[2]
            try:
                decoded_data = base64.b64decode(encoded_data).decode()
                data = json.loads(decoded_data)
                logger.trace(f"Decoded data: {data}")
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid API key data format: {str(e)}",
                )

            # Debug için JSON verilerini logla
            json_data = {"username": data["username"], "created_at": data["created_at"]}
            json_str = json.dumps(json_data)
            logger.trace(f"JSON data for signature: {json_str}")
            logger.trace(f"Secret key: {self.secret.KEY}")

            expected_signature = hmac.new(
                self.secret.KEY.encode(),
                json_str.encode(),
                hashlib.sha256,
            ).hexdigest()

            logger.trace(f"Expected signature: {expected_signature}")
            logger.trace(f"Received signature: {data['signature']}")

            if data["signature"] != expected_signature:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid API key signature: {data['signature']} != {expected_signature}",
                )

            result = data["username"]
            logger.trace(f"END: result: {result}")
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid API key: {str(e)}",
            )


    def verify_credentials(self, api_key: str = Security(api_key_header)) -> str:
        """Verify API key and extract username."""
        logger.trace(f"BEGIN: api_key: {api_key}")
        username = self.decode_api_key(api_key)

        result = username
        logger.trace(f"END: result: {result}")
        return result