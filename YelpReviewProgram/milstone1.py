# Ian Allenfort 011946359
# Ivan Romero 011909215
# Python version: 3.14.3

# Requires:
# - PyQt6
# - psycopg2-binary
# - PostgreSQL with database milestone1db

import sys
import psycopg2

from PyQt6.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from PyQt6 import uic

qtCreatorFile = "MainWindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class milestone1(QMainWindow):
    def __init__(self):
        super(milestone1, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # forces all text to appear as black against the white backgrounds
        self.setStyleSheet("""
            QWidget {
                color: black;
                background-color: white;
            }
            QComboBox, QListWidget, QTableWidget, QLineEdit, QTextEdit {
                color: black;
                background-color: white;
            }
            QComboBox QAbstractItemView {
                color: black;
                background-color: white;
                selection-background-color: #cce8ff;
                selection-color: black;
            }
            QHeaderView::section {
                color: black;
                background-color: #f3f3f3;
            }
            QToolBox::tab {
                color: black;
                background: #e6e6e6;
                border: 1px solid #999;
                border-radius: 3px;
                padding: 8px;
            }
            QToolBox::tab:selected {
                background: white;
                font-weight: bold;
            }
        """)
        self.ui.toolBox.setMaximumHeight(750)

        self.loadStateList()

        self.ui.stateList.currentTextChanged.connect(self.stateChanged)
        self.ui.cityList.itemSelectionChanged.connect(self.cityChanged)
        self.ui.zipcodeList.currentTextChanged.connect(self.zipcodeChanged)
        self.ui.catList.itemSelectionChanged.connect(self.categoryChanged)
        self.ui.clearButton.clicked.connect(self.clearCategorySelection)
        self.ui.refreshButton.clicked.connect(self.refreshPopBus)
        self.ui.refreshButton.clicked.connect(self.refreshSucBus)

    def executeQuery(self, sql_str, params=None):
        try:
            conn = psycopg2.connect(
                dbname="milestone1db",
                user="postgres",
                host="localhost",
                password="pugs",
                port="5432"
            )
        except Exception as e:
            print("Unable to connect to the database!")
            print(e)
            return []

        cur = conn.cursor()

        try:
            if params is None:
                cur.execute(sql_str)
            else:
                cur.execute(sql_str, params)

            conn.commit()

            try:
                result = cur.fetchall()
            except psycopg2.ProgrammingError:
                result = []

        except Exception as e:
            print("Query execution failed:", e)
            result = []

        cur.close()
        conn.close()
        return result

    def executeQueryOne(self, sql_str, params=None):
        results = self.executeQuery(sql_str, params)
        if results and len(results) > 0:
            return results[0]
        return None

    # ---------------- YOUR QUERIES ---------------- #

    def getPopularBusinesses(self, state, city, zipcode):
        sql = """
        WITH zipcode_category_avg AS (
            SELECT
                bc.category,
                AVG(b.numcheckins) AS avg_checkins,
                AVG(b.review_count) AS avg_reviews
            FROM business b
            JOIN business_category bc
                ON b.business_id = bc.business_id
            WHERE b.state = %s
            AND b.city = %s
            AND b.postal_code = %s
            GROUP BY bc.category
        )
        SELECT
            b.name,
            b.stars,
            b.reviewrating,
            b.review_count
        FROM business b
        WHERE b.state = %s
        AND b.city = %s
        AND b.postal_code = %s
        AND EXISTS (
            SELECT 1
            FROM business_category bc
            JOIN zipcode_category_avg a
                ON bc.category = a.category
            WHERE bc.business_id = b.business_id
                AND b.numcheckins > a.avg_checkins
                AND b.review_count > a.avg_reviews
        )
        ORDER BY b.numcheckins DESC, b.review_count DESC;
        """
        return self.executeQuery(sql, (state, city, zipcode, state, city, zipcode))


    def getSuccessfulBusinesses(self, state, city, zipcode):
        sql = """
        WITH zipcode_category_avg AS (
            SELECT
                bc.category,
                AVG(b.reviewrating) AS avg_rating,
                AVG(b.review_count) AS avg_reviews,
                AVG(b.numcheckins) AS avg_checkins
            FROM business b
            JOIN business_category bc
                ON b.business_id = bc.business_id
            WHERE b.state = %s
            AND b.city = %s
            AND b.postal_code = %s
            GROUP BY bc.category
        )
        SELECT
            b.name,
            b.reviewrating,
            b.review_count,
            b.numcheckins
        FROM business b
        WHERE b.state = %s
        AND b.city = %s
        AND b.postal_code = %s
        AND EXISTS (
            SELECT 1
            FROM business_category bc
            JOIN zipcode_category_avg a
                ON bc.category = a.category
            WHERE bc.business_id = b.business_id
                AND b.reviewrating > a.avg_rating
                AND b.review_count > a.avg_reviews
                AND b.numcheckins > a.avg_checkins
        )
        ORDER BY b.reviewrating DESC, b.numcheckins DESC, b.review_count DESC;
        """
        return self.executeQuery(sql, (state, city, zipcode, state, city, zipcode))

    # ---------------- EXISTING UI CODE ---------------- #

    def loadStateList(self):
        self.ui.stateList.clear()
        sql_str = "SELECT DISTINCT state FROM business ORDER BY state;"
        try:
            results = self.executeQuery(sql_str)
            for row in results:
                self.ui.stateList.addItem(row[0])
        except Exception as e:
            print("Query Failed!", e)

        self.ui.stateList.setCurrentIndex(-1)
        self.ui.stateList.clearEditText()

    def stateChanged(self):
        self.ui.cityList.clear()
        self.ui.zipcodeList.clear()
        self.ui.catList.clear()
        self.ui.numBus.clear()
        self.ui.totalPop.clear()
        self.ui.avgIncome.clear()
        self.ui.topCatList.clearContents()

        state = self.ui.stateList.currentText()

        if self.ui.stateList.currentIndex() >= 0:
            sql_str = "SELECT DISTINCT city FROM business WHERE state = %s ORDER BY city;"
            try:
                results = self.executeQuery(sql_str, (state,))
                for row in results:
                    self.ui.cityList.addItem(row[0])
            except Exception as e:
                print("Query failed!", e)

        self.refreshBusinessTable()
        self.refreshCatList()

    def cityChanged(self):
        self.ui.zipcodeList.clear()
        self.ui.numBus.clear()
        self.ui.totalPop.clear()
        self.ui.avgIncome.clear()
        self.ui.topCatList.clearContents()
        self.ui.catList.clear()
        if self.ui.stateList.currentIndex() >= 0 and len(self.ui.cityList.selectedItems()) > 0:
            state = self.ui.stateList.currentText()
            city = self.ui.cityList.selectedItems()[0].text()

            sql = "SELECT DISTINCT postal_code FROM business WHERE state = %s AND city = %s ORDER BY postal_code;"
            try:
                results = self.executeQuery(sql, (state, city))

                self.ui.zipcodeList.blockSignals(True)
                self.ui.zipcodeList.clear()
                self.ui.zipcodeList.addItem("All Zipcodes")

                for row in results:
                    self.ui.zipcodeList.addItem(row[0])

                self.ui.zipcodeList.setCurrentIndex(0)
                self.ui.zipcodeList.blockSignals(False)

            except Exception as e:
                print("Zipcode query failed!", e)

            self.refreshBusinessTable()
        self.refreshCatList()

    def refreshBusinessTable(self):
        if self.ui.stateList.currentIndex() < 0:
            self.clearBusinessTable()
            return

        state = self.ui.stateList.currentText()
        zipcode = self.ui.zipcodeList.currentText()

        sql_str = """
            SELECT b.name, b.address, b.city, b.stars, b.review_count, b.reviewrating, b.numCheckins
            FROM business b
            WHERE b.state = %s
        """
        params = [state]

        if len(self.ui.cityList.selectedItems()) > 0:
            city = self.ui.cityList.selectedItems()[0].text()
            sql_str += " AND b.city = %s"
            params.append(city)

        if zipcode != "" and zipcode != "All Zipcodes":
            sql_str += " AND b.postal_code = %s"
            params.append(zipcode)

        if len(self.ui.catList.selectedItems()) > 0:
            category = self.ui.catList.selectedItems()[0].text()
            sql_str += """
                AND EXISTS (
                    SELECT 1
                    FROM business_category bc
                    WHERE bc.business_id = b.business_id
                    AND bc.category = %s
                )
            """
            params.append(category)

        sql_str += " ORDER BY b.name;"

        try:
            results = self.executeQuery(sql_str, tuple(params))
            self.populateBusinessTable(results)
        except Exception as e:
            print("Query failed!", e)

        self.ui.businessTable.resizeColumnsToContents()

    def zipcodeChanged(self):
        self.refreshCatList()
        self.ui.catList.clearSelection()
        self.refreshBusinessTable()
        self.refreshNumBus()
        self.refreshTotalPop()
        self.refreshAvgIncome()
        self.refreshTopCatList()

    def refreshNumBus(self):
        if self.ui.stateList.currentIndex() < 0 or len(self.ui.cityList.selectedItems()) == 0:
            self.ui.numBus.setText("")
            return

        state = self.ui.stateList.currentText()
        city = self.ui.cityList.selectedItems()[0].text()
        zipcode = self.ui.zipcodeList.currentText()

        sql_str = """
            SELECT COUNT(*)
            FROM business
            WHERE state = %s AND city = %s
        """
        params = [state, city]

        if zipcode != "" and zipcode != "All Zipcodes":
            sql_str += " AND postal_code = %s"
            params.append(zipcode)

        try:
            result = self.executeQueryOne(sql_str, tuple(params))
            if result:
                self.ui.numBus.setText(str(result[0]))
            else:
                self.ui.numBus.setText("0")
        except Exception as e:
            self.ui.numBus.setText("0")
            print("refreshNumBus failed!", e)

    def refreshTotalPop(self):
        zipcode = self.ui.zipcodeList.currentText()

        if zipcode == "" or zipcode == "All Zipcodes":
            self.ui.totalPop.setText("")
            return

        sql_str = "SELECT population FROM zipcodeData WHERE zipcode = %s;"
        params = (zipcode,)

        try:
            result = self.executeQueryOne(sql_str, params)
            if result:
                self.ui.totalPop.setText(str(result[0]))
            else:
                self.ui.totalPop.setText("0")
        except Exception as e:
            self.ui.totalPop.setText("0")
            print("refreshTotalPop failed!", e)

    def refreshAvgIncome(self):
        zipcode = self.ui.zipcodeList.currentText()

        if zipcode == "" or zipcode == "All Zipcodes":
            self.ui.avgIncome.setText("")
            return

        sql_str = "SELECT meanIncome FROM zipcodeData WHERE zipcode = %s;"
        params = (zipcode,)

        try:
            result = self.executeQueryOne(sql_str, params)
            if result:
                self.ui.avgIncome.setText(str(result[0]))
            else:
                self.ui.avgIncome.setText("0")
        except Exception as e:
            self.ui.avgIncome.setText("0")
            print("refreshAvgIncome failed!", e)

    def refreshTopCatList(self):
        self.ui.topCatList.setRowCount(0)
        self.ui.topCatList.setColumnCount(2)
        self.ui.topCatList.setHorizontalHeaderLabels(['# of Business', 'Category'])

        if self.ui.stateList.currentIndex() < 0 or len(self.ui.cityList.selectedItems()) == 0:
            return

        zipcode = self.ui.zipcodeList.currentText()
        if zipcode == "" or zipcode == "All Zipcodes":
            return

        state = self.ui.stateList.currentText()
        city = self.ui.cityList.selectedItems()[0].text()

        sql_str = """
            SELECT COUNT(DISTINCT b.business_id) AS num_businesses, bc.category
            FROM business b
            JOIN business_category bc
                ON b.business_id = bc.business_id
            WHERE b.state = %s
            AND b.city = %s
            AND b.postal_code = %s
            GROUP BY bc.category
            ORDER BY num_businesses DESC, bc.category ASC;
        """
        params = (state, city, zipcode)

        try:
            results = self.executeQuery(sql_str, params)

            if results:
                self.ui.topCatList.setRowCount(len(results))

                currentRowCount = 0
                for row in results:
                    self.ui.topCatList.setItem(currentRowCount, 0, QTableWidgetItem(str(row[0])))
                    self.ui.topCatList.setItem(currentRowCount, 1, QTableWidgetItem(str(row[1])))
                    currentRowCount += 1

        except Exception as e:
            print("refreshTopCatList failed!", e)

    def refreshCatList(self):
        self.ui.catList.blockSignals(True)
        self.ui.catList.clear()

        if self.ui.stateList.currentIndex() < 0:
            self.ui.catList.blockSignals(False)
            return

        state = self.ui.stateList.currentText()
        zipcode = self.ui.zipcodeList.currentText()

        sql_str = """
            SELECT DISTINCT bc.category
            FROM business b
            JOIN business_category bc
                ON b.business_id = bc.business_id
            WHERE b.state = %s
        """
        params = [state]

        if len(self.ui.cityList.selectedItems()) > 0:
            city = self.ui.cityList.selectedItems()[0].text()
            sql_str += " AND b.city = %s"
            params.append(city)

        if zipcode != "" and zipcode != "All Zipcodes":
            sql_str += " AND b.postal_code = %s"
            params.append(zipcode)

        sql_str += " ORDER BY bc.category;"

        try:
            results = self.executeQuery(sql_str, tuple(params))
            for row in results:
                self.ui.catList.addItem(row[0])
        except Exception as e:
            print("refreshCatList failed!", e)

        self.ui.catList.blockSignals(False)

    def categoryChanged(self):
        self.refreshBusinessTable()

    def clearCategorySelection(self):
        self.ui.catList.clearSelection()
        self.refreshBusinessTable()

    def refreshPopBus(self):
        self.ui.popBus.setColumnCount(4)
        self.ui.popBus.setHorizontalHeaderLabels(['Business Name', 'Stars', 'Review Rating', '# of Reviews'])
        self.ui.popBus.setRowCount(0)

        if self.ui.stateList.currentIndex() < 0:
            return
        if len(self.ui.cityList.selectedItems()) == 0:
            return

        zipcode = self.ui.zipcodeList.currentText()
        if zipcode == "" or zipcode == "All Zipcodes":
            return

        state = self.ui.stateList.currentText()
        city = self.ui.cityList.selectedItems()[0].text()

        try:
            results = self.getPopularBusinesses(state, city, zipcode)
            self.ui.popBus.setRowCount(len(results))

            currentRowCount = 0
            for row in results:
                for colCount in range(0, len(row)):
                    self.ui.popBus.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                currentRowCount += 1

            self.ui.popBus.resizeColumnsToContents()

        except Exception as e:
            self.ui.popBus.setRowCount(0)
            print("refreshPopBus failed!", e)

    def refreshSucBus(self):
        self.ui.sucBus.setColumnCount(4)
        self.ui.sucBus.setHorizontalHeaderLabels(['Business Name', 'Review Rating', '# of Reviews', '# of Checkins'])
        self.ui.sucBus.setRowCount(0)

        if self.ui.stateList.currentIndex() < 0:
            return
        if len(self.ui.cityList.selectedItems()) == 0:
            return

        zipcode = self.ui.zipcodeList.currentText()
        if zipcode == "" or zipcode == "All Zipcodes":
            return

        state = self.ui.stateList.currentText()
        city = self.ui.cityList.selectedItems()[0].text()

        try:
            results = self.getSuccessfulBusinesses(state, city, zipcode)
            self.ui.sucBus.setRowCount(len(results))

            currentRowCount = 0
            for row in results:
                for colCount in range(0, len(row)):
                    self.ui.sucBus.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                currentRowCount += 1

            self.ui.sucBus.resizeColumnsToContents()

        except Exception as e:
            self.ui.sucBus.setRowCount(0)
            print("refreshSucBus failed!", e)

    # ---------------- TABLE HELPERS ---------------- #

    def clearBusinessTable(self):
        for i in reversed(range(self.ui.businessTable.rowCount())):
            self.ui.businessTable.removeRow(i)

    def populateBusinessTable(self, results):
        if results:
            self.ui.businessTable.setColumnCount(len(results[0]))
            self.ui.businessTable.setRowCount(len(results))
            self.ui.businessTable.setHorizontalHeaderLabels(['Business Name', 'Address', 'City', 'Stars', 'Review Count', 'Review Rating', 'Number of Checkins'])

            for i, row in enumerate(results):
                for j, val in enumerate(row):
                    self.ui.businessTable.setItem(i, j, QTableWidgetItem(str(val)))
        else:
            self.ui.businessTable.setRowCount(0)
            self.ui.businessTable.setColumnCount(3)
            self.ui.businessTable.setHorizontalHeaderLabels(['Business Name', 'Address', 'City', 'Stars', 'Review Count', 'Review Rating', 'Number of Checkins'])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = milestone1()

    # print("POPULAR TEST:")
    # print(window.getPopularBusinesses("85281", "Restaurants")[:5])
    # print("SUCCESSFUL TEST:")
    # print(window.getSuccessfulBusinesses("85281", "Restaurants")[:5])

    window.show()
    sys.exit(app.exec())