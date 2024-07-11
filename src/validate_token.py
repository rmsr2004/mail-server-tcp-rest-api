from globals import secret_key, revoked_tokens
import jwt

# ********************************************************************************************** #
# This function validates a JWT token. It first checks if the token exists. If the token does    #
# not exist, the function returns an error message. The function then decodes the token and      #
# checks if  the token is expired or invalid. If the token is expired or invalid, the function   #
# returns an error message. If the token is valid, the function returns the decoded token.       #
# ********************************************************************************************** #
def validate_token(jwt_token):
    if not jwt_token:
        return 'Authorization header is required!'
    
    if is_revoked(jwt_token):
        return 'Token Revoked'
    
    try:
        decoded_token = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return 'Token Expired'
    except jwt.InvalidTokenError:
        return 'Token Invalid'
    
def is_revoked(token):
    return token in revoked_tokens
    
    
# End of validate_token.py