from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from datetime import datetime
import os
app = Flask(__name__)
app.secret_key = "eco_ruta_secret"
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "eco_ruta.db")

# =====================================
# CONEXIÓN A LA BASE DE DATOS
# =====================================

def conectar():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion
# =====================================
# INDEX
# =====================================

@app.route('/index')
def index():

    if 'usuario' not in session:
        return redirect('/')

    conexion = sqlite3.connect('eco_ruta.db')
    conexion.row_factory = sqlite3.Row

    cursor = conexion.cursor()

    # CONTADORES
    cursor.execute("SELECT COUNT(*) FROM colonia")
    colonias_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ruta")
    rutas_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM camion")
    camiones_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM asignacion")
    asignaciones_count = cursor.fetchone()[0]

    # CONSULTA REAL DEL CONTROL CHOFER
    cursor.execute("""

        SELECT

            a.id_asignacion,
            a.fecha,

            r.nombre_ruta AS ruta,

            resp.nombre AS chofer,

            COALESCE(cc.estado, 'Pendiente') AS estado

        FROM asignacion a

        INNER JOIN ruta r
        ON a.id_ruta = r.id_ruta

        INNER JOIN responsable resp
        ON a.id_responsable = resp.id_responsable

        LEFT JOIN control_chofer cc
        ON a.id_asignacion = cc.id_asignacion

        ORDER BY a.id_asignacion DESC

    """)

    recolecciones = cursor.fetchall()

    conexion.close()

    return render_template(

        'index.html',

        rol=session['rol'],

        colonias_count=colonias_count,
        rutas_count=rutas_count,
        camiones_count=camiones_count,
        asignaciones_count=asignaciones_count,

        recolecciones=recolecciones

    )
# =====================================
# LOGIN
# =====================================

@app.route('/')
def login():
    return render_template('login.html')


@app.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():

    if request.method == 'GET':
        return redirect('/')

    usuario = request.form.get('usuario', '')
    contrasena = request.form.get('contrasena', '')

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT * FROM usuario
            WHERE usuario = ?
            AND contrasena = ?
        """, (usuario, contrasena))

        usuario_encontrado = cursor.fetchone()
        conexion.close()
    except sqlite3.OperationalError as e:
        app.logger.error(f"Error de base de datos en login: {e}")
        return render_template('login.html', error='Error de base de datos. Contacta al administrador.')

    if usuario_encontrado:
        session['usuario']    = usuario_encontrado['usuario']
        session['rol']        = usuario_encontrado['rol']
        session['nombre']     = usuario_encontrado['nombre']
        session['id_usuario'] = usuario_encontrado['id_usuario']

        if usuario_encontrado['rol'] == 'administrador':
            return redirect('/index')
        elif usuario_encontrado['rol'] == 'ciudadano':
            return redirect('/ciudadano')
        else:
            return redirect('/panel_chofer')

    return render_template('login.html', error='Usuario o contraseña incorrectos')

    


# =====================================
# CERRAR SESION
# =====================================

@app.route('/cerrar_sesion')
def cerrar_sesion():

    session.clear()

    return redirect('/')



# =====================================
# MOSTRAR COLONIAS
# =====================================

@app.route('/colonias')
def colonias():

    if session.get('rol') != 'administrador':
        return "No tienes permiso"

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT * FROM colonia
    """)

    colonias = cursor.fetchall()

    conexion.close()

    return render_template(
        'colonias.html',
        colonias=colonias
    )

# =====================================
# AGREGAR COLONIA
# =====================================

@app.route('/agregar_colonia', methods=['POST'])
def agregar_colonia():

    nombre        = request.form['nombre']
    codigo_postal = request.form['codigo_postal']

    conexion = conectar()
    cursor   = conexion.cursor()

    cursor.execute("""
        INSERT INTO colonia (nombre, codigo_postal, estado)
        VALUES (?, ?, 'Disponible')
    """, (nombre, codigo_postal))

    conexion.commit()
    conexion.close()

    return redirect('/colonias')


# =====================================
# ELIMINAR COLONIA
# =====================================

@app.route('/eliminar_colonia/<int:id>')
def eliminar_colonia(id):

    conexion = conectar()
    cursor   = conexion.cursor()

    cursor.execute("DELETE FROM colonia WHERE id_colonia = ?", (id,))

    conexion.commit()
    conexion.close()

    return redirect('/colonias')


# =====================================
# EDITAR COLONIA
# =====================================

@app.route('/editar_colonia/<int:id>')
def editar_colonia(id):

    conexion = conectar()
    cursor   = conexion.cursor()

    cursor.execute("SELECT * FROM colonia WHERE id_colonia = ?", (id,))
    colonia = cursor.fetchone()

    conexion.close()

    return render_template('editar_colonia.html', colonia=colonia)


# =====================================
# ACTUALIZAR COLONIA
# =====================================

@app.route('/actualizar_colonia/<int:id>', methods=['POST'])
def actualizar_colonia(id):

    nombre        = request.form['nombre']
    codigo_postal = request.form['codigo_postal']

    conexion = conectar()
    cursor   = conexion.cursor()

    cursor.execute("""
        UPDATE colonia
        SET nombre = ?, codigo_postal = ?
        WHERE id_colonia = ?
    """, (nombre, codigo_postal, id))

    conexion.commit()
    conexion.close()

    return redirect('/colonias')

