from orm.decorator import insertOne, selectOne


class Vertifykeys:
    def __init__(self, k: str):
        self.k = k


@selectOne(s="select * from vertifykeys where k like $k;", ClassNames=[Vertifykeys])
def getKey(k: str):
    pass
