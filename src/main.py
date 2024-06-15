import flask
import logging
from globals import config_vars, logger
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

# ********************************************************************************************** #
# This endpoint is used to register a new user in the system.                                    #
# The request must be a POST request with the following JSON body:                               #
# {                                                                                              #
#     "name": "string",                                                                          #
#     "email": "string",                                                                         #
#     "password": "string"                                                                       #
# }                                                                                              #
# The response will be a JSON object with the following structure:                               #
# {                                                                                              #
#     "status": 200,                                                                             #
#     "errors": null,                                                                            #
#     "results": user_id                                                                         #
# }                                                                                              #
# ********************************************************************************************** #
@app.route('/mail/register', methods=['POST'])
def register_endpoint():
    response = register()
    return flask.jsonify(response)

# ********************************************************************************************** #
# This endpoint is used to login a user in the system.                                           #
# The request must be a PUT request with the following JSON body:                                #
# {                                                                                              #
#     "email": "string",                                                                         #
#     "password": "string"                                                                       #
# }                                                                                              #
# The response will be a JSON object with the following structure:                               #
# {                                                                                              #
#     "status": 200,                                                                             #
#     "errors": null,                                                                            #
#     "results": JWT Token                                                                       #
# }                                                                                              #
# ********************************************************************************************** #
@app.route('/mail/login', methods=['PUT'])
def login_endpoint():
    response = login()
    return flask.jsonify(response)

# ********************************************************************************************** #
# This endpoint is used to send a message.                                                       #
# The request must be a POST request with the following JSON body:                               #
# {                                                                                              #
#     "receivers": [                                                                             #
#           "string",                                                                            #
#           ...                                                                                  #
#     ],                                                                                         #
#     "subject": "string",                                                                       #
#     "content": "string"                                                                        #
# }                                                                                              #
# The response will be a JSON object with the following structure:                               #
# {                                                                                              #
#     "status": 200,                                                                             #
#     "errors": null,                                                                            #
#     "results": message_id                                                                      #
# }                                                                                              #
# ********************************************************************************************** #
@app.route('/mail/send', methods=['POST'])
def send_message_endpoint():
    response = send_message()
    return flask.jsonify(response)

# ********************************************************************************************** #
# This endpoint is used to retrieve messages.                                                    #
# The request must be a GET request.                                                             #
# The response will be a JSON object with the following structure:                               #
# {                                                                                              #
#     "status": 200,                                                                             #
#     "errors": null,                                                                            #
#     "results": [                                                                               #
#         {                                                                                      #
#             "date": DATE,                                                                      #
#             "sender": [ "string" ]                                                             #
#             "subject": "string",                                                               #
#             "content": "string",                                                               #
#         }                                                                                      #
#     ]                                                                                          #
# }                                                                                              #
# ********************************************************************************************** #
@app.route('/mail/home', methods=['GET'])
def home_messages_endpoint():
    response = filter_messages('received')
    return flask.jsonify(response)

# ********************************************************************************************** #
# This endpoint is used to retrieve messages filtered by the filter parameter.                   #
# The request must be a GET request.                                                             #
# The response will be a JSON object with the following structure:                               #
# {                                                                                              #
#     "status": 200,                                                                             #
#     "errors": null,                                                                            #
#     "results": [                                                                               #
#         {                                                                                      #
#             "date": DATE,                                                                      #
#             "sender": [ "string" ] OR "receivers": ["string", "string", ...]                   #
#             "subject": "string",                                                               #
#             "content": "string",                                                               #
#         }                                                                                      #
#     ]                                                                                          #
# }                                                                                              #
# ********************************************************************************************** #
@app.route('/mail/filter/<filter>', methods=['GET'])
def filter_messages_endpoint(filter):
    response = filter_messages(filter)
    return flask.jsonify(response)
# ********************************************************************************************** #
# This endpoint is used to update a message.                                                     #
# The request must be a PUT request with the following JSON body:                                #
# {                                                                                              #
#     "details": ["string", "string", ...]                                                       #
# }                                                                                              #
# The response will be a JSON object with the following structure:                               #
# {                                                                                              #
#     "status": 200,                                                                             #
#     "errors": null,                                                                            #
#     "results": "Message updated"                                                               #
# }                                                                                              #
# ********************************************************************************************** #
@app.route('/mail/update/<message_id>', methods=['PUT'])
def update_message_endpoint(message_id):
    response = update_message(message_id)
    return flask.jsonify(response)
# ********************************************************************************************** #
# This endpoint is used to delete a message.                                                     #
# The request must be a DELETE request.                                                          #
# The response will be a JSON object with the following structure:                               #
# {                                                                                              #
#     "status": 200,                                                                             #
#     "errors": null,                                                                            #
#     "results": "Message deleted"                                                               #
# }                                                                                              #
# ********************************************************************************************** #
@app.route('/mail/delete/<message_id>', methods=['DELETE'])
def delete_message_endpoint(message_id):
    response = delete_message(message_id)
    return flask.jsonify(response)

if __name__ == '__main__':
    # set up logging
    logger.setLevel(logging.DEBUG)

 # Remove todos os handlers existentes para evitar duplicação
    logger.handlers.clear()

    # Criação do handler
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    handler.setFormatter(formatter)

    # Configurar o nível do handler baseado nas configurações
    if config_vars['debug']:
        handler.setLevel(logging.DEBUG)
    elif config_vars['log']:
        handler.setLevel(logging.INFO)

    # Adicionar o handler ao logger se qualquer uma das condições for verdadeira
    if config_vars['debug'] or config_vars['log']:
        logger.addHandler(handler)

    host = '127.0.0.1'
    port = 8080
    app.run(host=host, debug=config_vars['debug'], threaded=True, port=port)
    
    if config_vars['log']:
        logger.info(f'API v1.0 online: http://{host}:{port}')