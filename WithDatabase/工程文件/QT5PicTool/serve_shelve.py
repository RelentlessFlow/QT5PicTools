import shelve
import os
from shelve import Shelf


def getShelve(key, init=None) -> Shelf:
    isExists = os.path.exists(os.getcwd() + "/" + "static")
    if not isExists:
        os.makedirs(os.getcwd() + "/" + "static")
    db: Shelf[object] = shelve.open('./static/shelve')  # 构造打开数据文件
    if init is not None and not db.__contains__(key):
        db[key] = init
    return db[key]


def setShelve(key, value, init=None) -> None:
    db: Shelf[object] = shelve.open('./static/shelve')  # 构造打开数据文件
    if init is not None and not db.__contains__(key):
        db[key] = init
    db = shelve.open('./static/shelve')  # 构造打开数据文件
    db[key] = value


def resetDB() -> None:
    isExists = os.path.exists(os.getcwd() + "/" + "static/shelve.orm")
    if isExists:
        os.remove(os.getcwd() + "/" + "static/shelve.orm")
