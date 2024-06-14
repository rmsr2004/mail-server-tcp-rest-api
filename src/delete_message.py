import jwt
import psycopg2
import flask
from globals import status_codes, config_vars, logger
from db_connection import db_connection
from validate_token import validate_token

def delete_message(message_id: str):
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

    # Query to verify if the user is the receiver of the message
    statement = """
        SELECT r.user_id
        FROM receivers AS r
        JOIN receivers_messages AS rm ON r.receiver_id = rm.receiver_id
        JOIN messages AS m ON m.msg_id = rm.msg_id
        WHERE m.msg_id = %s AND r.trashed = TRUE;
    """
    values = (message_id,)

    try:
        cur.execute(statement, values)

        result = cur.fetchone()
        if result is None:
            raise Exception('Message not found')
        
        if result[0] != jwt_token['user_id']:
            raise Exception('Unauthorized')

        # Query to delete the message from messages table
        # and the receivers_messages table
        statement = """
            DELETE FROM messages
            WHERE msg_id = %s;
            
            DELETE FROM receivers_messages
            WHERE msg_id = %s;
        """
        values = (message_id,)
        cur.execute(statement, values)

        conn.commit()

        response = {'status': status_codes['success'], 'errors': None, 'results': 'Message deleted'}

    except (Exception, psycopg2.DatabaseError) as error:
        # an error occurred
        conn.rollback()

        logger.error(f'DELETE /mail/delete/{message_id} - error: {error}')
        
        error = str(error).split('\n')[0]
        response = {'status': status_codes['internal_error'], 'errors': str(error), 'results': None}

    finally:
        if conn is not None:
            conn.close()

    return response