# =====================================
# MOSTRAR RUTAS
# =====================================

# =====================================
# MOSTRAR RUTAS
# =====================================

@app.route('/rutas')
def rutas():
    if session.get('rol') != 'administrador':
        return "No tienes permiso"

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM ruta")
    rutas_raw = cursor.fetchall()

    rutas = []
    for ruta in rutas_raw:
        cursor.execute("""
            SELECT colonia.nombre
            FROM ruta_colonia
            INNER JOIN colonia ON ruta_colonia.id_colonia = colonia.id_colonia
            WHERE ruta_colonia.id_ruta = ?
        """, (ruta['id_ruta'],))
        colonias_ruta = [row['nombre'] for row in cursor.fetchall()]
        ruta_dict = dict(ruta)
        ruta_dict['colonias'] = colonias_ruta
        rutas.append(ruta_dict)

    cursor.execute("SELECT id_colonia, nombre, estado FROM colonia ORDER BY nombre")
    colonias = cursor.fetchall()

    conexion.close()

    return render_template('rutas.html', rutas=rutas, colonias=colonias)


# =====================================
# AGREGAR RUTA
# =====================================

@app.route('/agregar_ruta', methods=['POST'])
def agregar_ruta():

    nombre_ruta  = request.form['nombre_ruta']
    descripcion  = request.form['descripcion']
    distancia_km = request.form['distancia_km']
    ids_colonia  = request.form.getlist('ids_colonia')

    if not ids_colonia:
        return redirect('/rutas')

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO ruta (nombre_ruta, descripcion, distancia_km)
        VALUES (?, ?, ?)
    """, (nombre_ruta, descripcion, distancia_km))

    id_nueva_ruta = cursor.lastrowid

    for id_colonia in ids_colonia:
        cursor.execute("""
            INSERT OR IGNORE INTO ruta_colonia (id_ruta, id_colonia)
            VALUES (?, ?)
        """, (id_nueva_ruta, id_colonia))
        cursor.execute("""
            UPDATE colonia SET estado = 'Ocupada' WHERE id_colonia = ?
        """, (id_colonia,))

    conexion.commit()
    conexion.close()

    return redirect('/rutas')


# =====================================
# ELIMINAR RUTA
# =====================================

@app.route('/eliminar_ruta/<int:id>')
def eliminar_ruta(id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SELECT id_colonia FROM ruta_colonia WHERE id_ruta = ?", (id,))
    colonias_de_ruta = [row['id_colonia'] for row in cursor.fetchall()]

    for id_colonia in colonias_de_ruta:
        cursor.execute("""
            SELECT COUNT(*) as total FROM ruta_colonia
            WHERE id_colonia = ? AND id_ruta != ?
        """, (id_colonia, id))
        otras = cursor.fetchone()['total']
        if otras == 0:
            cursor.execute("""
                UPDATE colonia SET estado = 'Disponible' WHERE id_colonia = ?
            """, (id_colonia,))

    cursor.execute("DELETE FROM ruta_colonia WHERE id_ruta = ?", (id,))
    cursor.execute("DELETE FROM ruta WHERE id_ruta = ?", (id,))

    conexion.commit()
    conexion.close()

    return redirect('/rutas')


# =====================================
# EDITAR RUTA
# =====================================

@app.route('/editar_ruta/<int:id>')
def editar_ruta(id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM ruta WHERE id_ruta = ?", (id,))
    ruta = cursor.fetchone()

    cursor.execute("SELECT id_colonia FROM ruta_colonia WHERE id_ruta = ?", (id,))
    ids_asignadas = {row['id_colonia'] for row in cursor.fetchall()}

    cursor.execute("SELECT id_colonia, nombre, estado FROM colonia ORDER BY nombre")
    colonias = cursor.fetchall()

    conexion.close()

    return render_template(
        'editar_ruta.html',
        ruta=ruta,
        colonias=colonias,
        ids_asignadas=ids_asignadas
    )


# =====================================
# ACTUALIZAR RUTA
# =====================================

@app.route('/actualizar_ruta/<int:id>', methods=['POST'])
def actualizar_ruta(id):

    nombre_ruta  = request.form['nombre_ruta']
    descripcion  = request.form['descripcion']
    distancia_km = request.form['distancia_km']
    ids_nuevas   = request.form.getlist('ids_colonia')

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE ruta SET nombre_ruta = ?, descripcion = ?, distancia_km = ?
        WHERE id_ruta = ?
    """, (nombre_ruta, descripcion, distancia_km, id))

    cursor.execute("SELECT id_colonia FROM ruta_colonia WHERE id_ruta = ?", (id,))
    ids_anteriores = {row['id_colonia'] for row in cursor.fetchall()}
    ids_nuevas_set = {int(x) for x in ids_nuevas}

    for id_col in ids_anteriores - ids_nuevas_set:
        cursor.execute("""
            SELECT COUNT(*) as total FROM ruta_colonia
            WHERE id_colonia = ? AND id_ruta != ?
        """, (id_col, id))
        otras = cursor.fetchone()['total']
        if otras == 0:
            cursor.execute("""
                UPDATE colonia SET estado = 'Disponible' WHERE id_colonia = ?
            """, (id_col,))

    cursor.execute("DELETE FROM ruta_colonia WHERE id_ruta = ?", (id,))

    for id_col in ids_nuevas_set:
        cursor.execute("""
            INSERT OR IGNORE INTO ruta_colonia (id_ruta, id_colonia) VALUES (?, ?)
        """, (id, id_col))
        cursor.execute("""
            UPDATE colonia SET estado = 'Ocupada' WHERE id_colonia = ?
        """, (id_col,))

    conexion.commit()
    conexion.close()

    return redirect('/rutas')
