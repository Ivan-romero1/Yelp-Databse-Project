# Ian Allenfort 011946359
# Python version: 3.14.3

# Requires:
# - PyQt6
# - psycopg2-binary
# - PostgreSQL with database milestone1db

import sys
import psycopg2

from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout
)
from PyQt6 import uic, QtCore
from PyQt6.QtGui import QAction, QIcon, QPixmap

qtCreatorFile = "MainWindow.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class milestone1(QMainWindow):
    def __init__(self):
        super(milestone1, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.loadStateList()
        self.ui.stateList.currentTextChanged.connect(self.stateChanged)
        self.ui.cityList.itemSelectionChanged.connect(self.cityChanged)
        self.ui.zipcodeList.currentTextChanged.connect(self.zipcodeChanged)
        self.ui.bname.textChanged.connect(self.getBusinessNames)
        self.ui.businesses.itemSelectionChanged.connect(self.displayBusinessCity)

    def executeQuery(self, sql_str):
        try:
            conn = psycopg2.connect("dbname='milestone1db' user='postgres' host='localhost' password='Lalito0611' ")
        except:
            print('Unable to connect to the database!')
        cur = conn.cursor()
        cur.execute(sql_str)
        conn.commit()
        result = cur.fetchall()
        conn.close()
        return result

    def loadStateList(self):    # Fills state dropdown box
        self.ui.stateList.clear()
        sql_str = "SELECT DISTINCT state FROM business ORDER BY state;"
        try:
            results = self.executeQuery(sql_str)
            # Fill stateList dropdown box with all states in database
            for row in results:
                self.ui.stateList.addItem(row[0])
        except:
            print("Query Failed!")
        self.ui.stateList.setCurrentIndex(-1)
        self.ui.stateList.clearEditText()

    def stateChanged(self):
        self.ui.cityList.clear()
        self.ui.zipcodeList.clear()
        state = self.ui.stateList.currentText()
        if (self.ui.stateList.currentIndex()>=0):
            sql_str = "SELECT distinct city FROM business WHERE state ='" + state + "' ORDER BY city;"
            try:
                results = self.executeQuery(sql_str)
                for row in results:
                    self.ui.cityList.addItem(row[0])
            except:
                print("Query failed!")

        for i in reversed(range(self.ui.businessTable.rowCount())):
            self.ui.businessTable.removeRow(i)
        sql_str = "SELECT name, city, state FROM business  WHERE state = '" + state + "' ORDER BY name ;"
        try:
            results = self.executeQuery(sql_str)
            style = "::section {" "background-color: #f3f3f3; }"
            self.ui.businessTable.horizontalHeader().setStyleSheet(style)
            self.ui.businessTable.setColumnCount(len(results[0]))
            self.ui.businessTable.setRowCount(len(results))
            self.ui.businessTable.setHorizontalHeaderLabels(['Business Name', 'City', 'State'])
            self.ui.businessTable.resizeColumnsToContents()
            self.ui.businessTable.setColumnWidth(0, 300)
            self.ui.businessTable.setColumnWidth(1, 100)
            self.ui.businessTable.setColumnWidth(2, 50)
            currentRowCount = 0
            for row in results:
                for colCount in range (0,len(results[0])):
                    self.ui.businessTable.setItem(currentRowCount,colCount,QTableWidgetItem(row[colCount]))
                currentRowCount += 1
        except:
            print("Query failed!")

    def cityChanged(self):
        if (self.ui.stateList.currentIndex() >= 0) and (len(self.ui.cityList.selectedItems()) > 0):
            state = self.ui.stateList.currentText()
            city = self.ui.cityList.selectedItems()[0].text()

            zipcode_sql = "SELECT DISTINCT postal_code FROM business WHERE state = '" + state + "' AND city = '" + city + "' ORDER BY postal_code;"
            try:
                zipcodeResults = self.executeQuery(zipcode_sql)
                self.ui.zipcodeList.blockSignals(True)
                self.ui.zipcodeList.clear()
                self.ui.zipcodeList.addItem("All Zipcodes")
                for row in zipcodeResults:
                    self.ui.zipcodeList.addItem(row[0])
                self.ui.zipcodeList.setCurrentIndex(0)
                self.ui.zipcodeList.blockSignals(False)
            except:
                print("Zipcode query failed!")

            self.refreshBusinessTable()

    def refreshBusinessTable(self):
        if (self.ui.stateList.currentIndex() >= 0) and (len(self.ui.cityList.selectedItems()) > 0):
            state = self.ui.stateList.currentText()
            city = self.ui.cityList.selectedItems()[0].text()
            zipcode = self.ui.zipcodeList.currentText()

            sql_str = "SELECT name, city, state FROM business WHERE state = '" + state + "' AND city = '" + city + "'"

            if zipcode != "" and zipcode != "All Zipcodes":
                sql_str += " AND postal_code = '" + zipcode + "'"

            sql_str += " ORDER BY name;"

            try:
                results = self.executeQuery(sql_str)
                style = "::section {" "background-color: #f3f3f3; }"
                self.ui.businessTable.horizontalHeader().setStyleSheet(style)
                self.ui.businessTable.setColumnCount(len(results[0]))
                self.ui.businessTable.setRowCount(len(results))
                self.ui.businessTable.setHorizontalHeaderLabels(['Business Name', 'City', 'State'])
                self.ui.businessTable.resizeColumnsToContents()
                self.ui.businessTable.setColumnWidth(0, 300)
                self.ui.businessTable.setColumnWidth(1, 100)
                self.ui.businessTable.setColumnWidth(2, 50)

                currentRowCount = 0
                for row in results:
                    for colCount in range(0, len(results[0])):
                        self.ui.businessTable.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                    currentRowCount += 1
            except:
                print("Query failed!")

    def zipcodeChanged(self):
        self.refreshBusinessTable()

    def getBusinessNames(self):
        self.ui.businesses.clear()
        businessName = self.ui.bname.text()
        sql_str = "SELECT name FROM business WHERE name LIKE '%"+ businessName +"%' ORDER BY name;"
        try:
            results = self.executeQuery(sql_str)
            for row in results:
                self.ui.businesses.addItem(row[0])
        except:
            print("Query failed!")

    def displayBusinessCity(self):
        if len(self.ui.businesses.selectedItems()) == 0:
            self.ui.bcity.clear()
            return
    
        businessName = self.ui.businesses.selectedItems()[0].text()
        sql_str = "SELECT city FROM business WHERE name = '" + businessName + "';"
        try:
            results = self.executeQuery(sql_str)
            self.ui.bcity.setText(results[0][0])
        except:
            self.ui.bcity.clear()
            print("Query failed!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = milestone1()
    window.show()
    sys.exit(app.exec())