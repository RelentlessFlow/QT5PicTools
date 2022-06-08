from datetime import datetime

from orm.decorator import selectOne, deleteOne, insertOne

# 付费凭证
class Voucher:
    def __init__(self, id: int, userid: int, paid: bool, paid_time: datetime):
        self.id = id
        self.userid = userid
        self.paid = paid
        self.paid_time = paid_time

@insertOne('INSERT INTO cool.voucher (userid, paid, paid_time) VALUES ($user_id, $status, DEFAULT)')
def addVoucher(user_id: int, status: bool):
    pass

@selectOne('select * from voucher where userid = $user_id;', ClassNames=[Voucher])
def findVoucher(user_id: int) -> Voucher:
    pass
