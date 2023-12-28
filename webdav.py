import json

import flask

import main
import datetime
import time

from flask import Flask, request, render_template

f = open("config.json")
d = json.load(f)
USERNAME = d['USERNAME']
PASSWORD = d['PASSWORD']

app = Flask(__name__)


@app.route('/', methods=["GET", "PROPFIND", "PUT"])
def getfile(parent_dir=0):
    SESSION_ID = main.login(USERNAME, PASSWORD, Log=False)
    files = main.get_file(SESSION_ID, parent_dir)
    folders = main.get_folder(SESSION_ID, parent_dir)
    filesObj = []
    for i in files:
        filesObj.append(main.File(i))
    foldersObj = []
    for i in folders:
        foldersObj.append(main.Folder(i))
    main.logout(SESSION_ID)
    return render_template("base.xml", pathdir="/",
                           path_dir_name="root",
                           dirs=foldersObj,
                           files=filesObj), 207


@app.route("/<path:path>", methods=["GET", "PROPFIND", "PUT"])
def mainLogic(path):
    # print(path)
    SESSION_ID = main.login(USERNAME, PASSWORD, Log=False)
    if path[-1:] == "/":
        parent_dir = 0
        dirs = path.split("/")[:-1]
        for dir in dirs:
            folders = main.get_folder(SESSION_ID, parent_dir)
            found = False
            for i in folders:
                if i['name'] == dir:
                    parent_dir = i['id']
                    found = True
                    break
            if found != True:
                main.logout(SESSION_ID)
                return "Not Found", 404

        main.logout(SESSION_ID)
        return getfile(parent_dir=parent_dir)
    elif request.method == "GET":
        # print("file???")
        parent_dir = 0
        dirs = path.split("/")[:-1]
        filename = path.split("/")[-1]
        # print(dirs,filename)
        for dir in dirs:
            folders = main.get_folder(SESSION_ID, parent_dir)
            found = False
            for i in folders:
                if i['name'] == dir:
                    parent_dir = i['id']
                    found = True
                    break
            if found != True:
                main.logout(SESSION_ID)
                return "Not Found", 404
        files = main.get_file(SESSION_ID, parent_dir)
        for i in files:
            file = main.File(i)
            if file.name == filename:
                # print("OK?")
                main.logout(SESSION_ID)
                return flask.redirect(f"https://a.download.yunzhongzhuan.com{file.url}")
    main.logout(SESSION_ID)
    return "Not Found", 404


if __name__ == "__main__":
    app.run(port=8899)