# =====================================
# MOSTRAR CAMIONES
# =====================================

@app.route('/camiones')
def camiones():
        
    if session.get('rol') != 'administrador':
        return "No tienes permiso"

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT * FROM camion
    """)

    camiones = cursor.fetchall()

    conexion.close()

    return render_template(
        'camiones.html',
        camiones=camiones
    )

# =====================================
# AGREGAR CAMION
# =====================================

@app.route('/agregar_camion', methods=['POST'])
def agregar_camion():

    placas = request.form['placas']
    capacidad_kg = request.form['capacidad_kg']
    estado = request.form['estado']

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO camion
        (
            placas,
            capacidad_kg,
            estado
        )
        VALUES (?, ?, ?)
    """, (
        placas,
        capacidad_kg,
        estado
    ))

    conexion.commit()
    conexion.close()

    return redirect('/camiones')

# =====================================
# ELIMINAR CAMION
# =====================================

@app.route('/eliminar_camion/<int:id>')
def eliminar_camion(id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM camion
        WHERE id_camion = ?
    """, (id,))

    conexion.commit()
    conexion.close()

    return redirect('/camiones')

# =====================================
# EDITAR CAMION
# =====================================

@app.route('/editar_camion/<int:id>')
def editar_camion(id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT * FROM camion
        WHERE id_camion = ?
    """, (id,))

    camion = cursor.fetchone()

    conexion.close()

    return render_template(
        'editar_camion.html',
        camion=camion
    )

# =====================================
# ACTUALIZAR CAMION
# =====================================

@app.route('/actualizar_camion/<int:id>', methods=['POST'])
def actualizar_camion(id):

    placas = request.form['placas']
    capacidad_kg = request.form['capacidad_kg']
    estado = request.form['estado']

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE camion
        SET placas = ?,
            capacidad_kg = ?,
            estado = ?
        WHERE id_camion = ?
    """, (
        placas,
        capacidad_kg,
        estado,
        id
    ))

    conexion.commit()
    conexion.close()

    return redirect('/camiones')
# =====================================
# MOSTRAR RESPONSABLES
# =====================================

@app.route('/responsables')
def responsables():
    if session.get('rol') != 'administrador':
        return "No tienes permiso"

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT * FROM responsable
    """)

    responsables = cursor.fetchall()

    conexion.close()

    return render_template(
        'responsables.html',
        responsables=responsables
    )

# =====================================
# AGREGAR RESPONSABLE
# =====================================

@app.route('/agregar_responsable', methods=['POST'])
def agregar_responsable():

    nombre = request.form['nombre']
    cargo = request.form['cargo']
    telefono = request.form['telefono']
    licencia = request.form['licencia']

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO responsable
        (
            nombre,
            cargo,
            telefono,
            licencia
        )
        VALUES (?, ?, ?, ?)
    """, (
        nombre,
        cargo,
        telefono,
        licencia
    ))

    conexion.commit()
    conexion.close()

    return redirect('/responsables')

# =====================================
# ELIMINAR RESPONSABLE
# =====================================

@app.route('/eliminar_responsable/<int:id>')
def eliminar_responsable(id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM responsable
        WHERE id_responsable = ?
    """, (id,))

    conexion.commit()
    conexion.close()

    return redirect('/responsables')

# =====================================
# EDITAR RESPONSABLE
# =====================================

@app.route('/editar_responsable/<int:id>')
def editar_responsable(id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT * FROM responsable
        WHERE id_responsable = ?
    """, (id,))

    responsable = cursor.fetchone()

    conexion.close()

    return render_template(
        'editar_responsable.html',
        responsable=responsable
    )

# =====================================
# ACTUALIZAR RESPONSABLE
# =====================================

@app.route('/actualizar_responsable/<int:id>', methods=['POST'])
def actualizar_responsable(id):

    nombre = request.form['nombre']
    cargo = request.form['cargo']
    telefono = request.form['telefono']
    licencia = request.form['licencia']

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE responsable
        SET nombre = ?,
            cargo = ?,
            telefono = ?,
            licencia = ?
        WHERE id_responsable = ?
    """, (
        nombre,
        cargo,
        telefono,
        licencia,
        id
    ))

    conexion.commit()
    conexion.close()

    return redirect('/responsables')
