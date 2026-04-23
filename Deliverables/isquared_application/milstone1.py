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

        self.loadStateList()

        self.ui.stateList.currentTextChanged.connect(self.stateChanged)
        self.ui.cityList.itemSelectionChanged.connect(self.cityChanged)
        self.ui.zipcodeList.currentTextChanged.connect(self.zipcodeChanged)
        self.ui.bname.textChanged.connect(self.getBusinessNames)
        self.ui.businesses.itemSelectionChanged.connect(self.displayBusinessCity)

    def executeQuery(self, sql_str, params=None):
        try:
            conn = psycopg2.connect(
                dbname="milestone1db",
                user="postgres",
                host="localhost",
                password="Lalito0611",
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

    def getPopularBusinesses(self, zipcode, category):
        sql = """
        WITH zipcode_category_avg AS (
            SELECT
                b.postal_code,
                bc.category,
                AVG(b.numcheckins) AS avg_checkins,
                AVG(b.review_count) AS avg_reviews
            FROM business b
            JOIN business_category bc
                ON b.business_id = bc.business_id
            WHERE b.postal_code = %s
              AND bc.category = %s
            GROUP BY b.postal_code, bc.category
        )
        SELECT
            b.name,
            b.numcheckins,
            b.review_count
        FROM business b
        JOIN business_category bc
            ON b.business_id = bc.business_id
        JOIN zipcode_category_avg a
            ON b.postal_code = a.postal_code
           AND bc.category = a.category
        WHERE b.postal_code = %s
          AND bc.category = %s
          AND b.numcheckins > a.avg_checkins
          AND b.review_count > a.avg_reviews
        ORDER BY b.numcheckins DESC, b.review_count DESC;
        """
        return self.executeQuery(sql, (zipcode, category, zipcode, category))

    def getSuccessfulBusinesses(self, zipcode, category):
        sql = """
        WITH zipcode_category_avg AS (
            SELECT
                b.postal_code,
                bc.category,
                AVG(b.reviewrating) AS avg_rating,
                AVG(b.review_count) AS avg_reviews,
                AVG(b.numcheckins) AS avg_checkins
            FROM business b
            JOIN business_category bc
                ON b.business_id = bc.business_id
            WHERE b.postal_code = %s
              AND bc.category = %s
            GROUP BY b.postal_code, bc.category
        )
        SELECT
            b.name,
            b.reviewrating,
            b.review_count,
            b.numcheckins
        FROM business b
        JOIN business_category bc
            ON b.business_id = bc.business_id
        JOIN zipcode_category_avg a
            ON b.postal_code = a.postal_code
           AND bc.category = a.category
        WHERE b.postal_code = %s
          AND bc.category = %s
          AND b.reviewrating > a.avg_rating
          AND b.review_count > a.avg_reviews
          AND b.numcheckins > a.avg_checkins
        ORDER BY b.reviewrating DESC, b.numcheckins DESC, b.review_count DESC;
        """
        return self.executeQuery(sql, (zipcode, category, zipcode, category))

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
        state = self.ui.stateList.currentText()

        if self.ui.stateList.currentIndex() >= 0:
            sql_str = "SELECT DISTINCT city FROM business WHERE state = %s ORDER BY city;"
            try:
                results = self.executeQuery(sql_str, (state,))
                for row in results:
                    self.ui.cityList.addItem(row[0])
            except Exception as e:
                print("Query failed!", e)

        self.clearBusinessTable()

        sql_str = "SELECT name, city, state FROM business WHERE state = %s ORDER BY name;"
        try:
            results = self.executeQuery(sql_str, (state,))
            self.populateBusinessTable(results)
        except Exception as e:
            print("Query failed!", e)

    def cityChanged(self):
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

    def refreshBusinessTable(self):
        if self.ui.stateList.currentIndex() >= 0 and len(self.ui.cityList.selectedItems()) > 0:
            state = self.ui.stateList.currentText()
            city = self.ui.cityList.selectedItems()[0].text()
            zipcode = self.ui.zipcodeList.currentText()

            sql_str = """
                SELECT name, city, state
                FROM business
                WHERE state = %s AND city = %s
            """
            params = [state, city]

            if zipcode != "" and zipcode != "All Zipcodes":
                sql_str += " AND postal_code = %s"
                params.append(zipcode)

            sql_str += " ORDER BY name;"

            try:
                results = self.executeQuery(sql_str, tuple(params))
                self.populateBusinessTable(results)
            except Exception as e:
                print("Query failed!", e)

    def zipcodeChanged(self):
        self.refreshBusinessTable()

    def getBusinessNames(self):
        self.ui.businesses.clear()
        businessName = self.ui.bname.text()

        sql_str = "SELECT name FROM business WHERE name ILIKE %s ORDER BY name;"
        params = ('%' + businessName + '%',)

        try:
            results = self.executeQuery(sql_str, params)
            for row in results:
                self.ui.businesses.addItem(row[0])
        except Exception as e:
            print("Query failed!", e)

    def displayBusinessCity(self):
        if len(self.ui.businesses.selectedItems()) == 0:
            self.ui.bcity.clear()
            return

        businessName = self.ui.businesses.selectedItems()[0].text()

        sql_str = "SELECT city FROM business WHERE name = %s;"
        params = (businessName,)

        try:
            results = self.executeQuery(sql_str, params)
            if results:
                self.ui.bcity.setText(results[0][0])
            else:
                self.ui.bcity.clear()
        except Exception as e:
            self.ui.bcity.clear()
            print("Query failed!", e)

    # ---------------- TABLE HELPERS ---------------- #

    def clearBusinessTable(self):
        for i in reversed(range(self.ui.businessTable.rowCount())):
            self.ui.businessTable.removeRow(i)

    def populateBusinessTable(self, results):
        style = "::section { background-color: #f3f3f3; }"
        self.ui.businessTable.horizontalHeader().setStyleSheet(style)

        if results:
            self.ui.businessTable.setColumnCount(len(results[0]))
            self.ui.businessTable.setRowCount(len(results))
            self.ui.businessTable.setHorizontalHeaderLabels(['Business Name', 'City', 'State'])
            self.ui.businessTable.resizeColumnsToContents()
            self.ui.businessTable.setColumnWidth(0, 300)
            self.ui.businessTable.setColumnWidth(1, 100)
            self.ui.businessTable.setColumnWidth(2, 50)

            for i, row in enumerate(results):
                for j, val in enumerate(row):
                    self.ui.businessTable.setItem(i, j, QTableWidgetItem(str(val)))
        else:
            self.ui.businessTable.setRowCount(0)
            self.ui.businessTable.setColumnCount(3)
            self.ui.businessTable.setHorizontalHeaderLabels(['Business Name', 'City', 'State'])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = milestone1()

    print("POPULAR TEST:")
    print(window.getPopularBusinesses("85281", "Restaurants")[:5])
    print("SUCCESSFUL TEST:")
    print(window.getSuccessfulBusinesses("85281", "Restaurants")[:5])

    window.show()
    sys.exit(app.exec())