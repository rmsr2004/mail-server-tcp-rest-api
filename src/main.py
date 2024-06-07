import flask
import logging
from globals import config_vars
from login import login
from register import register
from send_message import send_message
from filter_messages import filter_messages
from update_message import update_message
from delete_message import delete_message

app = flask.Flask(__name__)

# ********************************************************************************************** #
# This function is an error handler for HTTP status codes 404 (Not Found) and 400 (Bad Request). #
# When a request is made to an invalid endpoint or a bad request is encountered,                 #
# this function generates a JSON response with the error details.                                #
# ********************************************************************************************** #
@app.errorhandler(404)
@app.errorhandler(400)
def error_handler(error):
    response = {
        'status': error.code,
        'errors': error.name,
        'results': None
    }
    return flask.jsonify(response)

@app.route('/mail/register', methods=['POST'])
def register_endpoint():
    response = register()
    return flask.jsonify(response)

@app.route('/mail/login', methods=['PUT'])
def login_endpoint():
    response = login()
    return flask.jsonify(response)

@app.route('/mail/send', methods=['POST'])
def send_message_endpoint():
    response = send_message()
    return flask.jsonify(response)

@app.route('/mail/home', methods=['GET'])
def home_messages_endpoint():
    response = filter_messages('received')
    return flask.jsonify(response)

@app.route('/mail/filter/<filter>', methods=['GET'])
def filter_messages_endpoint(filter):
    response = filter_messages(filter)
    return flask.jsonify(response)

@app.route('/mail/update/<message_id>', methods=['PUT'])
def update_message_endpoint(message_id):
    response = update_message(message_id)
    return flask.jsonify(response)

@app.route('/mail/delete/<message_id>', methods=['DELETE'])
def delete_message_endpoint(message_id):
    response = delete_message(message_id)
    return flask.jsonify(response)

if __name__ == '__main__':
    if config_vars['log']:
        logging.basicConfig(filename='log_file.log')
    
    logger = logging.getLogger('logger')

    ch = logging.StreamHandler()
    
    if config_vars['debug']:
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    host = '127.0.0.1'
    port = 8080

    logger.info(f'API v1.0 online: http://{host}:{port}')
    app.run(host=host, debug=config_vars['debug'], threaded=True, port=port)