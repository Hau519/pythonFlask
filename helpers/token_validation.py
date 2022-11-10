import jwt
from flask import request, jsonify
import app_config as config


def validateJWT():
    token = None
    userInformation = None

    try:
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return 400
        try:
            userInformation = jwt.decode(token, key=config.TOKEN_SECRET, algorithms=["HS256"])
        except Exception:
            return 401

        return userInformation

    except jwt.ExpiredSignatureError:
        return 401
    except:
        return 400




# def mainValidation(token):
#     token = validateJWT()
#     if token == 400:
#         return jsonify({'error': 'Token is missing in the request.'}), 400
#     if token == 401:
#         return jsonify({'error': 'Invalid authentication token.'}), 401
