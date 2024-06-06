import secrets

secret_key = secrets.token_hex(64)  # Generate a random secret key to encode/decode JWT tokens

status_codes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
} # Status codes for the API