import jwt
import psycopg2
import flask
from globals import status_codes, config_vars, logger
from db_connection import db_connection
from validate_token import validate_token

def filter_messages(filter: str):
    logger.info(f'GET /mail/filter/{filter}')

    #
    #   Validate filter
    #

    filters = ['draft', 'sent', 'read', 'replied', 'trashed', 'received']
    if filter not in filters:
        response = {'status': status_codes['api_error'], 'errors': 'Invalid filter', 'results': None}
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
    
    if filter == 'draft':
        statement = """
            SELECT msg_date, subject, content
            FROM messages
            WHERE is_draft = TRUE AND user_id = %s
            ORDER BY m.msg_date DESC;
        """
    elif filter == 'sent':
        statement = """
            SELECT msg_date, subject, content
            FROM messages
            WHERE is_draft = FALSE AND user_id = %s
            ORDER BY msg_date DESC;
        """
    elif filter == 'read':
        statement = """
            SELECT m.msg_date, m.subject, m.content
            FROM receivers_messages AS rm
            JOIN messages AS m ON m.msg_id = rm.msg_id
            JOIN receivers AS r ON r.msg_id = m.msg_id
            WHERE rm.user_id = %s AND r.is_read = TRUE
            ORDER BY m.msg_date DESC;
        """
    elif filter == 'replied':
        statement = """
            SELECT m.msg_date, m.subject, m.content
            FROM receivers_messages AS rm
            JOIN messages AS m ON m.msg_id = rm.msg_id
            JOIN receivers AS r ON r.msg_id = m.msg_id
            WHERE rm.user_id = %s AND r.is_replied = TRUE
            ORDER BY m.msg_date DESC;
        """
    elif filter == 'trashed':
        statement = """
            SELECT m.msg_date, m.subject, m.content
            FROM receivers_messages AS rm
            JOIN messages AS m ON m.msg_id = rm.msg_id
            JOIN receivers AS r ON r.msg_id = m.msg_id
            WHERE rm.user_id = %s AND r.is_trashed = TRUE
            ORDER BY m.msg_date DESC;
        """
    elif filter == 'received':
        statement = """
            SELECT m.msg_date, m.subject, m.content, u.email
            FROM messages_receivers AS mr
            JOIN messages AS m ON m.msg_id = mr.msg_id
            JOIN users AS u ON u.user_id = m.user_id
            WHERE mr.receiver_id = %s
            ORDER BY m.msg_date DESC;
        """
    values = (jwt_token['user_id'],)

    try:
        cur.execute(statement, values)

        result = cur.fetchall()
        if result:
            results = []
            for row in result:
                results.append({
                    'date': row[0],
                    'subject': row[1],
                    'content': row[2],
                    'sender': row[3]
                })
            response = {'status': status_codes['success'], 'errors': None, 'results': results}
        else:
            raise Exception('No messages found')

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /mail/filter/{filter} - error: {error}')

        response = {'status': status_codes['internal_error'], 'errors': str(error), 'results': None}

    finally:
        if conn is not None:
            conn.close()

    return response

## End of filter_messages.py