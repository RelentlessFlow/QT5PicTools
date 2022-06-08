import json

class ConnectorConfig():
    def __init__(self, host, port, db, username, password):
        self.host = host
        self.port = port
        self.db = db
        self.username = username
        self.password = password

    @classmethod
    def getConfig(cls):
        f = open('/Users/green/Documents/GitHub/QT5PicTool/orm/db.json')
        data = json.load(f)
        config = ConnectorConfig(**data['mysql'])
        return config