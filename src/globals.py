import secrets
from read_config import read_config

secret_key = secrets.token_hex(64)  # Generate a random secret key to encode/decode JWT tokens

status_codes = {
    'success': 200,
    'api_error': 400,
    'not_found': 404,
    'internal_error': 500
} # Status codes for the API

config_vars = read_config()  # Read the configuration file