# =====================================
# PANEL ENCARGADO
# =====================================

@app.route('/panel_chofer')
def panel_chofer():

    if 'usuario' not in session:
        return redirect('/')

    conexion = sqlite3.connect('eco_ruta.db')
    conexion.row_factory = sqlite3.Row

    cursor = conexion.cursor()

    # TRAER ASIGNACIONES + CONTROL DEL CHOFER
    cursor.execute("""

        SELECT
            a.id_asignacion,
            a.fecha,

            r.nombre_ruta,
            c.placas,
            resp.nombre,

            COALESCE(cc.estado, 'Pendiente') AS estado,
            COALESCE(cc.observacion, '') AS observacion,
            cc.evidencia

        FROM asignacion a

        INNER JOIN ruta r
        ON a.id_ruta = r.id_ruta

        INNER JOIN camion c
        ON a.id_camion = c.id_camion

        INNER JOIN responsable resp
        ON a.id_responsable = resp.id_responsable

        LEFT JOIN control_chofer cc
        ON a.id_asignacion = cc.id_asignacion

        ORDER BY a.id_asignacion DESC

    """)

    asignaciones = cursor.fetchall()

    conexion.close()

    return render_template(
        'panel_chofer.html',
        asignaciones=asignaciones
    )
# =====================================
# ACTUALIZAR ESTADO CHOFER
# =====================================

