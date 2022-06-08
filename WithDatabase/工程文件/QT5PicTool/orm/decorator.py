# 对传入的装饰器参数进行处理，生成可以被执行的SQL语句
from string import Template

from orm.executor import selectExecutor, executor

def sqlPre(func, args, s) -> str:
    sql = Template(s)
    parms = {}
    for (key, value) in zip(func.__code__.co_varnames, args):
        if type(value) == str:
            value = "\'" + value + "\'"
        if type(value) == bool:
            if value: value = 1
            if not value: value = 0
        parms[key] = value
    execSQl = sql.substitute(parms)
    print('execSQl:', execSQl)
    return execSQl


# 插入一条数据，返回格式 None，封装了insertOne()
def insertOne(s):
    def wrapper(func):
        def deco(*args, **kwargs):
            execSQl = sqlPre(func, args, s)
            executor(execSQl)
            # 真正执行函数的地方
            func(*args, **kwargs)
        return deco
    return wrapper


# 返回全部数据，返回格式 [ [Table1, Table2], [Table1, Table2], [Table1, Table2] ]，封装了selectExecutor()
def selectManyBase(s):
    def wrapper(func):
        def deco(*args, **kwargs):
            execSQl = sqlPre(func, args, s)
            results = selectExecutor(execSQl)
            # 真正执行函数的地方
            func(*args, **kwargs)
            return results
        return deco
    return wrapper



# 返回第一条数据，返回格式 [Table1, Table2]，封装了selectExecutor()
def selectOne(s, ClassNames: []):
    def wrapper(func):
        def deco(*args, **kwargs):
            execSQl = sqlPre(func, args, s)
            results = selectExecutor(execSQl)
            objArr = []
            if (len(results) > 0):
                i = 0
                for className in ClassNames:
                    obj = className()
                    for v in obj.__dict__.items():
                        setattr(obj, v[0], results[0][i])
                        i += 1
                    objArr.append(obj)
                # 真正执行函数的地方
            func(*args, **kwargs)
            return objArr

        return deco

    return wrapper


# 返回全部数据，返回格式 [ [Table1, Table2], [Table1, Table2], [Table1, Table2] ]，封装了selectExecutor()
def selectMany(s, ClassNames: []):
    def wrapper(func):
        def deco(*args, **kwargs):
            execSQl = sqlPre(func, args, s)
            results = selectExecutor(execSQl)
            objArrs = []
            for result in results:
                objArr = []
                i = 0  # results 中 一项的数组下表
                for className in ClassNames:
                    obj = className()
                    for v in obj.__dict__.items():
                        setattr(obj, v[0], result[i])
                        i += 1
                    objArr.append(obj)
                objArrs.append(objArr)
                # 真正执行函数的地方
            func(*args, **kwargs)
            return objArrs

        return deco

    return wrapper


# 删除一条数据，返回格式 None，封装了deleteExecutor()
def deleteOne(s):
    def wrapper(func):
        def deco(*args, **kwargs):
            execSQl = sqlPre(func, args, s)
            executor(execSQl)
            # 真正执行函数的地方
            func(*args, **kwargs)
        return deco
    return wrapper

def sql(s):
    def wrapper(func):
        def deco(*args, **kwargs):
            execSQl = sqlPre(func, args, s)
            executor(execSQl)
            # 真正执行函数的地方
            func(*args, **kwargs)
        return deco
    return wrapper