from globals import secret_key
import jwt

def validate_token(jwt_token):
    if not jwt_token:
        return 'Authorization header is required!'
    
    try:
        decoded_token = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return 'Token Expired'
    except jwt.InvalidTokenError:
        return 'Token Invalid'