import logging as logger
import jwt
import psycopg2
import flask
from globals import status_codes, secret_key
from db_connection import db_connection 

def login():
    logger.info('PUT /mail/login')

    payload = flask.request.get_json()

    logger.debug(f'PUT /mail/login - payload: {payload}')

    #
    # Validate payload
    #

    if 'email' not in payload:
        response = {'status': status_codes['api_error'], 'errors': 'email is required!'}
        return response
    if 'password' not in payload:
        response = {'status': status_codes['api_error'], 'errors': 'password is required!'}
        return response
    
    #
    # SQL query
    #

    conn = db_connection()
    cur = conn.cursor()
    
    statement =  """
        SELECT user_id, decrypt(password, 'my_secret_key') AS decrypted_password
        FROM users
        WHERE email = %s;
    """
    values = (payload['username'], payload['username'])

    try:
        cur.execute(statement, values)
        result = cur.fetchone()

        if result:
            user_id, decrypted_password = result

            if decrypted_password != payload['password']:
                raise Exception('Invalid password!')
            
            jwt_payload = {
                'user_id': int(user_id)
            }
            jwt_token = jwt.encode(jwt_payload, secret_key, algorithm='HS256')

            logger.debug(f'PUT /mail/login - user {user_id} logged in')
            
            response = {'status': status_codes['success'], 'results': jwt_token}

            conn.commit()
        else:
            raise Exception('Invalid username or password!')
        
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT mail/login - error: {error}')
        response = {'status': status_codes['internal_error'], 'errors': str(error), 'results': None}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return response

## End of login.py