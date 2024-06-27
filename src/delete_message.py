import jwt
import psycopg2
import flask
from globals import status_codes, config_vars, logger
from db_connection import db_connection
from validate_token import validate_token

# ********************************************************************************************** #
# This function deletes a message from the database. It first validates the Authorization header #
# and then checks if the user is the receiver of the message. If the user is the receiver, the   #
# message is deleted from the details table. If the user is not the receiver, the function       #
# returns an error message. If the message is not found, the function returns an error message.  #
# ********************************************************************************************** #
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
        BEGIN TRANSACTION ISOLATION LEVEL READ COMMITED;
        
        SELECT mu.user_id
        FROM messages_users AS mu
        JOIN details AS d ON (d.msg_id = mu.msg_id AND d.user_id = mu.user_id)
        WHERE d.trashed = TRUE AND mu.msg_id = %s;
    """
    values = (message_id,)

    try:
        cur.execute(statement, values)

        result = cur.fetchone()
        if result is None:
            raise Exception('Message not found')
        
        if result[0] != jwt_token['user_id']:
            raise Exception('Unauthorized')

        # Query to lock the row and set delete attribute to TRUE
        statement = """
            SELECT deleted FROM details WHERE msg_id = %s AND user_id = %s FOR UPDATE;

            UPDATE details
            SET deleted = TRUE
            WHERE msg_id = %s AND user_id = %s;
        """
        values = (message_id, jwt_token['user_id'], message_id, jwt_token['user_id'])
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

# End of delete_message.py