@app.route('/actualizar_estado/<int:id>', methods=['POST'])
def actualizar_estado(id):

    estado = request.form['estado']
    comentario = request.form['comentario']

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE asignacion
        SET estado = ?,
            comentario_chofer = ?
        WHERE id_asignacion = ?
    """, (
        estado,
        comentario,
        id
    ))

    conexion.commit()
    conexion.close()

    return redirect('/panel_chofer')
@app.route("/control_chofer")
def control_chofer():

    conexion = sqlite3.connect("eco_ruta.db")
    conexion.row_factory = sqlite3.Row

    cursor = conexion.cursor()

    # TABLA CONTROL

    cursor.execute("""
    SELECT
        c.*,
        r.nombre_ruta,
        ca.placas

    FROM control_chofer c

    INNER JOIN asignacion a
        ON c.id_asignacion = a.id_asignacion

    INNER JOIN ruta r
        ON a.id_ruta = r.id_ruta

    INNER JOIN camion ca
        ON a.id_camion = ca.id_camion
    """)

    controles = cursor.fetchall()

    # ASIGNACIONES

    cursor.execute("""
    SELECT
        a.id_asignacion,
        r.nombre_ruta,
        ca.placas

    FROM asignacion a

    INNER JOIN ruta r
        ON a.id_ruta = r.id_ruta

    INNER JOIN camion ca
        ON a.id_camion = ca.id_camion
    """)

    asignaciones = cursor.fetchall()

    conexion.close()

    return render_template(
        "control_chofer.html",
        controles=controles,
        asignaciones=asignaciones
    )
# =========================
# GUARDAR CONTROL CHOFER
# =========================

@app.route('/guardar_control_chofer', methods=['POST'])
def guardar_control_chofer():

    if 'usuario' not in session:
        return redirect('/')

    fecha = request.form['fecha']
    estado = request.form['estado']
    observacion = request.form['observacion']
    id_asignacion = request.form['id_asignacion']

    evidencia = ""

    # SUBIR ARCHIVO
    if 'evidencia' in request.files:

        archivo = request.files['evidencia']

        if archivo.filename != "":

            evidencia = archivo.filename

            ruta_guardado = os.path.join(
                'static/uploads',
                archivo.filename
            )

            archivo.save(ruta_guardado)

    conexion = sqlite3.connect('eco_ruta.db')
    cursor = conexion.cursor()

    # VERIFICAR SI YA EXISTE CONTROL
    cursor.execute("""

        SELECT id_control
        FROM control_chofer
        WHERE id_asignacion = ?

    """, (id_asignacion,))

    control_existente = cursor.fetchone()

    # SI YA EXISTE → ACTUALIZA
    if control_existente:

        cursor.execute("""

            UPDATE control_chofer

            SET
                estado = ?,
                observacion = ?,
                evidencia = ?,
                fecha = ?

            WHERE id_asignacion = ?

        """, (

            estado,
            observacion,
            evidencia,
            fecha,
            id_asignacion

        ))

    # SI NO EXISTE → INSERTA
    else:

        cursor.execute("""

            INSERT INTO control_chofer
            (
                id_asignacion,
                estado,
                observacion,
                evidencia,
                fecha
            )

            VALUES (?, ?, ?, ?, ?)

        """, (

            id_asignacion,
            estado,
            observacion,
            evidencia,
            fecha

        ))

    conexion.commit()
    conexion.close()

    return redirect('/control_chofer')
# =========================
# PANEL CONTROL ADMIN
# =========================

@app.route('/control_admin')
def control_admin():

    if 'usuario' not in session:
        return redirect('/')

    conexion = sqlite3.connect('eco_ruta.db')

    conexion.row_factory = sqlite3.Row

    cursor = conexion.cursor()

    cursor.execute("""

        SELECT
            control_chofer.*,
            ruta.nombre_ruta,
            camion.placas

        FROM control_chofer

        INNER JOIN asignacion
            ON control_chofer.id_asignacion =
            asignacion.id_asignacion

        INNER JOIN ruta
            ON asignacion.id_ruta =
            ruta.id_ruta

        INNER JOIN camion
            ON asignacion.id_camion =
            camion.id_camion

        ORDER BY control_chofer.id_control DESC

    """)

    controles = cursor.fetchall()

    conexion.close()

    return render_template(
        'control_admin.html',
        controles=controles
    )                
# =====================================
# MOSTRAR ASIGNACIONES
# =====================================

@app.route('/asignaciones')
def asignaciones():
    if session.get('rol') != 'administrador':
        return "No tienes permiso"

    conexion = conectar()
    cursor = conexion.cursor()

    # Lista de asignaciones
    cursor.execute("""
        SELECT asignacion.*,
               responsable.nombre AS nombre_responsable,
               ruta.nombre_ruta,
               camion.placas
        FROM asignacion
        INNER JOIN responsable ON asignacion.id_responsable = responsable.id_responsable
        INNER JOIN ruta        ON asignacion.id_ruta        = ruta.id_ruta
        INNER JOIN camion      ON asignacion.id_camion      = camion.id_camion
    """)
    asignaciones = cursor.fetchall()

    # IDs que ya están asignados
    cursor.execute("SELECT id_responsable, id_ruta, id_camion FROM asignacion")
    ya_asignados = cursor.fetchall()
    ids_resp   = {r['id_responsable'] for r in ya_asignados}
    ids_ruta   = {r['id_ruta']        for r in ya_asignados}
    ids_camion = {r['id_camion']      for r in ya_asignados}

    # Responsables con flag ocupado
    cursor.execute("SELECT * FROM responsable")
    responsables = []
    for r in cursor.fetchall():
        d = dict(r)
        d['ocupado'] = r['id_responsable'] in ids_resp
        responsables.append(d)

    # Rutas con flag ocupado
    cursor.execute("SELECT * FROM ruta")
    rutas = []
    for r in cursor.fetchall():
        d = dict(r)
        d['ocupado'] = r['id_ruta'] in ids_ruta
        rutas.append(d)

    # Camiones (el estado ya indica disponibilidad)
    cursor.execute("SELECT * FROM camion")
    camiones = cursor.fetchall()

    conexion.close()

    return render_template(
        'asignaciones.html',
        asignaciones=asignaciones,
        responsables=responsables,
        rutas=rutas,
        camiones=camiones
    )


# =====================================
# AGREGAR ASIGNACION
# =====================================

@app.route('/agregar_asignacion', methods=['POST'])
def agregar_asignacion():

    fecha          = request.form['fecha']
    id_responsable = request.form['id_responsable']
    id_ruta        = request.form['id_ruta']
    id_camion      = request.form['id_camion']

    conexion = conectar()
    cursor   = conexion.cursor()

    cursor.execute("""
        INSERT INTO asignacion (fecha, id_responsable, id_ruta, id_camion)
        VALUES (?, ?, ?, ?)
    """, (fecha, id_responsable, id_ruta, id_camion))

    conexion.commit()
    conexion.close()

    # ?guardado=1 dispara el toast verde en el HTML
    return redirect('/asignaciones?guardado=1')


# =====================================
# ELIMINAR ASIGNACION
# =====================================

@app.route('/eliminar_asignacion/<int:id>')
def eliminar_asignacion(id):

    conexion = conectar()
    cursor   = conexion.cursor()

    cursor.execute("DELETE FROM asignacion WHERE id_asignacion = ?", (id,))

    conexion.commit()
    conexion.close()

    return redirect('/asignaciones?guardado=1')


# =====================================
# EDITAR ASIGNACION
# =====================================

@app.route('/editar_asignacion/<int:id>')
def editar_asignacion(id):

    conexion = conectar()
    cursor   = conexion.cursor()

    cursor.execute("SELECT * FROM asignacion WHERE id_asignacion = ?", (id,))
    asignacion = cursor.fetchone()

    # Responsables con flag ocupado (excepto el actual)
    cursor.execute("SELECT id_responsable FROM asignacion WHERE id_asignacion != ?", (id,))
    ids_resp = {r['id_responsable'] for r in cursor.fetchall()}
    cursor.execute("SELECT * FROM responsable")
    responsables = []
    for r in cursor.fetchall():
        d = dict(r)
        d['ocupado'] = r['id_responsable'] in ids_resp
        responsables.append(d)

    # Rutas con flag ocupado (excepto la actual)
    cursor.execute("SELECT id_ruta FROM asignacion WHERE id_asignacion != ?", (id,))
    ids_ruta = {r['id_ruta'] for r in cursor.fetchall()}
    cursor.execute("SELECT * FROM ruta")
    rutas = []
    for r in cursor.fetchall():
        d = dict(r)
        d['ocupado'] = r['id_ruta'] in ids_ruta
        rutas.append(d)

    # Camiones
    cursor.execute("SELECT * FROM camion")
    camiones = cursor.fetchall()

    conexion.close()

    return render_template(
        'editar_asignacion.html',
        asignacion=asignacion,
        responsables=responsables,
        rutas=rutas,
        camiones=camiones
    )


# =====================================
# ACTUALIZAR ASIGNACION
# =====================================

@app.route('/actualizar_asignacion/<int:id>', methods=['POST'])
def actualizar_asignacion(id):

    fecha          = request.form['fecha']
    id_responsable = request.form['id_responsable']
    id_ruta        = request.form['id_ruta']
    id_camion      = request.form['id_camion']

    conexion = conectar()
    cursor   = conexion.cursor()

    cursor.execute("""
        UPDATE asignacion
        SET fecha = ?, id_responsable = ?, id_ruta = ?, id_camion = ?
        WHERE id_asignacion = ?
    """, (fecha, id_responsable, id_ruta, id_camion, id))

    conexion.commit()
    conexion.close()

    return redirect('/asignaciones?guardado=1')
# =====================================
# CRUD EVIDENCIAS
# =====================================

@app.route('/evidencias')
def evidencias():

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT evidencia.*,
               asignacion.fecha AS fecha_asignacion
        FROM evidencia

        INNER JOIN asignacion
        ON evidencia.id_asignacion = asignacion.id_asignacion
    """)

    evidencias = cursor.fetchall()

    cursor.execute("""
        SELECT * FROM asignacion
    """)

    asignaciones = cursor.fetchall()

    conexion.close()

    return render_template(
        'evidencias.html',
        evidencias=evidencias,
        asignaciones=asignaciones
    )

