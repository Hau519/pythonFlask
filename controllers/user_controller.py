from flask import jsonify
from models.user_model import User
import bcrypt
from database.__init__ import database
import app_config as config
from datetime import datetime, timedelta
import jwt


def generateHashPassword(password):
    salt = bcrypt.gensalt()
    hashedPassword = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashedPassword


def createUser(userInformation):
    try:
        newUser = User()
        newUser.name = userInformation['name'].lower()
        newUser.email = userInformation['email'].lower()
        newUser.password = generateHashPassword(userInformation['password'])

        collection = database.dataBase[config.CONST_USER_COLLECTION]

        if collection.find_one({'email': newUser.email}):
            return "Duplicated User"

        createdUsed = collection.insert_one(newUser.__dict__)

        return createdUsed
    except Exception as err:
        raise ValueError('Error on creating user: ', err)


def loginUser(userInformation):
    try:
        email = userInformation['email'].lower()
        password = userInformation['password'].encode("utf-8")

        collection = database.dataBase[config.CONST_USER_COLLECTION]

        currentUser = collection.find_one({'email': email})

        if not currentUser:
            return "Invalid email"

        if not bcrypt.checkpw(password, currentUser["password"]):
            return "Invalid password"

        loggedUsed = {}
        loggedUsed.update({'uid': str(currentUser['_id'])})
        loggedUsed.update({'email': currentUser['email']})
        loggedUsed.update({'name': currentUser['name']})

        expiration = datetime.utcnow() + timedelta(seconds=config.JWT_EXPIRATION)

        jwtData = {'email': currentUser['email'], 'id': str(currentUser['_id']), 'exp': expiration}

        jwtToReturn = jwt.encode(payload=jwtData, key=config.TOKEN_SECRET)

        return jsonify({'token': jwtToReturn, 'expiration': config.JWT_EXPIRATION, 'loggedUser': loggedUsed})

    except Exception as err:
        raise ValueError("Error on trying to login the user: ", err)


def fetchUsers():
    try:
        collection = database.dataBase[config.CONST_USER_COLLECTION]
        users = []

        for user in collection.find():
            currentUser = {}
            currentUser.update({'uid': str(user['_id'])})
            currentUser.update({'email': user['email']})
            currentUser.update({'name': user['name']})
            users.append(currentUser)

        return users

    except Exception as err:
        raise ValueError("Error when trying to fetch users: ", err)
