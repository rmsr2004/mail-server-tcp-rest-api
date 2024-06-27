import psycopg2
import flask
from globals import status_codes, config_vars, logger
from db_connection import db_connection

# ********************************************************************************************** #
# This function registers a user in the database. It first validates the payload and then        #
# inserts the user into the database. If the user is successfully inserted, the function         #
# returns the userID. If the user is not successfully inserted, the function returns an error    #
# message.                                                                                       #
# ********************************************************************************************** #
def register():
    logger.info('POST /mail/register')

    payload = flask.request.get_json()

    logger.debug(f'POST /mail/register - payload: {payload}')

    #
    # Validate payload.
    #

    # list to store errors
    errors = []

    required_fields = ['name', 'email', 'password']
    for field in required_fields:
        if field not in payload:
            errors.append(f'{field} required\n')

    if errors != []:
        response = {'status': status_codes['api_error'], 'errors': "\n".join(errors), 'results': None}
        return response

    #
    # SQL Query
    #

    conn = db_connection(config_vars)
    cur = conn.cursor()

    # query to insert the user
    statement = """
        BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
        
        INSERT INTO users (name, email, password) VALUES (%s, %s, %s)
        RETURNING user_id;
    """
    values = (payload['name'], payload['email'], payload['password'])

    try:
        cur.execute(statement, values)
        
        user_id = cur.fetchone()[0]
        if user_id is None:
            raise Exception('Error inserting user!')
        
        response = {'status': status_codes['success'], 'errors': None, 'results': user_id}

        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        # an error occurred, rollback
        conn.rollback()

        logger.error(f'POST /mail/register - error: {error}')

        error = str(error).split('\n')[0]
        response = {'status': status_codes['internal_error'], 'errors': str(error), 'results': None}

    finally:
        if conn is not None:
            conn.close()

    return response

## End of register.py