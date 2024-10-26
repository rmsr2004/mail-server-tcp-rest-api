import flask
import psycopg2
import traceback
from globals import status_codes, config_vars, logger
from validate_token import validate_token
from db_connection import db_connection

# ********************************************************************************************** #
# This function sends a message to a list of receivers. It first validates the Authorization     #
# header and then validates the payload. If the payload is invalid, the function returns an      #
# error message. The function then queries the database to check if the receivers exist. If the  #
# receivers do not exist, the function returns an error message. If the receivers exist, the     #
# function inserts the message into the database and associates the message with the receivers.  #
# ********************************************************************************************** #
def send_message():
    logger.info('POST /email/send')

    payload = flask.request.get_json()

    logger.debug(f'POST /email/send - payload: {payload}')

    #
    # Validate Authorization header
    #

    jwt_token = flask.request.headers.get('Authorization')
    
    jwt_token = validate_token(jwt_token)
    if isinstance(jwt_token, str):
        response = {'status': status_codes['api_error'], 'errors': jwt_token, 'results': None}
        return response
    
    #
    # Validate payload.
    #

    # list to store errors
    errors = []

    required_fields = ['receivers', 'subject', 'content']
    for field in required_fields:
        if field not in payload:
            errors.append(f'{field} required\n')
    
    if errors != []:
        response = {'status': status_codes['api_error'], 'errors': " ".join(errors), 'results': None}
        return response

    receivers = payload['receivers']
    if receivers == []:
        response = {'status': status_codes['api_error'], 'errors': 'receivers emails required', 'results': None}
        return response
   
    #
    # SQL query 
    #

    conn = db_connection(config_vars)
    cur = conn.cursor()

    try:
        # Query to set the isolation level
        statement = """
            BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
        """
        cur.execute(statement)
        
        # Queries to verify if the receivers emails exists in the database
        receivers_ids = []
        for receiver_email in receivers:
            statement = """
                SELECT user_id FROM users WHERE email = %s;
            """
            values = (receiver_email,)

            cur.execute(statement, values)
            receiver_id = cur.fetchone()

            if receiver_id is None:
                raise Exception(f"Receiver email {receiver_email} not found")

            receivers_ids.append(receiver_id)
            
        # Query to insert the message into the database
        statement = """
            INSERT INTO messages(msg_date, subject, content, user_id) VALUES (CURRENT_DATE, %s, %s, %s)
            RETURNING msg_id;
        """
        values = (payload['subject'], payload['content'], jwt_token['user_id'])

        cur.execute(statement, values)
        message_id = cur.fetchone()[0]

        # Queries to associate message with receiver
        for receiver_id in receivers_ids:
            statement = """
                INSERT INTO messages_users (msg_id, user_id) VALUES (%s, %s);
                INSERT INTO details (msg_id, user_id) VALUES (%s, %s);
            """
            values = (message_id, receiver_id, message_id, receiver_id)
            cur.execute(statement, values)

        response = {'status': status_codes['success'], 'errors': None, 'results': message_id}

        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        # an error occurred, rollback
        conn.rollback()
        
        error_trace = traceback.format_exc()
        logger.error(f'POST /email/send - error: {error_trace}')

        error = str(error).split('\n')[0]
        response = {'status': status_codes['internal_error'], 'errors': error, 'results': None}

    finally:
        if conn is not None:
            conn.close()
            
    return response

# End of send_message.py