# =====================================
# AGREGAR EVIDENCIA
# =====================================

@app.route('/agregar_evidencia', methods=['POST'])
def agregar_evidencia():

    fecha = request.form['fecha']
    tipo = request.form['tipo']
    descripcion = request.form['descripcion']
    id_asignacion = request.form['id_asignacion']

    archivo = request.files['archivo']

    nombre_archivo = ""

    if archivo:

        nombre_archivo = secure_filename(archivo.filename)

        ruta_archivo = os.path.join(
            app.config['UPLOAD_FOLDER'],
            nombre_archivo
        )

        archivo.save(ruta_archivo)

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO evidencia
        (
            fecha,
            tipo,
            descripcion,
            archivo,
            id_asignacion
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        fecha,
        tipo,
        descripcion,
        nombre_archivo,
        id_asignacion
    ))

    conexion.commit()
    conexion.close()

    return redirect('/evidencias')
# =====================================
# CRUD OBSERVACIONES
# =====================================

@app.route('/observaciones')
def observaciones():

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT observacion.*,
               asignacion.fecha AS fecha_asignacion
        FROM observacion

        INNER JOIN asignacion
        ON observacion.id_asignacion = asignacion.id_asignacion
    """)

    observaciones = cursor.fetchall()

    cursor.execute("""
        SELECT * FROM asignacion
    """)

    asignaciones = cursor.fetchall()

    conexion.close()

    return render_template(
        'observaciones.html',
        observaciones=observaciones,
        asignaciones=asignaciones
    )

# =====================================
# AGREGAR OBSERVACION
# =====================================

@app.route('/agregar_observacion', methods=['POST'])
def agregar_observacion():

    comentario = request.form['comentario']
    fecha = request.form['fecha']
    id_asignacion = request.form['id_asignacion']

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO observacion
        (
            comentario,
            fecha,
            id_asignacion
        )
        VALUES (?, ?, ?)
    """, (
        comentario,
        fecha,
        id_asignacion
    ))

    conexion.commit()
    conexion.close()

    return redirect('/observaciones')

# =====================================
# ELIMINAR OBSERVACION
# =====================================

@app.route('/eliminar_observacion/<int:id>')
def eliminar_observacion(id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM observacion
        WHERE id_observacion = ?
    """, (id,))

    conexion.commit()
    conexion.close()

    return redirect('/observaciones')

# =====================================
# EDITAR OBSERVACION
# =====================================

@app.route('/editar_observacion/<int:id>')
def editar_observacion(id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT * FROM observacion
        WHERE id_observacion = ?
    """, (id,))

    observacion = cursor.fetchone()

    cursor.execute("""
        SELECT * FROM asignacion
    """)

    asignaciones = cursor.fetchall()

    conexion.close()

    return render_template(
        'editar_observacion.html',
        observacion=observacion,
        asignaciones=asignaciones
    )

# =====================================
# ACTUALIZAR OBSERVACION
# =====================================

@app.route('/actualizar_observacion/<int:id>', methods=['POST'])
def actualizar_observacion(id):

    comentario = request.form['comentario']
    fecha = request.form['fecha']
    id_asignacion = request.form['id_asignacion']

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE observacion
        SET comentario = ?,
            fecha = ?,
            id_asignacion = ?
        WHERE id_observacion = ?
    """, (
        comentario,
        fecha,
        id_asignacion,
        id
    ))

    conexion.commit()
    conexion.close()

    return redirect('/observaciones')
# =====================================
# CRUD REPORTES
# =====================================

@app.route('/reportes')
def reportes():

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT reporte.*,
               colonia.nombre AS nombre_colonia
        FROM reporte

        INNER JOIN colonia
        ON reporte.id_colonia = colonia.id_colonia
    """)

    reportes = cursor.fetchall()

    cursor.execute("""
        SELECT * FROM colonia
    """)

    colonias = cursor.fetchall()

    conexion.close()

    return render_template(
        'reportes.html',
        reportes=reportes,
        colonias=colonias
    )

