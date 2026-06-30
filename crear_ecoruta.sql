PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- ============================
-- TABLA: COLONIA
-- ============================

CREATE TABLE IF NOT EXISTS colonia (

    id_colonia INTEGER PRIMARY KEY AUTOINCREMENT,

    nombre TEXT NOT NULL,

    codigo_postal TEXT,

    id_municipio INTEGER

);

-- ============================
-- TABLA: RUTA
-- ============================

CREATE TABLE IF NOT EXISTS ruta (

    id_ruta INTEGER PRIMARY KEY AUTOINCREMENT,

    nombre_ruta TEXT NOT NULL,

    descripcion TEXT,

    distancia_km REAL,

    id_colonia INTEGER NOT NULL,

    FOREIGN KEY (id_colonia)
        REFERENCES colonia(id_colonia)
        ON UPDATE CASCADE
        ON DELETE RESTRICT

);

-- ============================
-- TABLA: CAMION
-- ============================

CREATE TABLE IF NOT EXISTS camion (

    id_camion INTEGER PRIMARY KEY AUTOINCREMENT,

    placas TEXT NOT NULL UNIQUE,

    capacidad_kg REAL NOT NULL,

    estado TEXT NOT NULL DEFAULT 'Activo',

    CHECK (
        estado IN (
            'Activo',
            'En mantenimiento',
            'Fuera de servicio'
        )
    )

);

-- ============================
-- TABLA: RESPONSABLE
-- ============================

CREATE TABLE IF NOT EXISTS responsable (

    id_responsable INTEGER PRIMARY KEY AUTOINCREMENT,

    nombre TEXT NOT NULL,

    cargo TEXT,

    telefono TEXT,

    licencia TEXT

);

-- ============================
-- TABLA: ASIGNACION
-- ============================

CREATE TABLE IF NOT EXISTS asignacion (

    id_asignacion INTEGER PRIMARY KEY AUTOINCREMENT,

    fecha TEXT NOT NULL,

    id_responsable INTEGER NOT NULL,

    id_ruta INTEGER NOT NULL,

    id_camion INTEGER NOT NULL,

    FOREIGN KEY (id_responsable)
        REFERENCES responsable(id_responsable)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    FOREIGN KEY (id_ruta)
        REFERENCES ruta(id_ruta)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    FOREIGN KEY (id_camion)
        REFERENCES camion(id_camion)
        ON UPDATE CASCADE
        ON DELETE RESTRICT

);

-- ============================
-- TABLA: EVIDENCIA
-- ============================

CREATE TABLE IF NOT EXISTS evidencia (

    id_evidencia INTEGER PRIMARY KEY AUTOINCREMENT,

    fecha TEXT NOT NULL,

    tipo TEXT NOT NULL,

    descripcion TEXT,

    archivo TEXT,

    id_asignacion INTEGER NOT NULL,

    CHECK (
        tipo IN (
            'Foto',
            'Documento',
            'Registro'
        )
    ),

    FOREIGN KEY (id_asignacion)
        REFERENCES asignacion(id_asignacion)
        ON UPDATE CASCADE
        ON DELETE CASCADE

);

-- ============================
-- TABLA: OBSERVACION
-- ============================

CREATE TABLE IF NOT EXISTS observacion (

    id_observacion INTEGER PRIMARY KEY AUTOINCREMENT,

    comentario TEXT NOT NULL,

    fecha TEXT NOT NULL,

    id_asignacion INTEGER NOT NULL,

    FOREIGN KEY (id_asignacion)
        REFERENCES asignacion(id_asignacion)
        ON UPDATE CASCADE
        ON DELETE CASCADE

);

-- ============================
-- TABLA: REPORTE
-- ============================

CREATE TABLE IF NOT EXISTS reporte (

    id_reporte INTEGER PRIMARY KEY AUTOINCREMENT,

    fecha TEXT NOT NULL,

    descripcion TEXT NOT NULL,

    estado TEXT NOT NULL DEFAULT 'Pendiente',

    id_colonia INTEGER NOT NULL,

    CHECK (
        estado IN (
            'Pendiente',
            'En proceso',
            'Resuelto'
        )
    ),

    FOREIGN KEY (id_colonia)
        REFERENCES colonia(id_colonia)
        ON UPDATE CASCADE
        ON DELETE RESTRICT

);

-- ============================
-- TABLA: USUARIO
-- ============================

CREATE TABLE IF NOT EXISTS usuario (

    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,

    usuario TEXT NOT NULL UNIQUE,

    contrasena TEXT NOT NULL,

    rol TEXT NOT NULL

);

-- ============================
-- USUARIOS DEL SISTEMA
-- ============================

INSERT INTO usuario (
    usuario,
    contrasena,
    rol
)

VALUES (
    'admin',
    '1234',
    'administrador'
);

INSERT INTO usuario (
    usuario,
    contrasena,
    rol
)

VALUES (
    'chofer',
    '1234',
    'encargado'
);

-- ============================
-- ÍNDICES
-- ============================

CREATE INDEX IF NOT EXISTS idx_ruta_colonia
ON ruta(id_colonia);

CREATE INDEX IF NOT EXISTS idx_asignacion_responsable
ON asignacion(id_responsable);

CREATE INDEX IF NOT EXISTS idx_asignacion_ruta
ON asignacion(id_ruta);

CREATE INDEX IF NOT EXISTS idx_asignacion_camion
ON asignacion(id_camion);

CREATE INDEX IF NOT EXISTS idx_evidencia_asignacion
ON evidencia(id_asignacion);

CREATE INDEX IF NOT EXISTS idx_observacion_asignacion
ON observacion(id_asignacion);

CREATE INDEX IF NOT EXISTS idx_reporte_colonia
ON reporte(id_colonia);

COMMIT;