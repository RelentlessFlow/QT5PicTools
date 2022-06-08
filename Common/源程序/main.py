import os
import re
import sys
import time
import platform

from PyQt5 import QtWidgets, Qt, QtCore
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QFileDialog,  QWidget, QTextEdit, QGridLayout, \
    QLabel, QLineEdit, QDialog, QPushButton, QMessageBox, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QIcon

import cos
import shelve_serve
from cos import CosServer, CosConfig, resetDB, paramVal


class IndexView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.toolbar = self.addToolBar('toolbar')
        self.initUI()

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

        # 菜单栏绘制
        self.toolbar.addAction(uploadAction)
        self.toolbar.addAction(settingAction)
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
        mainLabel = QLabel('拖拽文件到这里')
        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(mainLabel)

        desLabel = QLabel('模式设定')
        hbox2 = QHBoxLayout()
        hbox2.addStretch(1)
        hbox2.addWidget(desLabel)

        hbox3 = QHBoxLayout()
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
        hbox3.addStretch(1)
        hbox3.addWidget(mdButton)
        hbox3.addWidget(htmlButton)
        hbox3.addWidget(urlButton)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        main_frame.setLayout(vbox)
        self.setCentralWidget(main_frame)

        # 窗体绘制
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('PYQT5极简图床')
        self.setAcceptDrops(True)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)  # 置顶
        self.show()

    def uploadDialog(self):
        fname = QFileDialog.getOpenFileName(self, '选择图片', 'c:\\', 'Image files(*.jpg *.gif *.png)')
        if fname[0]:
            text = self.uploadFileAndCreateURL(fname[0])
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            msg_box = QMessageBox(QMessageBox.Information, '通知', '已写入剪切板')
            msg_box.exec_()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

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
        # self.close()
        settingCosView = SettingCosView()
        # time.sleep(0.5)
        settingCosView.exec()

    def uploadFileAndCreateURL(self, file) -> str:
        cosServer = CosServer()
        url = cosServer.upload_file(file)
        formatText = r""
        if self.getUrlMode() == 1:
            formatText += r"![img](" + url + r')'
        if self.getUrlMode() == 2:
            formatText += r'<img src="' + url + r'" alt="" width="" height="">'
        if self.getUrlMode() == 3:
            formatText = url
        return formatText

    def getUrlMode(self) -> int:
        return shelve_serve.getShelve("url_mode", 1)

    def setUrlMode(self, mode: int):
        shelve_serve.setShelve(
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
        cos.resetDB()
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
            t_config = cos.CosSimpleConfig(
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = IndexView()
    sys.exit(app.exec_())
