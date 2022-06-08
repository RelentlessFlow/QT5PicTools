import pymysql

from orm.config import ConnectorConfig


class ConnectorFactory:
    def make(self):
        db = pymysql.connect(host=ConnectorConfig.getConfig().host,
                             user=ConnectorConfig.getConfig().username,
                             password=ConnectorConfig.getConfig().password,
                             database=ConnectorConfig.getConfig().db)
        return db

    def test(self):
        db = self.make()
        cursor = db.cursor()
        cursor.execute("SELECT VERSION()")
        data = cursor.fetchone()
        print("Database version : %s " % data)


connfactory = ConnectorFactory()
