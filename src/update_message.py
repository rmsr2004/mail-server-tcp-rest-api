import jwt
import psycopg2
import flask
from globals import status_codes, config_vars, logger
from db_connection import db_connection
from validate_token import validate_token

def update_message(message_id: str):
    logger.info(f'PUT /mail/update/{message_id}')

    payload = flask.request.get_json()

    logger.debug(f'PUT /mail/update/{message_id} - payload: {payload}')

    #
    #   Validate payload
    #

    # list to store errors
    errors = []

    if 'details' not in payload:
        response = {'status': status_codes['api_error'], 'errors': 'Details not found', 'results': None}
        return response
    
    details = ['sent', 'read', 'replied', 'trashed']
    for detail in payload['details']:
        if detail not in details:
            errors.append(f'{detail} is not a valid detail\n')

    if errors != []:
        response = {'status': status_codes['api_error'], 'errors': " ".join(errors), 'results': None}
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
                values = (message_id,)
                cur.execute(statement, values)
            
            else:
                # Query to check if the user is the recipient of the message
                statement = """
                    SELECT mu.user_id
                    FROM messages_users AS mu
                    WHERE mu.msg_id = %s AND mu.user_id = %s;
                """
                values = (message_id, jwt_token['user_id'])
                cur.execute(statement, values)

                result = cur.fetchone()[0];
                if not result:
                    raise Exception('Message not found')
                if result != jwt_token['user_id']:
                    raise Exception('Unauthorized')
                
                receiver_id = result
                
                if detail == 'read':
                    # Query to update the message as read
                    statement = """
                        UPDATE details
                        SET is_read = NOT is_read
                        WHERE user_id = %s AND msg_id = %s;
                    """
                elif detail == 'replied':
                    statement = """
                        UPDATE details
                        SET replied = NOT replied
                        WHERE user_id = %s AND msg_id = %s;
                    """
                elif detail == 'trashed':
                    statement = """
                        UPDATE details
                        SET trashed = NOT trashed
                        WHERE user_id = %s AND msg_id = %s;
                    """

                values = (receiver_id, message_id)
                cur.execute(statement, values)

            conn.commit()
            
            response = {'status': status_codes['success'], 'errors': None, 'results': 'Message updated'}

    except (Exception, psycopg2.DatabaseError) as error:
        # an error occurred, rollback
        conn.rollback()

        logger.error(f'PUT /email/update/{message_id} - error: {error}')

        error = str(error).split('\n')[0]
        response = {'status': status_codes['internal_error'], 'errors': error, 'results': None}

    finally:
        if conn is not None:
            conn.close()

    return response