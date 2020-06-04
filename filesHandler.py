import os

MAIN_DIR = './stories/'

def getUsers(): #Get users with downloaded stories
    folders = []
    for x in os.listdir(MAIN_DIR):
        folders.append(x)
    return folders

def getStories(user):
    if user != '': #Get downloaded stories from given user
        files = []
        for x in os.listdir(MAIN_DIR+user):
            files.append(x)
        return files
    else: #Get all downloaded stories
        files = {}
        users = getUsers()
        for user in users:
            files[user] = []
            for x in os.listdir(MAIN_DIR+user):
                files[user].append(x)
        return files