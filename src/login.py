import jwt
import psycopg2
import flask
import traceback
from globals import status_codes, secret_key, config_vars, logger
from db_connection import db_connection

# ********************************************************************************************** #
# This function logs a user into the system. It first validates the payload and then queries the #
# database to check if the user exists. If the user exists, the function checks if the password  #
# is correct. If the password is correct, the function generates a JWT token and returns it. If  #
# the user does not exist or the password is incorrect, the function returns an error message.   #
# ********************************************************************************************** #
def login():
    logger.info('PUT /mail/login')

    payload = flask.request.get_json()

    logger.debug(f'PUT /mail/login - payload: {payload}')

    #
    # Validate payload
    #

    # list to store errors
    errors = []

    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in payload:
            errors.append(f'{field} required\n')

    if errors != []:
        response = {'status': status_codes['api_error'], 'errors': "\n".join(errors), 'results': None}
        return response
    
    #
    # SQL query
    #

    conn = db_connection(config_vars)
    cur = conn.cursor()
    
    statement =  """
        BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
        
        SELECT user_id, password AS decrypted_password
        FROM users
        WHERE email = %s
        FOR UPDATE;
    """
    values = (payload['email'],)

    try:
        cur.execute(statement, values)
        result = cur.fetchone()

        if result:
            user_id, decrypted_password = result

            if decrypted_password != payload['password']:
                raise Exception('Invalid password!')
            
            jwt_payload = {'user_id': int(user_id)}
            jwt_token = jwt.encode(jwt_payload, secret_key, algorithm='HS256')
            
            response = {'status': status_codes['success'], 'errors': None, 'results': jwt_token}

            conn.commit()

            logger.info(f'PUT /mail/login - user {user_id} logged in')

        else:
            raise Exception('Invalid username or password!')
        
    except (Exception, psycopg2.DatabaseError) as error:
        # an error occurred, rollback
        conn.rollback()

        error_trace = traceback.format_exc()
        logger.error(f'POST /email/login - error: {error_trace}')

        error = str(error).split('\n')[0]
        response = {'status': status_codes['internal_error'], 'errors': error, 'results': None}

    finally:
        if conn is not None:
            conn.close()

    return response

## End of login.py