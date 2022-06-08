import datetime
import os
import re
import string
import sys
import time
import platform

from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QFileDialog, QWidget, QGridLayout, \
    QLabel, QLineEdit, QDialog, QPushButton, QMessageBox, QHBoxLayout, QVBoxLayout, QTableWidgetItem, QTableWidget
from PyQt5.QtGui import QIcon

import serve_shelve
import server_pic
import server_user
import server_voucher
from server_cos import CosServer, paramVal


# 登陆窗体
class LoginView(QDialog):

    def __init__(self, username, password, login, register):
        self.username = username
        self.password = password
        self.login = login
        self.register = register
        super().__init__()
        self.initUI()

    def initUI(self):
        usernameLabel = QLabel('用户名')
        passwordLabel = QLabel('密码')

        usernameEdit = QLineEdit(self.username)
        passwordEdit = QLineEdit(self.password)

        # 保存配置
        loginButton = QPushButton("登陆")
        loginButton.clicked.connect(
            lambda: self.login(usernameEdit.text(), passwordEdit.text())
        )

        registerButton = QPushButton("注册")
        registerButton.clicked.connect(
            lambda: self.register()
        )

        quitButton = QPushButton("退出程序")
        quitButton.clicked.connect(qApp.quit)


        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(usernameLabel, 1, 0)
        grid.addWidget(usernameEdit, 1, 1)

        grid.addWidget(passwordLabel, 2, 0)
        grid.addWidget(passwordEdit, 2, 1)

        grid.addWidget(quitButton, 3, 0)
        grid.addWidget(registerButton, 3, 1)
        grid.addWidget(loginButton, 4, 0, 1, 2)

        self.setLayout(grid)
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('欢迎使用QT5图床工具')
        self.show()

# 注册窗体
class RegisterView(QDialog):

    def __init__(self, register):
        super().__init__()
        self.initUI()
        self.register = register

    def initUI(self):
        usernameLabel = QLabel('用户名')
        passwordLabel = QLabel('密码')
        passwordLabelEnter = QLabel('确认密码')

        usernameEdit = QLineEdit('')
        passwordEdit = QLineEdit('')
        passwordEditEnter = QLineEdit('')

        registerButton = QPushButton("注册")
        registerButton.clicked.connect(
            lambda: self.register(usernameEdit.text(), passwordEditEnter.text())
        )

        quitButton = QPushButton("退出程序")
        quitButton.clicked.connect(qApp.quit)


        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(usernameLabel, 1, 0)
        grid.addWidget(usernameEdit, 1, 1)

        grid.addWidget(passwordLabel, 2, 0)
        grid.addWidget(passwordEdit, 2, 1)

        grid.addWidget(passwordLabelEnter, 3, 0)
        grid.addWidget(passwordEditEnter, 3, 1)

        grid.addWidget(quitButton, 4, 0)
        grid.addWidget(registerButton, 4, 1)

        self.setLayout(grid)
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('注册账户')
        self.show()

# 付费激活（存储桶设定）
class VerifyIsPardView(QDialog):

    def __init__(self, verify):
        self.verify = verify
        super().__init__()
        self.initUI()

    def initUI(self):
        keyLabel = QLabel('激活码')
        keyEdit = QLineEdit('')
        registerButton = QPushButton("激活")
        registerButton.clicked.connect(
            lambda x:self.verify(keyEdit.text())
        )

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(keyLabel, 1, 0)
        grid.addWidget(keyEdit, 1, 1)
        grid.addWidget(registerButton, 2, 1)
        self.setLayout(grid)
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle("自定义存储桶功能激活")
        self.show()

