from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload
from multiprocessing import Process
import filesHandler
import mimetypes
import os.path
import pickle

## ---------- CONFIG ---------- ##
SCOPES = ['https://www.googleapis.com/auth/drive']
STORIES_PATH_ID = '1yMPLjDZUC2V1yYv-1E3HQNp9rnLgai52'
DELETE_AFTER_UPLOAD = True
RUN_PARALLEL = True
PROCESSES = 4
## ---------- ------ ---------- ##

#Load credentials
creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials_drive.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

drive_service = build('drive', 'v3', credentials=creds)

def getMIMEType(filename):
    return mimetypes.MimeTypes().guess_type(filename)[0]

def upload(filename, filePath, folderID):
    file_metadata = {'name': filename, 'parents': [folderID]}
    media = MediaFileUpload(filePath, mimetype=getMIMEType(filename))
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

def createFolder(folderName):
    file_metadata = {'name': folderName, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [STORIES_PATH_ID]}
    file = drive_service.files().create(body=file_metadata,fields='id').execute()
    return file.get('id')

def getFolderID(path):
    page_token = None
    while True:
        response = drive_service.files().list(q="mimeType='application/vnd.google-apps.folder'", spaces='drive', fields='nextPageToken, files(id, name, parents)', pageToken=page_token).execute()
        for file in response.get('files', []):
            if file.get('name') == path and file.get('parents')[0] == STORIES_PATH_ID:
                return file.get('id')
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            return False

def buildPath(user, filename):
    return 'stories'+'/'+user+'/'+filename

def handleUploads(folders):
    cont = 0
    for folder in folders:
        cont += 1
        print('Uploading downloaded stories from {} ({}/{}):'.format(folder,cont,len(folders)))
        stories = filesHandler.getStories(folder)
        if (len(stories) == 0):
            print('There are no downloaded stories for this user')
            continue
        counter = 0
        folder_id = getFolderID(folder)
        if not folder_id:
            folder_id = createFolder(folder)
        for file in stories:
            counter += 1
            print('Uploading file {} of {}'.format(counter,len(stories)))
            localPath = buildPath(folder, file)
            fileID = upload(file, localPath, folder_id)
            if fileID and DELETE_AFTER_UPLOAD:
                os.remove(localPath)

def divideList(folders, qnt):
    _list = []
    lists = []
    index = 0
    for folder in folders:
        _list.append(folder)
        index += 1
        if index == int(len(folders)/qnt):
            index = 0
            lists.append(_list)
            _list = []
    if len(_list) > 0:
        for leftover in _list:
            lists[qnt-1].append(leftover)
    return lists

def runSerial():
    folders = filesHandler.getUsers()
    handleUploads(folders)

def runParallel():
    if __name__ == '__main__':
        folders = filesHandler.getUsers()
        lists = divideList(folders, PROCESSES)
        jobs = []
        for lst in lists:
            jobs.append(Process(target=handleUploads, args=(lst,)))
        for job in jobs:
            job.start()
    
if RUN_PARALLEL:
    runParallel()
else:
    runSerial()