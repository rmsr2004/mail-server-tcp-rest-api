import flask
import logging
import psycopg2
import jwt
import secrets
from read_config import read_config
from globals import config_vars
from login import login
from register import register
from send_message import send_message

app = flask.Flask(__name__)

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

@app.route('/mail/filter/<filter>', methods=['GET'])
def filter_messages_endpoint(filter):
    response = None
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