import json
import os
import random
import datetime

import httpx
from rich.console import Console
from rich.progress import track
from rich.table import Table
import hashlib
from os.path import getsize

requests = httpx.Client(http2=True, timeout=None)
# import requests


GMT = "%a, %d %b %Y %H:%M:%S GMT"

# 账号&密码
f = open("config.json")
d = json.load(f)
USERNAME = d['USERNAME']
PASSWORD = d['PASSWORD']

console = Console()


class Folder:
    """文件夹基类"""

    def __init__(self, data: dict):
        self.name = data['name']
        self.date = data['date']
        self.date_int = data['date_int']
        self.id = data['id']
        self.parent = data['parent']
        # TODO: Path更新
        self.path = ""

    def __repr__(self):
        return self.name

    def get_GMT_time(self):
        return datetime.datetime.utcfromtimestamp(int(self.date_int)).strftime(GMT)


class File:
    """文件基类"""

    def __init__(self, data: dict):
        self.name = data['name']
        self.date = data['date']
        self.date_int = data['date_int']
        self.id = data['id']
        self.hash = data['hash']
        self.parent = data['parent']
        self.mirror = data['mirror']
        self.size = data['size']
        self.url = data['url']
        self.share = data['share']

    def __repr__(self):
        return self.name

    def get_GMT_time(self):
        return datetime.datetime.utcfromtimestamp(int(self.date_int)).strftime(GMT)


