from globals import revoked_tokens, logger, status_codes
import flask
from validate_token import validate_token


def logout():
    logger.info('POST /mail/logout')

    jwt_token = flask.request.headers.get('Authorization')
    
    jwt_token = validate_token(jwt_token)
    if isinstance(jwt_token, str):
        response = {'status': status_codes['api_error'], 'errors': jwt_token, 'results': None}
        return response
    
    revoked_tokens.add(jwt_token)

    response = {'status': status_codes['success'], 'errors': None, 'results': 'Logged out successfully'}
    return response

# end of logout.py