# =====================================
# AGREGAR REPORTE
# =====================================

@app.route('/agregar_reporte', methods=['POST'])
def agregar_reporte():

    fecha = request.form['fecha']
    descripcion = request.form['descripcion']
    estado = request.form['estado']
    id_colonia = request.form['id_colonia']

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO reporte
        (
            fecha,
            descripcion,
            estado,
            id_colonia
        )
        VALUES (?, ?, ?, ?)
    """, (
        fecha,
        descripcion,
        estado,
        id_colonia
    ))

    conexion.commit()
    conexion.close()

    return redirect('/reportes')

# =====================================
# ELIMINAR REPORTE
# =====================================

@app.route('/eliminar_reporte/<int:id>')
def eliminar_reporte(id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM reporte
        WHERE id_reporte = ?
    """, (id,))

    conexion.commit()
    conexion.close()

    return redirect('/reportes')

# =====================================
# EDITAR REPORTE
# =====================================

@app.route('/editar_reporte/<int:id>')
def editar_reporte(id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT * FROM reporte
        WHERE id_reporte = ?
    """, (id,))

    reporte = cursor.fetchone()

    cursor.execute("""
        SELECT * FROM colonia
    """)

    colonias = cursor.fetchall()

    conexion.close()

    return render_template(
        'editar_reporte.html',
        reporte=reporte,
        colonias=colonias
    )

# =====================================
# ACTUALIZAR REPORTE
# =====================================

@app.route('/actualizar_reporte/<int:id>', methods=['POST'])
def actualizar_reporte(id):

    fecha = request.form['fecha']
    descripcion = request.form['descripcion']
    estado = request.form['estado']
    id_colonia = request.form['id_colonia']

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE reporte
        SET fecha = ?,
            descripcion = ?,
            estado = ?,
            id_colonia = ?
        WHERE id_reporte = ?
    """, (
        fecha,
        descripcion,
        estado,
        id_colonia,
        id
    ))

    conexion.commit()
    conexion.close()

    return redirect('/reportes')
# =====================================
# REGISTRO CIUDADANO
# =====================================

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre     = request.form['nombre']
        usuario    = request.form['usuario']
        contrasena = request.form['contrasena']

        conexion = conectar()
        cursor = conexion.cursor()

        # Verificar si ya existe
        cursor.execute("SELECT * FROM usuario WHERE usuario=?", (usuario,))
        existe = cursor.fetchone()

        if existe:
            conexion.close()
            return render_template('registro.html', error='Ese usuario ya existe')

        cursor.execute("""
            INSERT INTO usuario (nombre, usuario, contrasena, rol)
            VALUES (?, ?, ?, 'ciudadano')
        """, (nombre, usuario, contrasena))

        conexion.commit()
        conexion.close()
        return redirect('/')

    return render_template('registro.html')


# =====================================
# PANEL CIUDADANO
# =====================================

@app.route('/ciudadano')
def panel_ciudadano():
    if session.get('rol') != 'ciudadano':
        return redirect('/')

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT * FROM reporte_ciudadano
        WHERE id_usuario = ?
        ORDER BY fecha DESC
    """, (session['id_usuario'],))

    mis_reportes = cursor.fetchall()
    conexion.close()

    return render_template('panel_ciudadano.html', reportes=mis_reportes)


EXTENSIONES_PERMITIDAS = {
    'jpg', 'jpeg', 'png', 'gif', 'webp',
    'mp4', 'mov', 'avi', 'mkv', 'webm'
}

def extension_permitida(nombre):
    return '.' in nombre and \
           nombre.rsplit('.', 1)[1].lower() in EXTENSIONES_PERMITIDAS

@app.route('/ciudadano/nuevo_reporte', methods=['GET', 'POST'])
def nuevo_reporte_ciudadano():
    if session.get('rol') != 'ciudadano':
        return redirect('/')

    # Cargar colonias desde la BD
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_colonia, nombre FROM colonia ORDER BY nombre")
    colonias = cursor.fetchall()  # lista de tuplas (id, nombre)
    conexion.close()

    if request.method == 'POST':
        id_colonia  = request.form['colonia']
        direccion   = request.form['direccion']
        tipo        = request.form['tipo']
        descripcion = request.form['descripcion']
        fecha       = datetime.now().strftime('%Y-%m-%d %H:%M')

        archivos_guardados = []
        archivos = request.files.getlist('archivos')

        for archivo in archivos:
            if archivo and archivo.filename != '':
                if extension_permitida(archivo.filename):
                    nombre_seguro = secure_filename(archivo.filename)
                    archivo.save(os.path.join('static/uploads', nombre_seguro))
                    archivos_guardados.append(nombre_seguro)

        nombres_archivos = ','.join(archivos_guardados) if archivos_guardados else None

        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO reporte_ciudadano
            (id_usuario, nombre, id_colonia, direccion,
             tipo, descripcion, evidencia, estado, fecha)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Pendiente', ?)
        """, (
            session['id_usuario'],
            session['nombre'],
            id_colonia, direccion,
            tipo, descripcion,
            nombres_archivos,
            fecha
        ))
        conexion.commit()
        conexion.close()
        return redirect('/ciudadano')

    return render_template('nuevo_reporte.html', colonias=colonias)


