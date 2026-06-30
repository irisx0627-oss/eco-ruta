import sqlite3

conexion = sqlite3.connect("eco_ruta.db")
cursor = conexion.cursor()

# Agregar columna estado a asignacion
try:
    cursor.execute("""
        ALTER TABLE asignacion 
        ADD COLUMN estado TEXT DEFAULT 'Pendiente'
    """)
    print("✅ Columna 'estado' agregada")
except:
    print("⚠️ La columna 'estado' ya existe")

# Agregar columna comentario_chofer a asignacion
try:
    cursor.execute("""
        ALTER TABLE asignacion 
        ADD COLUMN comentario_chofer TEXT DEFAULT ''
    """)
    print("✅ Columna 'comentario_chofer' agregada")
except:
    print("⚠️ La columna 'comentario_chofer' ya existe")

conexion.commit()
conexion.close()