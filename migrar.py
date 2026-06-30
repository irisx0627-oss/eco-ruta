import sqlite3

conexion = sqlite3.connect("eco_ruta.db")
cursor = conexion.cursor()

# ── 20 CHOFERES ──
choferes = [
    ("Juan García López",       "Chofer",  "7221001001", "B001"),
    ("Carlos Martínez Pérez",   "Chofer",  "7221001002", "B002"),
    ("Miguel Hernández Ruiz",   "Chofer",  "7221001003", "B003"),
    ("José Ramírez Torres",     "Chofer",  "7221001004", "B004"),
    ("Luis González Sánchez",   "Chofer",  "7221001005", "B005"),
    ("Roberto Flores Morales",  "Chofer",  "7221001006", "B006"),
    ("Antonio Reyes Castro",    "Chofer",  "7221001007", "B007"),
    ("Fernando Díaz Vargas",    "Chofer",  "7221001008", "B008"),
    ("Alejandro Cruz Jiménez",  "Chofer",  "7221001009", "B009"),
    ("David Ortiz Mendoza",     "Chofer",  "7221001010", "B010"),
    ("Mario Ramos Gutiérrez",   "Chofer",  "7221001011", "B011"),
    ("Ernesto Vega Salinas",    "Chofer",  "7221001012", "B012"),
    ("Pedro Mora Aguilar",      "Chofer",  "7221001013", "B013"),
    ("Héctor Ríos Delgado",     "Chofer",  "7221001014", "B014"),
    ("Ramón Silva Cervantes",   "Chofer",  "7221001015", "B015"),
    ("Arturo Mejía Herrera",    "Chofer",  "7221001016", "B016"),
    ("Gerardo Luna Espinoza",   "Chofer",  "7221001017", "B017"),
    ("Salvador Peña Romero",    "Chofer",  "7221001018", "B018"),
    ("Benjamín Soto Fuentes",   "Chofer",  "7221001019", "B019"),
    ("Ignacio Medina Campos",   "Chofer",  "7221001020", "B020"),
]

for nombre, cargo, telefono, licencia in choferes:
    cursor.execute("""
        INSERT INTO responsable (nombre, cargo, telefono, licencia)
        VALUES (?, ?, ?, ?)
    """, (nombre, cargo, telefono, licencia))

print("✅ 20 choferes insertados")

# ── 20 CAMIONES ──
camiones = [
    ("ABC-001", 5000, "Activo"),
    ("ABC-002", 4500, "Activo"),
    ("ABC-003", 6000, "Activo"),
    ("ABC-004", 5500, "Activo"),
    ("ABC-005", 4000, "Activo"),
    ("ABC-006", 7000, "Activo"),
    ("ABC-007", 5000, "Activo"),
    ("ABC-008", 4500, "Activo"),
    ("ABC-009", 6500, "Activo"),
    ("ABC-010", 5000, "Activo"),
    ("XYZ-011", 4000, "En mantenimiento"),
    ("XYZ-012", 5500, "Activo"),
    ("XYZ-013", 6000, "Activo"),
    ("XYZ-014", 4500, "Activo"),
    ("XYZ-015", 5000, "Activo"),
    ("XYZ-016", 7000, "Fuera de servicio"),
    ("XYZ-017", 4000, "Activo"),
    ("XYZ-018", 5500, "Activo"),
    ("XYZ-019", 6000, "Activo"),
    ("XYZ-020", 4500, "Activo"),
]

for placas, capacidad_kg, estado in camiones:
    cursor.execute("""
        INSERT INTO camion (placas, capacidad_kg, estado)
        VALUES (?, ?, ?)
    """, (placas, capacidad_kg, estado))

print("✅ 20 camiones insertados")

conexion.commit()
conexion.close()
print("✅ Todo listo")