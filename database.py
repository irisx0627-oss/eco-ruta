import mysql.connector

def conectar():
    conexion = mysql.connector.connect(
        host="localhost",
        user="jaz",
        password="iris",
        database="eco_ruta"
    )

    return conexion