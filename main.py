import sys
import platform
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect,
                          QSize, QTime, QUrl, Qt, QEvent, QThreadPool, QTimer)
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence,
                         QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PyQt5.QtWidgets import *
from PyQt5.QtChart import QChart, QChartView, QBarSet, QPercentBarSeries, QBarCategoryAxis, QBarSeries

from ui_main import Ui_MainWindow
from monitor.Monitor import Monitor
from monitor.Cockroach import CRDB

import json

class Object(object):
    pass

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        with open("config.json") as file:
            self.config = json.load(file)
        print(self.config)

        self.initialize_db()
        self.show()

        self.update_styles()

        self.create_settings()
        self.create_summary()

        self.monitor = Monitor(self.config['settings']['mouse_timeout'])
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.run_monitor)
        self.timer.start()

    def create_settings(self):
        if self.ui.settingsCreateGroupTimezoneComboBox.count() == 0:
            self.ui.settingsCreateGroupTimezoneComboBox.addItems(['one', 'two'])

        group = self.db.get_user_groups()

        if len(group) > 1:
            self.ui.settingsCurrentGroupLabel.setText(group[0])
        else:
            self.ui.settingsCurrentGroupLabel.setText("")

        self.ui.settingsGroupList.clear()

        for i in range(0, len(group)):
            if group[i] != 'global':
                self.ui.settingsGroupList.addItem(group[i])

        out = Object()
        out.text = lambda: group[0]

        self.ui.settingsGroupList.sortItems()
        if len(group) > 1:
            self.settings_group_item_clicked(out)
        else:
            self.settings_group_item_clicked()

    def create_summary(self):
        set0 = QBarSet("data")

        # set0 << 1 << 2 << 3 << 4 << 5 << 6 << 7
        # print(set0)
        set0.append(1)
        set0.append(2)

        series = QBarSeries()
        series.append(set0)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("This Week")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        categories = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
        axis = QBarCategoryAxis()
        axis.append(categories)
        chart.createDefaultAxes()
        chart.setAxisX(axis, series)

        chart.legend().setVisible(False)

        chartView = QChartView(chart)
        chartView.setRenderHint(QPainter.Antialiasing)

        self.ui.summaryChartLayout.addWidget(chartView)

    def update_styles(self):
        #background-color: rgb(198, 161, 106);
        #background-color: rgb(198, 161, 106);
        #border: 0px;
        flatButtonStyle = "QPushButton{border-color: rgb(0, 0, 0);\nbackground-color: #b2c2a5;\ncolor: rgb(255, 255, 255);\nborder-radius: 8px;\npadding: 8;\ntransition: 0.3s;}QPushButton:hover{border-color: rgb(0, 0, 0);\nbackground-color:rgb(255, 255, 255);\ncolor:  rgb(123, 139, 111);\nborder-radius: 8px;\npadding: 8;}"
        self.ui.sidebar.setStyleSheet(flatButtonStyle)

    def settings_group_item_clicked(self, item=None):
        if item is None:
            self.ui.settingsCurrentGroupLabel.setText("")
            self.ui.settingsMemberList.clear()
            self.ui.timeZoneLabel.setText("")
        else:
            self.ui.settingsCurrentGroupLabel.setText(item.text())
            members = self.db.get_members_in_group(item.text())
            self.ui.settingsMemberList.clear()
            for i in range(len(members)):
                self.ui.settingsMemberList.addItem(members[i])
            self.ui.timeZoneLabel.setText(self.db.get_group_timezone(item.text()))

    def run_monitor(self):
        res = self.monitor.update_time_window()
        if type(res) != bool:
            self.db.add_tracking_data(res.name, res.process, res.start_time, res.end_time)

    def initialize_db(self):
        if self.config['account']['user_id'] != "":
            self.db = CRDB(self.config['account']['name'], self.config['account']['timezone'],
                           self.config['account']['user_id'])
        else:
            self.db = CRDB(self.config['account']['name'], self.config['account']['timezone'])

    def switchPage1(self):
        self.ui.stackedPanels.setCurrentIndex(0)

    def switchPage2(self):
        self.ui.stackedPanels.setCurrentIndex(1)

    def switchPage3(self):
        self.ui.stackedPanels.setCurrentIndex(2)

    def switchPage4(self):
        self.ui.stackedPanels.setCurrentIndex(3)

    def settings_join_group_clicked(self):
        group_name = self.ui.settingsJoinGroupNameTextBox.toPlainText()
        if group_name != "":
            self.db.join_group(group_name)
            self.create_settings()

    def settings_create_group_clicked(self):
        group_name = self.ui.settingsCreateGroupNameTextBox.toPlainText()
        timezone = self.ui.settingsCreateGroupTimezoneComboBox.currentText()
        print(group_name)
        print(timezone)
        if group_name != "" and timezone != "":
            self.db.create_group(group_name, timezone)
            self.db.join_group(group_name)
            self.create_settings()

    def settings_leave_group_clicked(self):
        if self.ui.settingsGroupList.currentItem() is None:
            return
        group_name = self.ui.settingsGroupList.currentItem().text()
        print(group_name)
        self.db.leave_group(group_name)
        self.create_settings()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
