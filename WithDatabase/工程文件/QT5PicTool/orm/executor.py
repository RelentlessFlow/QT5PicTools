from string import Template

from orm.connectFactory import connfactory

# 对SQL语句(无返回值)的执行进行了封装，
def executor(sql):
    db = connfactory.make()
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        print('Error:executor(',sql + ')!')
        print('db.rollback()')
    return cursor.fetchall()


# 对SQL查询语句的执行进行了封装，
def selectExecutor(sql):
    cursor = connfactory.make().cursor()
    try:
        cursor.execute(sql)
    except:
        print('Error:selectExecutor(',sql + ')!')
    return cursor.fetchall()