def sha256(file):
    """计算SHA, 输入为str时当路径处理,输入bytes时直接计算"""
    if isinstance(file, str):
        sha256_hash = hashlib.sha256()
        with open(file, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    else:
        sha_hash = hashlib.sha256(file).hexdigest()
        return sha_hash


def data_convert(value):
    """单位转换"""
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f %s" % (value, units[i])
        value = value / size


def rand_session():
    """生成随机Session ID"""
    BASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
    res = ""
    for i in range(26):
        res += BASE[random.randint(0, 61)]
    return res


def login(username: str, password: str, Log: bool = True) -> str:
    """登陆，返回session ID 供操作"""
    session_id = rand_session()
    s = requests

    r = s.post("https://c34a02aaeb0d6.cname.frontwize.com/php/v4/userinfo", data={"post": 1, "session_id": session_id})

    # console.print(r.json()['status_code'])
    if not r.json()['status']:
        if Log:
            console.print("[MAIN] 需要登陆,正在登陆中...")
        r = s.post("https://c34a02aaeb0d6.cname.frontwize.com/php/v4/login",
                   data={"username": username, "password": password, "session_id": session_id})
        if Log:
            console.print(f"[INFO] {r.json()['message']}")
        if not r.json()['status']:
            logout(1)
    else:
        if Log:
            console.print("[MAIN] 不需要登陆")

    r = s.post("https://c34a02aaeb0d6.cname.frontwize.com/php/v4/userinfo", data={"post": 1, "session_id": session_id})

    if Log:
        # console.print(r.json())
        data = r.json()
        console.print(f"[MAIN] 成功登录到{data['username']}({data['id']})")
        console.print(f"[INFO] 单个文件上限{data['upload_file_max_size'] / 1024 / 1024 / 1024}GB")
        console.print(f"[INFO] 外链能力: {data['public_link']}")

        # POST https://c34a02aaeb0d6.cname.frontwize.com/php/v4/get_usedsize {"post": 1, "session_id": SESSION_ID}
        console.print(f"[INFO] 已用云盘空间{data_convert(int(data['files_size_sum']))}")
    return session_id


def get_usedsize(session_id):
    return int(requests.post("https://c34a02aaeb0d6.cname.frontwize.com/php/v4/get_usedsize",
                             data={"post": 1, "session_id": session_id}).text)


def copy_file(session_id, from_dir, to_dir, fileid):
    r = requests.post("https://c34a02aaeb0d6.cname.frontwize.com/php/v4/files_paste",
                      data={"new_parent_folder_id": to_dir, "folders_id": 0, "files_id": f"{0},{fileid}",
                            "session_id": session_id}).text


def logout(session_id):
    """退出登陆"""
    requests.post("https://c34a02aaeb0d6.cname.frontwize.com/php/v4/exit", data={"session_id": session_id})


def create_folder(session_id: str, parent_folder: int, name: str) -> int:
    """创建文件夹,返回文件夹ID"""
    r = requests.post("https://c34a02aaeb0d6.cname.frontwize.com/php/v4/create_folder",
                      data={"session_id": session_id, "parent_folder_id": parent_folder, "folder_name": name})
    return r.json()['id']


def get_folder(session_id: str, parent_folder: int, search: str = "") -> list:
    """获取文件夹,带search参数时搜索文件"""
    i = 0
    r = requests.post("https://c34a02aaeb0d6.cname.frontwize.com/php/v4/folders",
                      data={"session_id": session_id, "parent_folder_id": parent_folder, "page": i, "like": search})
    folders = r.json()['data']
    while not r.json()['loadover']:
        i += 1
        r = requests.post("https://c34a02aaeb0d6.cname.frontwize.com/php/v4/folders",
                          data={"session_id": session_id, "parent_folder_id": parent_folder, "page": i, "like": search})
        folders += r.json()['data']

    return folders


def remove_folder(session_id: str, folder: int, parent_folder: int) -> None:
    """删除文件夹,慎用,很慢"""
    requests.post("https://c34a02aaeb0d6.cname.frontwize.com/php/v4/files_delete",
                  data={"session_id": session_id, "parent_folder_id": parent_folder, "folders_id": folder,
                        "files_id": ""})


def get_file(session_id: str, parent_folder: int, search: str = "") -> list:
    """获取文件,带search参数时搜索文件"""
    i = 0
    r = requests.post("https://c34a02aaeb0d6.cname.frontwize.com/php/v4/files",
                      data={"session_id": session_id, "parent_folder_id": parent_folder, "page": i, "like": search})
    folders = r.json()['data']
    while not r.json()['loadover']:
        i += 1
        r = requests.post("https://c34a02aaeb0d6.cname.frontwize.com/php/v4/folders",
                          data={"session_id": session_id, "parent_folder_id": parent_folder, "page": i, "like": search})
        folders += r.json()['data']

    return folders


def remove_file(session_id: str, file: int, parent_folder: int) -> None:
    """删除文件夹,慎用,很慢"""
    requests.post("https://c34a02aaeb0d6.cname.frontwize.com/php/v4/files_delete",
                  data={"session_id": session_id, "parent_folder_id": parent_folder, "folders_id": "",
                        "files_id": file})


def print_dir(session_id, parent_folder):
    """输出文件夹的所有文件以及目录"""
    t = Table()
    t.add_column("Name")
    t.add_column("Time")
    t.add_column("Size")
    folders = get_folder(session_id, parent_folder)
    for i in folders:
        t.add_row(f"[blue]{i['name']}[/blue]", i['date'], "Folder")
    files = get_file(session_id, parent_folder)
    l = []
    for i in files:
        t.add_row(f"[green]{i['name']}[/green]", i['date'], f"{data_convert(int(i['size']))}")
    console.print(t)


def get_all_file(session_id, id=0, root=Folder({"name": "root", "date": "N/A", "date_int": 0, "id": 0, "parent": 0})):
    """遍历所有文件"""

    All = {
        root: []
    }
    Folders = get_folder(session_id, id)
    Files = get_file(session_id, id)
    for i in Folders:
        folder = Folder(i)
        All[root].append(get_all_file(session_id, folder.id, folder))
    for i in Files:
        All[root].append(File(i))

    return All


def upload_file(session_id, parent_folder, file_path, BLOCK=50 * 1024 * 1024):
    """文件上传, 提供session, 文件夹, 文件本机位置, 分块大小"""
    # print("start")
    size = getsize(file_path)
    r = requests.post("https://c34a02aaeb0d6.cname.frontwize.com/php/v4/need_calc_hash",
                      data={"session_id": session_id, "name": os.path.basename(file_path), "size": size})
    r = requests.post("https://c34a02aaeb0d6.cname.frontwize.com/php/v4/hash_copy",
                      data={"name": os.path.basename(file_path), "key": "", "parent_folder_id": parent_folder,
                            "size": size,
                            "hash": sha256(file_path), "session_id": session_id})
    isOK = r.json()['status']
    # isOK = False
    if isOK is False:
        # print("需要上传")
        # print(r.json())
        if size <= BLOCK:
            # if True:
            file = open(file_path, mode="rb").read()
            # 文件小于等于50MB
            headers = {
                # "Origin": "https://upload.yunzhongzhuan.com",
                'Content-Length': f"{size}",
                "Content-Range": f"0-{size}",
                # "Referer": "https://upload.yunzhongzhuan.com/v10/upload",
                "Cookie": f"PHPSESSID={session_id}",
                "SID": session_id,
                "Filesize": f"{size}",
                "FileName": os.path.basename(file_path),
                "folderOf": f"{parent_folder}",
                "token": sha256(file),
                "Accept-Encoding": "gzip, deflate",
                # "Content-Type": "application/x-www-form-urlencoded",
                # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
            }
            try:
                response = requests.post("https://upload.yunzhongzhuan.com/php/v5/upload", headers=headers, data=file)
            except UnicodeEncodeError:
                headers.update({"FileName": os.path.basename(file_path).encode("utf-8")})
                response = requests.post("https://upload.yunzhongzhuan.com/php/v5/upload", headers=headers, data=file)

            except ConnectionResetError:

                console.print(f"[red]上传{os.path.basename(file_path)}失败, 重试ing...[/red]")
                upload_file(session_id, parent_folder, file_path, BLOCK)
            # response = requests.post("https://upload.yunzhongzhuan.com/php/v5/upload", headers=headers)
            # try:
            #     console.print(response.json())
            #     # console.print(response.headers)
            #     # console.print(response.request.headers)
            # except:
            #     console.print(response.status_code)
            #     console.print(response.text)
            #     console.print(response.request.headers)
            if response.status_code != 200:
                console.print(f"[yellow]上传{os.path.basename(file_path)}可能出现问题[/yellow]")
            else:
                for j in track(range(1), description=f"正在上传{os.path.basename(file_path)}中..."):
                    pass
        else:
            start = 0
            end = BLOCK
            token = ""
            f = open(file_path, mode="rb")
            i = 0
            while start < size:
                start += BLOCK
                i += 1

            start = 0
            end = BLOCK

            for j in track(range(i), description=f"正在上传{os.path.basename(file_path)}中..."):
                # print("a")
                # if True:
                file = f.read(BLOCK)
                # 文件大于50MB
                headers = {
                    # "Origin": "https://upload.yunzhongzhuan.com",
                    'Content-Length': f"{len(file)}",
                    "Content-Range": f"{start}-{end - 1}",
                    # "Referer": "https://upload.yunzhongzhuan.com/v10/upload",
                    "Cookie": f"PHPSESSID={session_id}",
                    # "SID": session_id,
                    # "Filesize": f"{size}",
                    # "FileName": os.path.basename(file_path),
                    # "folderOf": f"{parent_folder}",
                    # "token": sha256(file) + sha256(file_path),
                    # "Accept-Encoding": "gzip, deflate",
                    # "Content-Type": "application/x-www-form-urlencoded",
                    # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
                }
                if start != 0:
                    # 开始传输
                    headers.update({"token": token})
                if start + BLOCK > size:
                    headers['token'] += sha256(file_path)
                    headers.update({
                        "SID": session_id,
                        "Filesize": f"{size}",
                        "FileName": os.path.basename(file_path),
                        "folderOf": f"{parent_folder}",

                    })
                try:
                    response = requests.post("https://upload.yunzhongzhuan.com/php/v5/upload", headers=headers,
                                             data=file)
                except UnicodeEncodeError:
                    headers.update({"FileName": os.path.basename(file_path).encode("utf-8")})
                    response = requests.post("https://upload.yunzhongzhuan.com/php/v5/upload", headers=headers,
                                             data=file)
                except ConnectionResetError:
                    console.print(f"[red]上传{os.path.basename(file_path)}失败, 重试ing...[/red]")
                    upload_file(session_id, parent_folder, file_path, BLOCK)

                # response = requests.post("https://upload.yunzhongzhuan.com/php/v5/upload", headers=headers)
                start += len(file)
                end += len(file)
                if start < size:
                    token = response.json()["token"]

                if response.status_code != 200:
                    console.print(f"[yellow]上传{os.path.basename(file_path)}可能出现问题[/yellow]")
                # try:
                #     console.print(response.json())
                #     console.print(response.headers)
                #     console.print(response.request.headers)
                # except:
                #     console.print(response.status_code)
                #     # console.print(response.text)
                #     console.print(response.request.headers)
    else:
        console.print(f"[green][FastCopy] 快速拷贝文件 {os.path.basename(file_path)}[/green]")


def upload_folder(session_id, parent_folder, file_path, folder: dict, BLOCK=50 * 1024 * 1024):
    """遍历并且上传文件夹所有文件"""

    for i in folder:
        folder_id = create_folder(session_id, parent_folder, i)
        if True:
            d = folder[i]
            for j in d:
                if isinstance(j, dict):
                    for k in j:
                        upload_folder(session_id, folder_id, os.path.join(file_path, k), j)
                        # print(os.path.join(file_path, k))
                else:
                    upload_file(session_id, folder_id, os.path.join(file_path, j), BLOCK)


def create_file_dict(folder_path, name="root") -> dict:
    """创建本地文件字典"""
    file_dict = {name: []}
    for root, dirs, files in os.walk(folder_path):
        for dir in dirs:
            if root == folder_path:
                file_dict[name].append(create_file_dict(os.path.join(root, dir), dir))
        for file in files:
            if root == folder_path:
                file_dict[name].append(file)
    return file_dict


if __name__ == "__main__":
    SESSION_ID = login(USERNAME, PASSWORD, Log=False)
    parent_folder_id = 0

    parent_folder_id = 30533
    print_dir(SESSION_ID, parent_folder_id)
    logout(SESSION_ID)
