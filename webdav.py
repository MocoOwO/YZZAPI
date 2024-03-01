import json
import urllib

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
    if request.data:
        print(request.data)
        return f"""<?xml version="1.0" encoding="utf-8"?>
<D:multistatus
    xmlns:D="DAV:">
    <D:response>
        <D:href>/</D:href>
        <D:propstat>
            <D:prop>
                <D:quota-available-bytes>{main.get_usedsize(SESSION_ID) // 3}</D:quota-available-bytes>
            </D:prop>767
            <D:prop>
                <D:quota-used-bytes>{main.get_usedsize(SESSION_ID)}</D:quota-used-bytes>
            </D:prop>
            <D:status>HTTP/1.1 200 OK</D:status>
        </D:propstat>
    </D:response>
</D:multistatus>""", 207
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
                           pathid=str(parent_dir),
                           dirs=foldersObj,
                           files=filesObj), 207


@app.route("/<path:path>", methods=["GET", "PROPFIND", "MOVE"])
def mainLogic(path):
    # print(path)
    # print(request.headers)
    SESSION_ID = main.login(USERNAME, PASSWORD, Log=False)
    if request.method == "PROPFIND" and path[-1:] == "/":
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
    elif request.method == "PROPFIND" and path[-1:] != "/":
        dirs = path.split("/")[:-1]
        parent_dir = 0
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
                main.logout(SESSION_ID)
                return render_template("file.xml", path=path, file=file), 207
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
                return flask.redirect(f"https://yunzhongzhuan.com.publicdn.com{file.url}")
    elif request.method == "MOVE" and path[-1:] != "/":
        to_dir = (urllib.parse.urlparse(urllib.parse.unquote(request.headers["Destination"])).path)
        from_dir = (urllib.parse.urlparse(request.url).path)
        to_dirs = to_dir.split("/")[1:-1]
        filename = to_dir.split("/")[-1]
        # print(to_dir,from_dir)
        to_dir_id = 0
        for dir in to_dirs:
            folders = main.get_folder(SESSION_ID, to_dir_id)
            found = False
            for i in folders:
                if i['name'] == dir:
                    to_dir_id = i['id']
                    found = True
                    break
            if found != True:
                print("Not found to_dir:", to_dirs)
                main.logout(SESSION_ID)
                return "Not Found", 404
        from_dirs = from_dir.split("/")[1:-1]
        from_dir_id = 0
        for dir in from_dirs:
            folders = main.get_folder(SESSION_ID, from_dir_id)
            found = False
            for i in folders:
                if i['name'] == dir:
                    from_dir_id = i['id']
                    found = True
                    break
            if found != True:
                print("Not found from_dir")
                main.logout(SESSION_ID)
                return "Not Found", 404
        files = main.get_file(SESSION_ID, from_dir_id)
        found = False
        for i in files:
            file = main.File(i)
            if file.name == filename:
                fileid = file.id
                main.copy_file(SESSION_ID, to_dir_id, fileid)
                main.logout(SESSION_ID)
                # time.sleep(0.5)
                return "Created", 201

        main.logout(SESSION_ID)
        return "Not Allowed", 403
    main.logout(SESSION_ID)
    return "Not Found", 404


if __name__ == "__main__":
    app.run(port=8899)
