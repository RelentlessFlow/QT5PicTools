from orm.decorator import insertOne,selectMany

# 用户自定义 OSS 配置
class Oss:
    def __init__(self, id: int, secret_key="", region="", bucket="", userid=""):
        self.id = id
        self.secret_key = secret_key
        self.region = region
        self.bucket = bucket
        self.userid = userid


@insertOne(s="INSERT INTO cool.oss (secret_key, secret_id, region, bucket, userid) VALUES ($secret_key, $secret_id, $region, $bucket, $user_id)")
def addOssConfig(secret_key:str, secret_id:str, region:str, bucket:str, user_id:int):
    pass

@selectMany(s="select * from oss where userid like $user_id", ClassNames=[Oss])
def findOss(user_id:int):
    pass