import serve_shelve
from db import UserMapper


class UserServer:
    def __init__(self, username = "", password = ""):
        self.username = username
        self.password = password

    def isLogin(self):
        s = serve_shelve.getShelve("isLogin", False)
        return s

    def login(self, username, passwword):
        userList = UserMapper.findUser(username, passwword)
        if len(userList) > 0:
            serve_shelve.setShelve("isLogin", True)
            serve_shelve.setShelve("username", userList[0].username)
            serve_shelve.setShelve("password", userList[0].password)
            serve_shelve.setShelve("userid", userList[0].id)
            return userList[0]

    def loginOut(self):
        serve_shelve.getShelve("isLogin", False)

    def register(self, username, password, remark):
        UserMapper.addUser(username, password, remark)

    def getUserNameBySheleve(self):
        return serve_shelve.getShelve("username", '')

    def getPasswordBySheleve(self):
        return serve_shelve.getShelve("password", '')

    def getIdBySheleve(self):
        return serve_shelve.getShelve("userid", '')