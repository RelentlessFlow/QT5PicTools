import serve_shelve
from db import VoucherMapper
from db.KeyMapper import getKey

class VoucherServer:
    def isPaid(self):
        return serve_shelve.getShelve("isPaid", False)

    def verifityKey(self, key):
        keys = getKey(key)
        if len(keys) > 0:
            return True
        else:
            return False

    def setPaid(self, userid:int):
        uid = serve_shelve.getShelve('userid')
        VoucherMapper.addVoucher(uid, True)
        serve_shelve.setShelve("isPaid", True)