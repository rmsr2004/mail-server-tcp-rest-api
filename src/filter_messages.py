import jwt
import psycopg2
import flask
from globals import status_codes, config_vars, logger
from db_connection import db_connection
from validate_token import validate_token

# ********************************************************************************************** #
# This function filters messages based on the filter parameter. It first validates the filter    #
# parameter and then validates the Authorization header. If the filter parameter is invalid, the #
# function returns an error message. If the Authorization header is invalid, the function        #
# returns an error message. The function then queries the database based on the filter parameter #
# and returns the messages. If no messages are found, the function returns an error message.     #
# ********************************************************************************************** #
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
            SELECT m.msg_date, m.subject, m.content, u.email
            FROM messages AS m
            JOIN messages_users AS mu ON m.msg_id = mu.msg_id
            JOIN users AS u ON u.user_id = mu.user_id
            WHERE m.is_draft = TRUE AND m.user_id = %s
            ORDER BY msg_date DESC;
        """
    elif filter == 'sent':
        statement = """
            SELECT m.msg_date, m.subject, m.content, u.email
            FROM messages AS m
            JOIN messages_users AS mu ON m.msg_id = mu.msg_id
            JOIN users AS u ON u.user_id = mu.user_id
            WHERE m.is_draft = FALSE AND m.user_id = %s
            ORDER BY msg_date DESC;
        """
    elif filter == 'read':
        statement = """
            SELECT m.msg_date, m.subject, m.content, u.email
            FROM messages AS m
            JOIN messages_users AS mu ON m.msg_id = mu.msg_id
            JOIN users AS u ON u.user_id = m.user_id
            JOIN details AS d ON (d.msg_id = mu.msg_id AND d.user_id = mu.user_id)
            WHERE d.is_read = TRUE AND mu.user_id = %s
            ORDER BY msg_date DESC;
        """
    elif filter == 'replied':
        statement = """
            SELECT m.msg_date, m.subject, m.content, u.email
            FROM messages AS m
            JOIN messages_users AS mu ON m.msg_id = mu.msg_id
            JOIN users AS u ON u.user_id = m.user_id
            JOIN details AS d ON (d.msg_id = mu.msg_id AND d.user_id = mu.user_id)
            WHERE d.replied = TRUE AND mu.user_id = %s
            ORDER BY msg_date DESC;
        """
    elif filter == 'trashed':
        statement = """
            SELECT m.msg_date, m.subject, m.content, u.email
            FROM messages AS m
            JOIN messages_users AS mu ON m.msg_id = mu.msg_id
            JOIN users AS u ON u.user_id = m.user_id
            JOIN details AS d ON (d.msg_id = mu.msg_id AND d.user_id = mu.user_id)
            WHERE d.trashed = TRUE AND mu.user_id = %s
            ORDER BY msg_date DESC;
        """
    elif filter == 'received':
        statement = """
            SELECT m.msg_date, m.subject, m.content, u.email
            FROM messages AS m
            JOIN messages_users AS mu ON mu.msg_id = m.msg_id
            JOIN users AS u ON u.user_id = m.user_id
            WHERE m.is_draft = FALSE AND mu.user_id = %s
            ORDER BY m.msg_date DESC;
        """
    values = (jwt_token['user_id'],)

    try:
        # add isolation level to the transaction
        statement = """
            BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
        """ + statement
        cur.execute(statement, values)

        result = cur.fetchall()
        if result:
            # Group messages by content
            grouped_messages = {}
            for row in result:
                msg_date, subject, content, receiver = row
                if content not in grouped_messages:
                    grouped_messages[content] = {
                        'date': msg_date,
                        'subject': subject,
                        'content': content,
                        'receivers': []
                    }
                grouped_messages[content]['receivers'].append(receiver)

            # Format the grouped messages for response
            results = []
            for content, message in grouped_messages.items():
                results.append(
                    {
                        'date': message['date'],
                        'subject': message['subject'],
                        'content': message['content'],
                        'receivers' if filter == 'sent' else 'sender' : message['receivers'] 
                    }
                )

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