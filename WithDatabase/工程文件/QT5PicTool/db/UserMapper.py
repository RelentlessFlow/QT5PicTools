from datetime import datetime
from orm.decorator import selectOne, deleteOne, insertOne

# 用户表
class User:
    def __init__(self, id: int = None, username: str = "", password: str = "", remark: str = ""):
        self.id = id
        self.username = username
        self.password = password
        self.remark = remark


@selectOne(s="select * from user where username like $username and password like $password", ClassNames=[User])
def findUser(username: str, password: str) -> list: pass


@deleteOne(s="delete from user where id = $id")
def removeUser(id: int): pass


@insertOne(s="INSERT INTO user(username, password, remark) VALUE ($username,$password,$remark);")
def addUser(username: str, password: str, remark: str): pass

