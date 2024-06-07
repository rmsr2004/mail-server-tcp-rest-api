import logging as logger
import jwt
import psycopg2
import flask
from globals import status_codes, config_vars
from db_connection import db_connection
from validate_token import validate_token

def update_message(message_id: str):
    logger.info(f'PUT /mail/update/{message_id}')

    payload = flask.request.get_json()

    logger.debug(f'PUT /mail/update/{message_id} - payload: {payload}')

    #
    #   Validate detail
    #

    if 'details' not in payload:
        response = {'status': status_codes['api_error'], 'errors': 'Details not found', 'results': None}
        return response
    
    details = ['sent', 'read', 'replied', 'trashed']
    for detail in payload['details']:
        if detail not in details:
            response = {'status': status_codes['api_error'], 'errors': 'Invalid detail to udpdate', 'results': None}
            return response
    
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
        for detail in payload['details']:
            if detail == 'sent':
                # Query to verify if the user is the sender of the message
                statement = """
                    SELECT user_id
                    FROM messages
                    WHERE msg_id = %s AND user_id = %s;
                """
                values = (message_id, jwt_token['user_id'])
                cur.execute(statement, values)

                result = cur.fetchone()[0];
                if not result:
                    raise Exception('Message not found')
                
                if result != jwt_token['user_id']:
                    raise Exception('Unauthorized')
                
                # Query to update the message
                statement = """
                    UPDATE messages
                    SET is_draft = NOT is_draft
                    WHERE msg_id = %s;
                """
            
            else:
                # Query to check if the user is the recipient of the message
                statement = """
                    SELECT r.user_id
                    FROM receivers_messages AS rm
                    JOIN receivers AS r ON r.receiver_id = rm.receiver_id
                    WHERE msg_id = %s AND r.user_id = %s;
                """
                values = (message_id, jwt_token['user_id'])
                cur.execute(statement, values)

                result = cur.fetchone()[0];
                if not result:
                    raise Exception('Message not found')
                if result != jwt_token['user_id']:
                    raise Exception('Unauthorized')
                
                if detail == 'read':
                    # Query to update the message as read
                    statement = """
                        UPDATE receivers
                        SET is_read = NOT is_read
                        WHERE msg_id = %s AND user_id = %s;
                    """
                elif detail == 'replied':
                    statement = """
                        UPDATE receivers
                        SET is_replied = NOT is_replied
                        WHERE msg_id = %s AND user_id = %s;
                    """
                elif detail == 'trashed':
                    statement = """
                        UPDATE receivers
                        SET is_trashed = NOT is_trashed
                        WHERE msg_id = %s AND user_id = %s;
                    """

                values = (message_id, jwt_token['user_id'])
                cur.execute(statement, values)

            response = {'status': status_codes['success'], 'errors': None, 'results': 'Message updated'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT /mail/update/{message_id} - error: {error}')

        response = {'status': status_codes['internal_error'], 'errors': str(error), 'results': None}

    finally:
        if conn is not None:
            conn.close()

    return response