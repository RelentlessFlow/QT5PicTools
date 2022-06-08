from db.PictureMapper import Picture, addPic
class PictureSever:
    def __init__(self):
        pass

    def addPictureInfo(self,name, root, path, userid):
        addPic(name, root, path, userid)