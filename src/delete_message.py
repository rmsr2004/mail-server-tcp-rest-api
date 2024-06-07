import logging as logger
import jwt
import psycopg2
import flask
from globals import status_codes, config_vars
from db_connection import db_connection
from validate_token import validate_token

def update_message(message_id: str):
    logger.info(f'DELETE /mail/delete/{message_id}')

    payload = flask.request.get_json()

    logger.debug(f'DELETE /mail/delete/{message_id} - payload: {payload}')
    
    #
    # Validate Authorization header
    #

    jwt_token = flask.request.headers.get('Authorization')
    
    jwt_token = validate_token(jwt_token)
    if isinstance(jwt_token, str):
        response = {'status': status_codes['api_error'], 'errors': jwt_token, 'results': None}
        return response
    
    #
    # SQL query
    #

    conn = db_connection(config_vars)
    cur = conn.cursor()
    
    try:


    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'DELETE /mail/delete/{message_id} - error: {error}')

        response = {'status': status_codes['internal_error'], 'errors': str(error), 'results': None}

    finally:
        if conn is not None:
            conn.close()

    return response