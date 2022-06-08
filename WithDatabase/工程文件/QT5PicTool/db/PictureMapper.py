# 图片表
from datetime import datetime
from orm.decorator import insertOne,selectMany


class Picture:
    def __init__(self, id: int, name="", root="", path="", userid="", create_time: datetime = None):
        self.id = id
        self.name = name
        self.root = root
        self.path = path
        self.userid = userid
        self.create_time = create_time


@insertOne(s="INSERT INTO picture (name, root, path, userid, create_time) VALUES ($name, $root, $path, $userid , DEFAULT);")
def addPic(name:str, root:str, path:str, userid:int):
    pass

@selectMany(s="select * from picture where userid like $userid;", ClassNames=[Picture])
def findUserPic(userid:int):
    pass