# 主页
class IndexView(QMainWindow):
    def __init__(self):
        # 服务注入
        userServer = server_user.UserServer

        # 登陆窗体处理
        def openLoginWindow():
            def tapLogin(u, p):  # 登陆点击事件
                if userServer.login(userServer, u, p) == None:
                    av = AlertView('用户或者密码错误！')
                    av.exec_()
                else:
                    av = AlertView('登陆成功！')
                    av.exec_()
                    self.refreshWindow()

            def registerViewTapRegister(username, password):  # 注册界面点击注册按钮的事件回调
                userServer.register(userServer, username, password, "")
                av = AlertView('注册成功！')
                av.exec_()
                time.sleep(0.5)
                # self.refreshWindow()
                initMainApplication()

            def tapRegister():  # 注册点击事件
                rv = RegisterView(register=lambda u, p: registerViewTapRegister(u, p))
                rv.exec_()

            userServer.loginOut(userServer)
            u = userServer.getUserNameBySheleve(userServer)
            p = userServer.getPasswordBySheleve(userServer)
            loginView = LoginView(username=u, password=p, login=lambda u, p: tapLogin(u, p), register=tapRegister)
            loginView.exec()

        # 上上传图片按钮事件
        def uploadDialog(self):
            fname = QFileDialog.getOpenFileName(self, '选择图片', 'c:\\', 'Image files(*.jpg *.gif *.png)')
            if fname[0]:
                text = self.uploadFileAndCreateURL(fname[0])
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
                msg_box = QMessageBox(QMessageBox.Information, '通知', '已写入剪切板')
                msg_box.exec_()

        # 拖拽图片事件
        def dragEnterEvent(event):
            if event.mimeData().hasUrls:
                event.accept()
            else:
                event.ignore()


        # 已上传图片点击事件回调
        def exportImgsInfo():
            import pandas as pd
            from pandas import DataFrame
            table_name = "data"
            from orm.connectFactory import connfactory
            conn = connfactory.make()
            sql = "select * from picture where userid like 1;"
            df = pd.read_sql(sql, conn)
            isExists = os.path.exists(os.getcwd() + "/" + "xlsx")
            if not isExists:
                os.makedirs(os.getcwd() + "/" + "xlsx")
            timeStr = time.ctime()
            df.to_excel(os.getcwd() + "/xlsx/" + timeStr + '.xlsx', index=0)
            QMessageBox(QMessageBox.Information, '通知', '图片数据导出已完成')
            os.popen("open ./xlsx")



        self.openLoginWindow = openLoginWindow
        self.uploadDialog = uploadDialog
        self.dragEnterEvent = dragEnterEvent
        self.exportImgsInfo = exportImgsInfo

        if userServer.isLogin(userServer):
            super().__init__()
            self.toolbar = self.addToolBar('toolbar')
            self.initUI()

        elif not userServer.isLogin(userServer): # 如果没登陆，加载登陆窗体
            openLoginWindow()





    def initUI(self):
        # 状态栏配置
        exitAction = QAction(QIcon('static/icon/exit.png'), '退出', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)

        # 打开配置COS的View
        settingAction = QAction(QIcon('static/icon/setting.png'), '设置', self)
        settingAction.setShortcut('Ctrl+E')
        settingAction.triggered.connect(self.openSettingCosView)

        # 上传图片
        uploadAction = QAction(QIcon('static/icon/upload.png'), '上传文件', self)
        uploadAction.setShortcut('Ctrl+U')
        uploadAction.triggered.connect(self.uploadDialog)

        # 加载登陆界面
        loginAction = QAction(QIcon('static/icon/login.png'), '登陆', self)
        loginAction.setShortcut('Ctrl+L')
        loginAction.triggered.connect(self.openLoginWindow)

        # 图片上传信息
        picsAction = QAction(QIcon('static/icon/imgs.png'), '图片列表', self)
        picsAction.setShortcut('Ctrl+P')
        picsAction.triggered.connect(self.exportImgsInfo)
        # picsAction.triggered.connect(lambda : print('sssss'))

        # 菜单栏绘制
        self.toolbar.addAction(uploadAction)
        self.toolbar.addAction(settingAction)
        self.toolbar.addAction(picsAction)
        self.toolbar.addAction(loginAction)
        self.toolbar.addAction(exitAction)

        # 状态栏绘制
        # 处理服务器连接问题
        cosServer = CosServer()
        errors = cosServer.isBucketExists()
        statusDisplayStr = ""
        if errors.__len__() == 0:
            statusDisplayStr += '存储桶已经准备就绪\t'
        else:
            for e in errors:
                statusDisplayStr += e + "\t"
        # 处理上传模式
        mode = self.getUrlModeMap(self.getUrlMode())
        statusDisplayStr += "当前模式:" + mode + "\t"
        self.statusBar().showMessage(statusDisplayStr)

        # 绘制主体
        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        mainLabel = QLabel('拖拽文件到这里')
        hbox1.addWidget(mainLabel)

        hbox2 = QHBoxLayout()
        hbox2.addStretch(1)
        userLabel = QLabel('当前用户：' + server_user.UserServer().getUserNameBySheleve())
        hbox2.addWidget(userLabel)

        hbox3 = QHBoxLayout()
        hbox3.addStretch(1)
        desLabel = QLabel('模式设定')
        hbox3.addWidget(desLabel)

        hbox4 = QHBoxLayout()
        main_frame = QWidget()
        mdButton = QPushButton("Markdown")
        mdButton.clicked.connect(
            lambda: self.setUrlMode(1)
        )
        htmlButton = QPushButton("HTML")
        htmlButton.clicked.connect(
            lambda: self.setUrlMode(2)
        )
        urlButton = QPushButton("URL")
        urlButton.clicked.connect(
            lambda: self.setUrlMode(3)
        )
        hbox4.addStretch(1)
        hbox4.addWidget(mdButton)
        hbox4.addWidget(htmlButton)
        hbox4.addWidget(urlButton)


        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        main_frame.setLayout(vbox)
        self.setCentralWidget(main_frame)

        # 窗体绘制
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('PYQT5极简图床')
        self.setAcceptDrops(True)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)  # 置顶
        self.show()



    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            try:
                event.setDropAction(Qt.Qt.CopyAction)
            except Exception as e:
                print(e)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        try:
            if event.mimeData().hasUrls:
                event.setDropAction(Qt.Qt.CopyAction)
                event.accept()
                link = event.mimeData().urls()[0].path()
                if platform.system() == "Windows":
                    link = link[1:]
                # 文件拓展名验证
                ext = os.path.splitext(link)[1]
                exp_available = False
                pic_exps = ['.jpg', '.jpeg', '.gif', '.png']
                for p in pic_exps:
                    if re.search(ext, p, re.IGNORECASE):
                        exp_available = True
                if ext != "" and exp_available:
                    text = self.uploadFileAndCreateURL(link)
                    clipboard = QApplication.clipboard()
                    clipboard.setText(text)
                    msg_box = QMessageBox(QMessageBox.Information, '通知', '已写入剪切板')
                    msg_box.exec_()
                else:
                    msg_box = QMessageBox(QMessageBox.Warning, '错误', '请不要将非图片拖入其中！')
                    msg_box.exec_()
            else:
                event.ignore()
        except Exception as e:
            print(e)

    def openSettingCosView(self):
        def verifyKey(key):
            server = server_user.UserServer()
            if server_voucher.VoucherServer().verifityKey(key):
                server_voucher.VoucherServer().setPaid(server.getIdBySheleve())
                av = AlertView(message="已激活")
                av.exec_()
            else:
                server_voucher.VoucherServer().setPaid(server.getIdBySheleve())
                av = AlertView(message="密钥不正确")
                av.exec_()



        paid = server_voucher.VoucherServer().isPaid()
        if paid:
            # self.close()
            settingCosView = SettingCosView()
            # time.sleep(0.5)
            settingCosView.exec()
        else:
            vv= VerifyIsPardView(verifyKey)
            vv.exec_()

    # 上传并且创建格式化URL
    def uploadFileAndCreateURL(self, file) -> str:
        cosServer = CosServer()
        rs = cosServer.upload_file(file)
        root = rs.get('root')
        filePath = rs.get('file')
        filename = filePath.split('/')[-1]
        path = rs.get('path')
        url = rs.get('url')
        userid = server_user.UserServer().getIdBySheleve()
        picServer = server_pic.PictureSever()
        picServer.addPictureInfo(filename, root, path, userid)

        # url_items = url.split('/')
        # filename = url_items[-1]

        formatText = r""
        if self.getUrlMode() == 1:
            formatText += r"![img](" + url + r')'
        if self.getUrlMode() == 2:
            formatText += r'<img src="' + url + r'" alt="" width="" height="">'
        if self.getUrlMode() == 3:
            formatText = url
        return formatText

    def getUrlMode(self) -> int:
        return serve_shelve.getShelve("url_mode", 1)

    def setUrlMode(self, mode: int):
        serve_shelve.setShelve(
            "url_mode", mode)
        self.refreshWindow()

    def getUrlModeMap(self, mode: int) -> str:
        if mode == 1:
            return "Markdown"
        if mode == 2:
            return "HTML"
        if mode == 3:
            return "URL"

    # 刷新窗口
    def refreshWindow(self):
        self.close()
        iw = IndexView()
        time.sleep(0.01)
        iw.show()


