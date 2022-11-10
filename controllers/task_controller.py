from bson.objectid import ObjectId
from flask import jsonify
import app_config as config
from database.__init__ import database
from models.task_model import Task
from datetime import datetime, timedelta, time
from bson.errors import BSONError, InvalidId, InvalidStringData, InvalidBSON


def getUserNameByUId(Uid):
    collection = database.dataBase[config.CONST_USER_COLLECTION]
    userInfo = collection.find_one({"_id": ObjectId(Uid)})
    return userInfo['name']


# def checkingUserUid(Uid):
#     try:
#         collection = database.dataBase[config.CONST_USER_COLLECTION]
#         if not collection.find_one({"_id": ObjectId(Uid)}):
#             return jsonify({'error': 'User does not exist'})
#         else:
#             return True
#     except Exception as err:
#         raise ValueError('Error on user Uid: ', err)


def createTask(userInformation, taskInformation):
    try:
        newTask = Task()
        newTask.description = taskInformation['description']
        newTask.createdByUid = userInformation['id']
        newTask.createdByName = getUserNameByUId(userInformation['id'])
        newTask.assignedToUid = taskInformation['assignedToUid']
        newTask.assignedToName = getUserNameByUId(taskInformation['assignedToUid'])
        taskInformation['createdAt'] = datetime.utcnow()
        newTask.createdAt = taskInformation['createdAt']
        newTask.updatedAt = taskInformation['updatedAt']

        collection = database.dataBase[config.CONST_TASK_COLLECTION]
        createdTask = collection.insert_one(newTask.__dict__)
        return createdTask
    except Exception as err:
        raise ValueError('Error on creating task: ', err)


def fetchCreatedTask(Uid):
    try:
        collection = database.dataBase[config.CONST_TASK_COLLECTION]
        createdTasks = []

        for task in collection.find():
            if str(task['createdByUid']) == str(Uid):
                currentTask = {}
                currentTask.update({'uid': str(task['_id'])})
                currentTask.update({'description': task['description']})
                currentTask.update({'createdByUid': str(task['createdByUid'])})
                currentTask.update({'createdByName': task['createdByName']})
                currentTask.update({'assignedToUid': str(task['assignedToUid'])})
                currentTask.update({'assignedToName': task['assignedToName']})
                currentTask.update({'createdAt': task['createdAt']})
                currentTask.update({'updatedAt': task['updatedAt']})
                createdTasks.append(currentTask)

        return createdTasks

    except Exception as err:
        raise ValueError("Error when trying to fetch users: ", err)


def fetchAssignedToTask(Uid):
    try:
        collection = database.dataBase[config.CONST_TASK_COLLECTION]
        createdTasks = []

        for task in collection.find():
            if str(task['assignedToUid']) == str(Uid):
                currentTask = {}
                currentTask.update({'uid': str(task['_id'])})
                currentTask.update({'description': task['description']})
                currentTask.update({'createdByUid': task['createdByUid']})
                currentTask.update({'createdByName': task['createdByName']})
                currentTask.update({'assignedToUid': task['assignedToUid']})
                currentTask.update({'assignedToName': task['assignedToName']})
                currentTask.update({'createdAt': task['createdAt']})
                currentTask.update({'updatedAt': task['updatedAt']})
                createdTasks.append(currentTask)

        return createdTasks

    except Exception as err:
        raise ValueError("Error when trying to fetch users: ", err)


def updateTask(token, Uid):
    collection = database.dataBase[config.CONST_TASK_COLLECTION]
    taskToUpdate = collection.find_one({"_id": ObjectId(Uid)})
    taskToUpdate['updatedAt'] = datetime.utcnow()
    if taskToUpdate['assignedToUid'] != token['id']:
        return jsonify({'error': "User can only change status when task is assigned to them."})
    collection.update_one({"_id": taskToUpdate["_id"]}, {"$set": {"done": True}})
    return jsonify({'taskUid': Uid})


# {"updatedAt": datetime.utcnow()}

def delete(token, Uid):
    collection = database.dataBase[config.CONST_TASK_COLLECTION]
    taskToDelete = collection.find_one({"_id": ObjectId(Uid)})
    if taskToDelete['createdByUid'] != token['id']:
        return jsonify({'error': "Users can only delete when task is created by them."})
    collection.delete_one({"_id": taskToDelete["_id"]})
    return jsonify({'tasksAffected': 1}), 200
