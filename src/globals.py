import secrets
from read_config import read_config
import logging

secret_key = secrets.token_hex(64)  # Generate a random secret key to encode/decode JWT tokens

status_codes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
} # Status codes for the API

config_vars = read_config()  # Read the configuration file

logging.basicConfig(filename='log_file.log')
logger = logging.getLogger('logger')