# =====================================
# ADMIN VE REPORTES CIUDADANOS
# =====================================

@app.route('/admin/reportes_ciudadanos')
def admin_reportes_ciudadanos():
    if session.get('rol') != 'administrador':
        return redirect('/')

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT * FROM reporte_ciudadano
        ORDER BY fecha DESC
    """)

    reportes = cursor.fetchall()
    conexion.close()

    return render_template('admin_reportes_ciudadanos.html', reportes=reportes)


# =====================================
# CAMBIAR ESTADO REPORTE CIUDADANO
# =====================================

@app.route('/admin/cambiar_estado/<int:id>/<estado>')
def cambiar_estado_reporte(id, estado):
    if session.get('rol') != 'administrador':
        return redirect('/')

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE reporte_ciudadano
        SET estado = ?
        WHERE id_reporte = ?
    """, (estado, id))

    conexion.commit()
    conexion.close()
    return redirect('/admin/reportes_ciudadanos')
# =====================================
# HISTORIAL DE RUTAS Y EVIDENCIAS
# =====================================

@app.route('/historial')
def historial():

    if 'usuario' not in session:
        return redirect('/')

    conexion = conectar()
    cursor = conexion.cursor()

    fecha_inicio          = request.args.get('fecha_inicio', '')
    fecha_fin             = request.args.get('fecha_fin', '')
    id_ruta_filtro        = request.args.get('id_ruta', '')
    id_responsable_filtro = request.args.get('id_responsable', '')
    estado_filtro         = request.args.get('estado', '')

    query = """
        SELECT
            a.id_asignacion,
            a.fecha AS fecha_asignacion,
            r.id_ruta,
            r.nombre_ruta,
            r.distancia_km,
            cam.placas,
            resp.id_responsable,
            resp.nombre AS chofer,
            COALESCE(cc.estado, 'Pendiente') AS estado,
            COALESCE(cc.observacion, '') AS observacion_chofer,
            cc.evidencia AS evidencia_control,
            cc.fecha AS fecha_control
        FROM asignacion a
        INNER JOIN ruta r        ON a.id_ruta = r.id_ruta
        INNER JOIN camion cam    ON a.id_camion = cam.id_camion
        INNER JOIN responsable resp ON a.id_responsable = resp.id_responsable
        LEFT JOIN control_chofer cc ON a.id_asignacion = cc.id_asignacion
        WHERE 1=1
    """
    params = []

    if fecha_inicio:
        query += " AND a.fecha >= ?"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND a.fecha <= ?"
        params.append(fecha_fin)
    if id_ruta_filtro:
        query += " AND r.id_ruta = ?"
        params.append(id_ruta_filtro)
    if id_responsable_filtro:
        query += " AND resp.id_responsable = ?"
        params.append(id_responsable_filtro)
    if estado_filtro:
        query += " AND COALESCE(cc.estado, 'Pendiente') = ?"
        params.append(estado_filtro)

    query += " ORDER BY a.fecha DESC, a.id_asignacion DESC"

    cursor.execute(query, params)
    historial_raw = cursor.fetchall()

    # Evidencias y observaciones agrupadas por asignación
    cursor.execute("SELECT * FROM evidencia ORDER BY fecha DESC")
    evidencias_por_asignacion = {}
    for ev in cursor.fetchall():
        evidencias_por_asignacion.setdefault(ev['id_asignacion'], []).append(ev)

    cursor.execute("SELECT * FROM observacion ORDER BY fecha DESC")
    observaciones_por_asignacion = {}
    for ob in cursor.fetchall():
        observaciones_por_asignacion.setdefault(ob['id_asignacion'], []).append(ob)

    historial = []
    for h in historial_raw:
        item = dict(h)
        item['evidencias']    = evidencias_por_asignacion.get(h['id_asignacion'], [])
        item['observaciones'] = observaciones_por_asignacion.get(h['id_asignacion'], [])
        historial.append(item)

    cursor.execute("SELECT id_ruta, nombre_ruta FROM ruta ORDER BY nombre_ruta")
    rutas = cursor.fetchall()

    cursor.execute("SELECT id_responsable, nombre FROM responsable ORDER BY nombre")
    responsables = cursor.fetchall()

    conexion.close()

    return render_template(
        'historial.html',
        historial=historial,
        rutas=rutas,
        responsables=responsables,
        filtros={
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'id_ruta': id_ruta_filtro,
            'id_responsable': id_responsable_filtro,
            'estado': estado_filtro
        }
    )        
# =====================================
# EJECUTAR APP
# =====================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)