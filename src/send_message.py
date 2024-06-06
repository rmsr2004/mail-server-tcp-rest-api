import logging as logger
import flask
import psycopg2
from globals import status_codes
from validate_token import validate_token
from db_connection import db_connection

def send_message(receiver_email):
    logger.info(f'POST /email/send/{receiver_email}')

    payload = flask.request.get_json()

    logger.debug(f'POST /email/send/{receiver_email} - payload: {payload}')

    #
    # Validate Authorization header
    #

    jwt_token = flask.request.headers.get('Authorization')
    
    jwt_token = validate_token(jwt_token)
    if isinstance(jwt_token, str):
        response = {'status': status_codes['api_error'], 'errors': jwt_token}
        return response
    
    #
    # Validate payload.
    #

    required_fields = ['subject', 'content']
    for field in required_fields:
        if field not in payload:
            response = {'status': status_codes['api_error'], 'errors': f'{field} value required'}
            return response

    #
    # SQL query 
    #

    conn = db_connection()
    cur = conn.cursor()
    
    # Query to verify if the receiver_email exists in the database
    statement =  """
        SELECT id FROM users WHERE email = %s;
    """
    values = (receiver_email, )

    try:
        cur.execute(statement, values)
        receiver_id = cur.fetchone()[0]

        if receiver_id is None:
            raise Exception(f'User with email {receiver_email} not found')
        
        # Query to insert the message into the database
        statement = """
            INSERT INTO messages(msg_date, subject, content, msg_type, user_id) VALUES (CURRENT_DATE, %s, %s, 1, %s)
            RETURNING msg_id;
        """
        values = (payload['subject'], payload['content'], jwt_token['id'])

        cur.execute(statement, values)
        message_id = cur.fetchone()[0]

        # Query to associate message with receiver
        statement = """
            INSERT INTO message_receivers(msg_id, receiver_id) VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
        """
        values = (message_id, receiver_id)

        cur.execute(statement, values)

        response = {'status': status_codes['success'], 'results': message_id}

        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        # an error occurred, rollback
        conn.rollback()

        logger.error(f'POST /email/send/{receiver_email} - error: {error}')

        error = str(error).split('\n')[0]
        response = {'status': status_codes['internal_error'], 'errors': error, 'results': None}

    finally:
        if conn is not None:
            conn.close()

    return response