# 存储桶
class SettingCosView(QDialog):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        secretId = QLabel('secret_id')
        secretKey = QLabel('secret_key')
        region = QLabel('region')
        bucket = QLabel('bucket')

        csObj = CosServer(False)
        cosConfig = csObj.getConfig()

        secretIdValue = cosConfig.secret_id
        secretKeyValue = cosConfig.secret_key
        regionValue = cosConfig.region
        bucketValue = cosConfig.bucket

        secretIdEdit = QLineEdit(secretIdValue)
        secretKeyEdit = QLineEdit(secretKeyValue)
        regionEdit = QLineEdit(regionValue)
        bucketEdit = QLineEdit(bucketValue)

        # 保存配置
        okButton = QPushButton("保存")
        okButton.clicked.connect(
            lambda: self.saveSetting(
                secret_id=secretIdEdit.text(),
                secret_key=secretKeyEdit.text(),
                region=regionEdit.text(),
                bucket=bucketEdit.text()
            )
        )

        cancelButton = QPushButton("返回")
        cancelButton.clicked.connect(self.closeWindows)
        # 重置配置
        resetButton = QPushButton("恢复预设")
        resetButton.clicked.connect(self.resetSetting)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(secretId, 1, 0)
        grid.addWidget(secretIdEdit, 1, 1)

        grid.addWidget(secretKey, 2, 0)
        grid.addWidget(secretKeyEdit, 2, 1)

        grid.addWidget(region, 3, 0)
        grid.addWidget(regionEdit, 3, 1)

        grid.addWidget(bucket, 4, 0)
        grid.addWidget(bucketEdit, 4, 1)

        grid.addWidget(cancelButton, 5, 0)
        grid.addWidget(resetButton, 5, 1)
        grid.addWidget(okButton, 6, 0, 1, 2)

        self.setLayout(grid)
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('COS对象云存储配置')
        self.show()

    # 关闭窗体
    def closeWindows(self):
        self.close()

    # 重置设定
    def resetSetting(self):
        serve_shelve.resetDB()
        self.close()
        settingCosView = SettingCosView()
        time.sleep(0.5)
        settingCosView.exec()

    # 保存设定
    def saveSetting(self, secret_id, secret_key, region, bucket):
        flag = paramVal(secret_id, secret_key, region, bucket)
        if flag is False:
            msg_box = QMessageBox(QMessageBox.Warning, '警告', '请填写好全部参数！！！')
            msg_box.exec_()
        else:
            cosServer = CosServer()
            t_config = cosServer.CosSimpleConfig(
                secret_id=secret_id,
                secret_key=secret_key,
                region=region,
                bucket=bucket
            )
            errors = cosServer.isBucketExists(
                t_config
            )
            if errors.__len__() == 0:
                cosServer.setConfig(
                    secret_id=secret_id,
                    secret_key=secret_key,
                    region=region,
                    bucket=bucket
                )
                msg_box = QMessageBox(QMessageBox.Warning, '成功', "保存成功")
                msg_box.exec_()
                self.close()
            else:
                for e in errors:
                    msg_box = QMessageBox(QMessageBox.Warning, '错误', e)
                    msg_box.exec_()
                msg_box = QMessageBox(QMessageBox.Warning, '错误', "保存失败")
                msg_box.exec_()

# 自定义提示框
class AlertView(QDialog):
    def __init__(self, message: str):
        self.message = message
        super().__init__()
        self.initUI()
    def initUI(self):
        message = QLabel(self.message)
        cancelButton = QPushButton("返回")
        cancelButton.clicked.connect(self.closeWindows)
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(message, 1, 0)
        grid.addWidget(cancelButton, 2   , 0)

        self.setLayout(grid)
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('提示')
        self.show()
    # 关闭窗体
    def closeWindows(self):
        self.close()


# 应用程序初始化
def initMainApplication():
    app = QApplication(sys.argv)
    ex = IndexView()
    sys.exit(app.exec_())

if __name__ == '__main__':
    initMainApplication()
