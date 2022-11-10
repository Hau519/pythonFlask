# this view is the endpoint accessed by the user.
# this file will serve as a "sub-route".
# the API acts as a "waiter" delivering requests from the front to the backend.
# "JSON Web Token is a proposed Internet standard for creating data with optional signature and/or optional encryption whose payload holds JSON that asserts some number of claims."

import json
from flask import Blueprint, request, jsonify
from controllers.user_controller import createUser, loginUser, fetchUsers
from helpers.token_validation import validateJWT  # , mainValidation

user = Blueprint("user", __name__)  # for backwards compatibility, the framework requires a name + the file name.


@user.route("/v0/users/signup", methods=["POST"])
def create():
    try:
        data = json.loads(
            request.data)  # the data will be sent from the mobile application -> the (object) will be created and pushed to the DB. the request can be accessed as a dict.

        if 'email' not in data:
            return jsonify({'error': 'Email is needed in the request.'}), 400
        if 'password' not in data:
            return jsonify({'error': 'Password is needed in the request.'}), 400
        if 'name' not in data:
            return jsonify({'error': 'Name is needed in the request.'}), 400

        createdUser = createUser(data)

        if createdUser == "Duplicated User":
            return jsonify({'error': 'There is already an user with this email.'}), 400

        if not createdUser.inserted_id:
            return jsonify({'error': 'Something wrong happened when creating user.'}), 500

        return jsonify({'uid': str(createdUser.inserted_id)})

    except ValueError:
        return jsonify({'error': 'Error creating user.'}), 400


@user.route("/v0/users/login", methods=["POST"])
def login():
    try:
        data = json.loads(request.data)

        if 'email' not in data:
            return jsonify({'error': 'Email is needed in the request.'}), 400
        if 'password' not in data:
            return jsonify({'error': 'Password is needed in the request.'}), 400

        loginAttempt = loginUser(data)

        if loginAttempt == "Invalid email":
            return jsonify({'error': 'Email not found.'}), 401

        if loginAttempt == "Invalid password":
            return jsonify({'error': 'Invalid Credentials'}), 401

        return jsonify({'token': loginAttempt.json['token'], 'expiration': loginAttempt.json['expiration'],
                        'loggedUser': loginAttempt.json['loggedUser']})

    except ValueError:
        return jsonify({'error': 'Error login user.'})


@user.route("/v0/users/all", methods=["GET"])
def fetch():
    try:
        token = validateJWT()

        if token == 400:
            return jsonify({'error': 'Token is missing in the request.'}), 400
        if token == 401:
            return jsonify({'error': 'Invalid authentication token.'}), 401

        return fetchUsers()
    except ValueError:
        return jsonify({'error': 'Error on fetching users, try again.'})
