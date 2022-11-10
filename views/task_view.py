import json

from bson.errors import InvalidId
from flask import Blueprint, request, jsonify
from pkg_resources import require
from bson.objectid import ObjectId
from controllers.task_controller import createTask, fetchCreatedTask, fetchAssignedToTask, updateTask, delete
from helpers.token_validation import validateJWT

task = Blueprint("task", __name__)
token = validateJWT()
invalid_request = {}
# ObjectId = require('mongodb').ObjectId
# data = json.loads(request.data)

def mainValidation(token: object) -> object:
    global invalid_request
    if token == 400:
        invalid_request = jsonify({'error': 'Token is missing in the request.'}), 400
        return invalid_request
    if token == 401:
        invalid_request = jsonify({'error': 'Invalid authentication token.'}), 401
        return invalid_request


def is_valid(oid):
    try:
        ObjectId(oid)
        return True
    except (InvalidId, TypeError):
        return False




@task.route("/v0/tasks/createTask", methods=["POST"])
def create():
    try:
        if mainValidation(token) is not None:
            return invalid_request

        data = json.loads(request.data)

        if 'description' not in data:
            return jsonify({'error': 'Description is needed in the request.'}), 400
        if 'assignedToUid' not in data:
            return jsonify({'error': 'Assigned user is needed in the request.'}), 400
        # checkingUserUid(data['assignedToUid'])
        if is_valid(data['assignedToUid']) is False:
            return jsonify({'error': 'Uid id not in the right format.'}), 400

        createdTask = createTask(token, data)
        return jsonify({'uid': str(createdTask.inserted_id)})

    except ValueError:
        return jsonify({'error': 'Error creating task.'})


@task.route("/v0/tasks/createdby/", methods=["GET"])
def createdBy():
    if mainValidation(token) is not None:
        return invalid_request

    return fetchCreatedTask(token['id'])


@task.route("/v0/tasks/assignedto/", methods=["GET"])
def assignedTo():
    if mainValidation(token) is not None:
        return invalid_request

    return fetchAssignedToTask(token['id'])


@task.route("/v0/tasks/<taskUid>", methods=["PATCH"])
def updatetask(taskUid):
    if mainValidation(token) is not None:
        return invalid_request

    data = json.loads(request.data)

    if 'done' not in data:
        return jsonify({'error': 'Done is needed in the request.'}), 400

    return updateTask(token, taskUid)


@task.route("/v0/tasks/<taskUid>", methods=["DELETE"])
def deleteTask(taskUid):
    if mainValidation(token) is not None:
        return invalid_request

    return delete(token, taskUid)
