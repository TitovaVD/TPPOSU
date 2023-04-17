from PyQt5 import uic
from PyQt5 import QtGui, QtWidgets,QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem
import sys

from datetime import datetime

import pymongo
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

import pprint # библа для красивого вывода в консоль
import json

#import ctypes

from plant.plant import Plant
from plant import plantUtils

def getDatabase():       ###database###
    # Create the client
    client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=10)
    try:
        info = client.server_info() # Forces a call.
    except ServerSelectionTimeoutError:
        print("server is down.")
    # Connect to our database
    return client['test']
    ###

### Окно ввода логина и пароля ###
class LoginWindow(QMainWindow):
    userName = ""

    def __init__(self):
        QMainWindow.__init__(self)
        self.loginWindow()

    def loginWindow(self):
        self.ui = uic.loadUi('src/forms/login.ui',self)
        self.setWindowTitle('LoginWindow')
        
        #события
        self.pushButtonLogin.clicked.connect(self.login)
        self.pushButtonRegister.clicked.connect(self.registerUser)

        #self.lineEditLogin.text() введенное имя
        #self.lineEditPassword.text() введенный пароль
        self.labelMessage.setText("")  # сообщения


    #################################
    def login(self):
        posts = dbName.users

        user = posts.find_one({'name': '{name}'.format(name= self.lineEditLogin.text())})

        if (user != None):
            for i in user:             # находим пароль пользователя
                if i == "password":
                    userPassword = user[i]

            if (userPassword != self.lineEditPassword.text()):
                self.labelMessage.setStyleSheet("color: rgb(255, 0, 0)")
                self.labelMessage.setText("Неверный пароль!")

            else:
                LoginWindow.userName = self.lineEditLogin.text()
                self.cams = MainWindow()
                self.cams.show()
                self.close()
                
        else:
            self.labelMessage.setStyleSheet("color: rgb(255, 0, 0)")
            self.labelMessage.setText("Пользователь с таким именем не найден!")


    ###############################

    def registerUser(self):
        posts = dbName.users

        if self.lineEditLogin.text() != "":
            user = posts.find_one({'name': '{name}'.format(name= self.lineEditLogin.text())})
        
            if (user) == None:
                if self.lineEditPassword.text() != "":
                    post = {
                        "name": self.lineEditLogin.text(),
                        "password": self.lineEditPassword.text(),
                        "accessRights": "administrator",
                        "experements": {}
                        }
                    post_id = posts.insert_one(post).inserted_id

                    self.labelMessage.setStyleSheet("color: rgb(0, 255, 0)")
                    self.labelMessage.setText("Пользователь успешно зарегистрирован!")
                    self.lineEditLogin.setText("")
                    self.lineEditPassword.setText("")
                else:
                    self.labelMessage.setStyleSheet("color: rgb(255, 0, 0)")
                    self.labelMessage.setText("Введите пароль!")
            else:
                self.labelMessage.setStyleSheet("color: rgb(255, 0, 0)")
                self.labelMessage.setText("Пользователь с таким именем существует!")
        
        else:
            self.labelMessage.setStyleSheet("color: rgb(255, 0, 0)")
            self.labelMessage.setText("Введите имя пользователя!")
        #pprint.pprint(posts.find_one({"user": "Admin"}))

### Основное окно программы ###
class MainWindow(QMainWindow):
    tableData = {}
    startTime = datetime.now()
    endTime = datetime.now()
    
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = uic.loadUi('src/forms/gui.ui',self)
        self.setWindowTitle('MainWindow')

        self.actionLogout.triggered.connect(self.logout)
        self.actionProcessingWindow.triggered.connect(self.setProcessingWindow)
        self.labelName.setText(LoginWindow.userName)
        self.pushButtonStart.clicked.connect(self.start_measure)
        self.pushButtonSaveResults.clicked.connect(self.saveResults)
        self.pushButtonClearLogs.clicked.connect(self.clearLogs)

        self.progressBar.hide()

        #Настройка ширины столбцов для таблицы логов
        self.tableLogs.setColumnWidth(0, 700)
        self.tableLogs.setColumnWidth(1, 200)

        #Настройка ширины столбцов для таблицы результаты
        for i in range (10):
            self.tableWidget.setColumnWidth(i, 100)

    def saveResults(self):             ###Проверить, что имя эксперимента не пустое
        posts = dbName.users           # Проверить, что есть таблчные данные эксперимента
        posts.find_one_and_update({"name": LoginWindow.userName}, 
                                  {"$set": 
                                    {"experements." + self.lineEditNameOfExp.text(): 
                                       {"startTime" : MainWindow.startTime,
                                        "endTime" : MainWindow.endTime,
                                        "description" : "",
                                        "data" : MainWindow.tableData#json.dumps(MainWindow.tableData, indent = 4)
                                        }
                                    }
                                    }, upsert=False)

    def logout(self):
        self.cams = LoginWindow()
        self.cams.show()
        self.close()

    def write_log(self, message):
        self.tableLogs.insertRow(0)
        self.tableLogs.setItem(0, 0, QtWidgets.QTableWidgetItem(message))
        self.tableLogs.setItem(0, 1, QtWidgets.QTableWidgetItem(str(datetime.now())))
    
    def clearLogs(self):
        self.tableLogs.setRowCount(0)

    def setProcessingWindow(self):
        self.cams = ProcessingWindow()
        self.cams.show()
        self.close()
    
    def start_measure(self):
        self.progressBar.show() # появляется прогрессбар

        get_data = plantUtils.get_data_from_model(plantUtils.channels, plant=plant)
        spin_box = self.spinBox.value() 
        if True:#self.num_data_is_fine(): !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            self.current_measures = []
            self.tableWidget.setRowCount(0)
            self.write_log("Начало опроса")
            MainWindow.startTime = datetime.now()
            for i in range(int(spin_box)):
                result, errors = get_data()
                self.progressBar.setValue(i/(int(spin_box))*100) # увеличение значения прогрессбара
                print(result)

                MainWindow.tableData[str(i)] = result

                if result:
                    if errors:
                        self.write_log("Кадр №" + str(i) + ": " + " ".join(errors))
                    self.tableWidget.insertRow(i)
                    self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(str(round(result[0], 3))))
                    self.current_measures.append([i + 1, *result])
                    
                    for j in range(len(result)-1):
                        cell_data = str(round(result[j + 1], 3))
                        self.tableWidget.setItem(i, j + 1, QtWidgets.QTableWidgetItem(cell_data))
            
            self.write_log("Конец опроса")
            MainWindow.endTime = datetime.now()
            self.progressBar.hide() # скрывается прогрессбар
            


            #print(MainWindow.tableData)
   
        #self.saveButton.setEnabled(True)  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  
###  ###
class ProcessingWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.processingWindow()

        self.actionLogout.triggered.connect(self.logout)
        self.actionRegisterWindow.triggered.connect(self.setRegisterWindow)
        self.labelName.setText(LoginWindow.userName)
    
    def processingWindow(self):
        self.ui = uic.loadUi('src/forms/processing.ui',self)
        self.setWindowTitle('ProcessingWindow')
    
    def logout(self):
        self.cams = LoginWindow()
        self.cams.show()
        self.close()
        #события
        #self.pushButtonLogin.clicked.connect(self.login)
        #self.pushButtonRegister.clicked.connect(self.registerUser)

    def setRegisterWindow(self):
        self.cams = MainWindow()
        self.cams.show()
        self.close()


###  ###
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()

    dbName = getDatabase()

    plant = Plant('src\plant\PlantDLL.dll')

    sys.exit(app.exec_())




    


