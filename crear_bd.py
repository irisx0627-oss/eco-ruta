import sqlite3

conexion = sqlite3.connect("eco_ruta.db")

cursor = conexion.cursor()

with open("crear_ecoruta.sql", "r", encoding="utf-8") as archivo:

    sql = archivo.read()

cursor.executescript(sql)

conexion.commit()

conexion.close()

print("Base de datos creada correctamente")