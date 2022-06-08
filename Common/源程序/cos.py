import os
import time
import uuid
from typing import List

from qcloud_cos import CosConfig, CosServiceError, CosClientError
from qcloud_cos import CosS3Client
import sys
import logging

import shelve_serve
from shelve_serve import getShelve, setShelve, resetDB


class CosSimpleConfig:
    def __init__(self, secret_id: str, secret_key: str, region: str, bucket: str):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        self.bucket = bucket


def paramVal(*params):
    def val_error(p):
        if p == "" or p is None:
            print("参数为空")
            return True

    for p in params:
        if val_error(p):
            return False


def getDefaultConfig() -> CosSimpleConfig:
    return CosSimpleConfig(
        secret_id="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        secret_key="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        region="ap-beijing",
        bucket="python-1257765810"
    )


class CosServer:
    def __init__(self, start=True):
        # 从shelve中读取cos配置
        cosSimpleConfig: CosSimpleConfig = getShelve(key="cos_config", init=getDefaultConfig())
        self.__config = CosSimpleConfig(
            secret_id=cosSimpleConfig.secret_id,
            secret_key=cosSimpleConfig.secret_key,
            region=cosSimpleConfig.region,
            bucket=cosSimpleConfig.bucket
        )
        if start:
            self.__client = self.__get_client()
        else:
            self.__client: CosS3Client = None

    def __get_client(self, secret_id="", secret_key="", region="") -> CosS3Client:
        # 正常情况日志级别使用INFO，需要定位时可以修改为DEBUG，此时SDK会打印和服务端的通信信息
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        # 1. 设置用户属性, 包括 secret_id, secret_key, region等。
        # Appid 已在CosConfig中移除，请在参数 Bucket 中带上 Appid。Bucket 由BucketName-Appid 组成
        if secret_id == "":
            secret_id = self.__config.secret_id  # 替换为用户的 SecretId，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
        if secret_key == "":
            secret_key = self.__config.secret_key  # 替换为用户的 SecretKey，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
        if region == "":
            region = self.__config.region  # 替换为用户的 region，已创建桶归属的region可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
        # COS支持的所有region列表参见https://www.qcloud.com/document/product/436/6224
        token = None  # 如果使用永久密钥不需要填入token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见https://cloud.tencent.com/document/product/436/14048
        scheme = 'https'  # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)

        # 2. 获取客户端对象
        client: CosS3Client = CosS3Client(config)
        return client

    def upload_file(self, file: str) -> str:
        # 强烈建议您以二进制模式(binary mode)打开文件,否则可能会导致错误
        with open(file, 'rb') as fp:
            dataStr = str(time.strftime('%Y-%m-%d',time.localtime(time.time())))
            rs = self.__client.put_object(
                Bucket=self.__config.bucket,
                Body=fp,
                Key="img/" + dataStr + "/" + str(uuid.uuid4()) + os.path.split(file)[1],
                StorageClass='STANDARD',
                EnableMD5=False
            )
        return rs[1]

    def getConfig(self) -> CosSimpleConfig:
        return self.__config

    def setConfig(self, secret_id, secret_key, region, bucket):
        paramVal(secret_id, secret_key, region, bucket)
        self.__config.secret_id = secret_id
        self.__config.secret_key = secret_key
        self.__config.region = region
        self.__config.bucket = bucket
        # 获取新的客户端对象
        self.__client = self.__get_client()
        setShelve("cos_config", self.__config)

    @classmethod
    def resetConfig(cls):
        resetDB()

    def isBucketExists(self, config: CosSimpleConfig = None) -> List[str]:
        errors = []
        try:
            client: CosS3Client = None
            bucket = ""
            if config is None:
                client = self.__get_client()
                bucket = self.__config.bucket
            if config is not None:
                client = self.__get_client(
                    config.secret_id,
                    secret_key=config.secret_key,
                    region=config.region
                )
                bucket = config.bucket

            f = client.bucket_exists(bucket)
            if not f:
                errors.append("bucket不存在")
        except CosServiceError:
            errors.append("secret_id或secret_key输入错误！！！")
        except CosClientError:
            errors.append("region输入错误！！！")
        return errors
