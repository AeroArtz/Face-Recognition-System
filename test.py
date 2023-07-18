# importing required libraries
import mysql.connector

dataBase = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="admin",
    database="damac"
)

# preparing a cursor object
cursorObject = dataBase.cursor()


sql = "INSERT INTO users (name, cluster, villa_no)\
VALUES (%s, %s, %s)"
val = ("Abdul Rehman", "coruseta", "100")

cursorObject.execute(sql, val)
dataBase.commit()

# disconnecting from server
dataBase.close()