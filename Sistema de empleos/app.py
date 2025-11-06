from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import json
import os
from datetime import datetime
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_muy_segura_aqui'

# Directorio de datos
DATA_DIR = 'data'

# Asegurar que el directorio data existe
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Archivos JSON para simular BD
USUARIOS_FILE = os.path.join(DATA_DIR, 'usuarios.json')
EMPLEADORES_FILE = os.path.join(DATA_DIR, 'empleadores.json')
TRABAJOS_FILE = os.path.join(DATA_DIR, 'trabajos.json')
MENSAJES_FILE = os.path.join(DATA_DIR, 'mensajes.json')
CALIFICACIONES_FILE = os.path.join(DATA_DIR, 'calificaciones.json')
REPORTES_FILE = os.path.join(DATA_DIR, 'reportes.json')  # NUEVO - SISTEMA DE REPORTES
POSTULACIONES_FILE = os.path.join(DATA_DIR, 'postulaciones.json')
ALERTAS_FILE = os.path.join(DATA_DIR, 'alertas.json')
TRABAJOS_ACTIVOS_FILE = os.path.join(DATA_DIR, 'trabajos_activos.json')

# ===== FUNCIONES HELPER PARA JINJA2 =====
def none_containing(seq, value):
    """Helper function for Jinja2 templates"""
    if seq is None:
        return True
    return value not in seq

# Registra la función en Jinja2
app.jinja_env.filters['none_containing'] = none_containing

# ===== FUNCIONES DE LIMPIEZA AUTOMÁTICA =====
def limpiar_alertas_expiradas():
    """Eliminar alertas expiradas automáticamente"""
    alertas = leer_json(ALERTAS_FILE)
    alertas_actualizadas = []
    
    for alerta in alertas:
        # Si tiene fecha de expiración y ya pasó, no incluirla
        if alerta.get('fecha_expiracion'):
            try:
                fecha_expiracion = datetime.fromisoformat(alerta['fecha_expiracion'])
                if fecha_expiracion < datetime.now():
                    continue  # Saltar esta alerta expirada
            except (ValueError, KeyError):
                # Si hay error en la fecha, mantener la alerta
                pass
        
        alertas_actualizadas.append(alerta)
    
    if len(alertas_actualizadas) != len(alertas):
        escribir_json(ALERTAS_FILE, alertas_actualizadas)
        print(f"✅ Alertas expiradas limpiadas: {len(alertas) - len(alertas_actualizadas)} eliminadas")

# Funciones para manejar JSON
def leer_json(archivo):
    try:
        if not os.path.exists(archivo):
            print(f"DEBUG: Archivo {archivo} no existe, retornando lista vacía")
            return []
        
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read().strip()
            if not contenido:
                print(f"DEBUG: Archivo {archivo} está vacío")
                return []
            
            datos = json.loads(contenido)
            print(f"DEBUG: Archivo {archivo} leído exitosamente, {len(datos)} registros")
            return datos
            
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"DEBUG: Error leyendo {archivo}: {e}")
        return []

def obtener_usuario_por_id(user_id):
    usuarios = leer_json(USUARIOS_FILE)
    return next((u for u in usuarios if u['id'] == user_id), None)

def escribir_json(archivo, datos):
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def crear_datos_prueba():
    """Crear datos de prueba automáticamente"""
    
    # Datos de usuarios/estudiantes de prueba
    usuarios_prueba = [
        {
            'id': '1',
            'nombres': 'María',
            'apellidos': 'García López',
            'email': 'maria.garcia@email.com',
            'password': generate_password_hash('123456'),
            'codigo_estudiante': '231.0408.026',
            'dni': '76543218',
            'telefono': '987654321',
            'universidad': 'Universidad Nacional Mayor de San Marcos',
            'carrera': 'Administración de Empresas',
            'habilidades': 'Mesero, Atención al cliente, Organización de eventos',
            'horario_clases': 'Lunes y Miércoles 8:00-12:00, Viernes 14:00-16:00',
            'fecha_registro': datetime.now().isoformat()
        },
        {
            'id': '2',
            'nombres': 'Carlos',
            'apellidos': 'López Mendoza',
            'email': 'carlos.lopez@email.com',
            'password': generate_password_hash('123456'),
            'codigo_estudiante': '231.0512.015',
            'dni': '87654321',
            'telefono': '912345678',
            'universidad': 'Universidad de Lima',
            'carrera': 'Ingeniería de Sistemas',
            'habilidades': 'Tutoría de programación, Asistente técnico, Soporte IT',
            'horario_clases': 'Martes y Jueves 9:00-13:00, Sábados 8:00-12:00',
            'fecha_registro': datetime.now().isoformat()
        },
        {
            'id': '3',
            'nombres': 'Ana',
            'apellidos': 'Rodríguez Castro',
            'email': 'ana.rodriguez@email.com',
            'password': generate_password_hash('123456'),
            'codigo_estudiante': '231.0325.038',
            'dni': '98765432',
            'telefono': '934567890',
            'universidad': 'Pontificia Universidad Católica del Perú',
            'carrera': 'Psicología',
            'habilidades': 'Paseo de perros, Cuidado de mascotas, Tutoría de inglés',
            'horario_clases': 'Lunes a Viernes 7:00-11:00',
            'fecha_registro': datetime.now().isoformat()
        }
    ]
    
    # Datos de empleadores de prueba
    empleadores_prueba = [
        {
            'id': '1',
            'empresa': 'Restaurante Las Brasas',
            'ruc': '20123456789',
            'dni_representante': '12345678',
            'nombre_representante': 'Roberto Silva',
            'email': 'restaurante.lasbrasas@email.com',
            'password': generate_password_hash('123456'),
            'telefono': '901234567',
            'direccion': 'Av. Arequipa 123, Miraflores',
            'rubro': 'Gastronomía',
            'fecha_registro': datetime.now().isoformat()
        },
        {
            'id': '2',
            'empresa': 'TechTronics SAC',
            'ruc': '20456789123',
            'dni_representante': '23456789',
            'nombre_representante': 'Laura Mendoza',
            'email': 'techtronics.sac@email.com',
            'password': generate_password_hash('123456'),
            'telefono': '902345678',
            'direccion': 'Calle Los Pinos 456, San Isidro',
            'rubro': 'Tecnología',
            'fecha_registro': datetime.now().isoformat()
        },
        {
            'id': '3',
            'empresa': 'Mascotas Felices',
            'ruc': '20567891234',
            'dni_representante': '34567890',
            'nombre_representante': 'Miguel Torres',
            'email': 'mascotasfelices@email.com',
            'password': generate_password_hash('123456'),
            'telefono': '903456789',
            'direccion': 'Jr. Las Flores 789, Surco',
            'rubro': 'Cuidado de mascotas',
            'fecha_registro': datetime.now().isoformat()
        }
    ]
    
    # Datos de trabajos de prueba
    trabajos_prueba = [
        {
            'id': '1',
            'empleador_id': '1',
            'titulo': 'Mesero para evento corporativo',
            'descripcion': 'Se necesita mesero para evento corporativo este viernes. Experiencia en servicio de catering requerida.',
            'categoria': 'Gastronomía',
            'pago': '180',
            'horario': 'Viernes 18:00-23:00',
            'ubicacion': 'Miraflores',
            'estado': 'disponible',
            'fecha_publicacion': datetime.now().isoformat()
        },
        {
            'id': '2',
            'empleador_id': '2',
            'titulo': 'Asistente de soporte técnico',
            'descripcion': 'Buscamos estudiante de sistemas para asistir en soporte técnico a usuarios internos.',
            'categoria': 'Tecnología',
            'pago': '25',
            'horario': 'Lunes a Viernes 15:00-18:00',
            'ubicacion': 'San Isidro',
            'estado': 'disponible',
            'fecha_publicacion': datetime.now().isoformat()
        },
        {
            'id': '3',
            'empleador_id': '3',
            'titulo': 'Paseador de perros por las mañanas',
            'descripcion': 'Paseo de 3 perros pequeños por las mañanas. Deben ser amigables con los animales.',
            'categoria': 'Cuidado de mascotas',
            'pago': '15',
            'horario': 'Lunes a Viernes 7:00-9:00',
            'ubicacion': 'Surco',
            'estado': 'disponible',
            'fecha_publicacion': datetime.now().isoformat()
        }
    ]
    
    # Crear algunos trabajos activos de prueba
    trabajos_activos_prueba = [
        {
            'id': '1',
            'postulacion_id': '1',
            'trabajo_id': '1',
            'usuario_id': '1',  # María García
            'empleador_id': '1',  # Restaurante Las Brasas
            'titulo': 'Mesero para evento corporativo',
            'descripcion': 'Se necesita mesero para evento corporativo este viernes. Experiencia en servicio de catering requerida.',
            'pago': '180',
            'horario_trabajo': 'Viernes 18:00-23:00',
            'ubicacion': 'Miraflores',
            'estado': 'activo',
            'fecha_inicio': datetime.now().isoformat(),
            'fecha_finalizacion': None
        }
    ]

    # Escribir datos de prueba
    escribir_json(USUARIOS_FILE, usuarios_prueba)
    escribir_json(EMPLEADORES_FILE, empleadores_prueba)
    escribir_json(TRABAJOS_FILE, trabajos_prueba)
    escribir_json(TRABAJOS_ACTIVOS_FILE, trabajos_activos_prueba)
    
    # Crear archivos vacíos para los demás datos
    escribir_json(MENSAJES_FILE, [])
    escribir_json(CALIFICACIONES_FILE, [])
    escribir_json(REPORTES_FILE, [])
    escribir_json(POSTULACIONES_FILE, [])
    escribir_json(ALERTAS_FILE, [])
    
    print("✅ Datos de prueba creados exitosamente!")

def inicializar_archivos():
    archivos = {
        USUARIOS_FILE: [],
        EMPLEADORES_FILE: [],
        TRABAJOS_FILE: [],
        MENSAJES_FILE: [],
        CALIFICACIONES_FILE: [],
        REPORTES_FILE: [],  # NUEVO - SISTEMA DE REPORTES
        POSTULACIONES_FILE: [],
        ALERTAS_FILE: [],
        TRABAJOS_ACTIVOS_FILE: []
    }
    
    for archivo, datos in archivos.items():
        if not os.path.exists(archivo):
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
    
    if os.path.getsize(USUARIOS_FILE) == 0:
        crear_datos_prueba()

# Validaciones
def validar_codigo_estudiante(codigo):
    patron = r'^\d{3}\.\d{4}\.\d{3}$'
    return bool(re.match(patron, codigo))

def validar_dni(dni):
    return len(dni) == 8 and dni.isdigit()

def validar_ruc(ruc):
    return len(ruc) == 11 and ruc.isdigit()

def validar_telefono(telefono):
    return len(telefono) == 9 and telefono.isdigit()

def validar_email(email):
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email))

def validar_pago(pago):
    try:
        return float(pago) > 0
    except ValueError:
        return False

# Rutas principales
@app.route('/')
def index():
    trabajos = leer_json(TRABAJOS_FILE)
    trabajos_disponibles = [t for t in trabajos if t.get('estado') == 'disponible']
    return render_template('index.html', trabajos=trabajos_disponibles[:3])

@app.route('/login')
def login():
    return render_template('login_usuario.html')

# ===== SELECCIÓN DE TIPO DE USUARIO =====
@app.route('/seleccion-tipo')
def seleccion_tipo():
    return render_template('seleccion_tipo.html')

@app.route('/seleccion/estudiante')
def seleccion_estudiante():
    # Puedes expandir esta página después con más info para estudiantes
    return redirect(url_for('registro_usuario'))

@app.route('/seleccion/empleador')
def seleccion_empleador():
    # Puedes expandir esta página después con más info para empleadores
    return redirect(url_for('registro_empleador'))

@app.route('/acerca')
def acerca():
    return render_template('acerca.html')

@app.route('/debug/session')
def debug_session():
    """Ruta para debuggear la sesión actual"""
    session_info = {
        'user_id': session.get('user_id'),
        'user_type': session.get('user_type'), 
        'user_name': session.get('user_name'),
        'session_keys': list(session.keys())
    }
    return jsonify(session_info)


# ===== RUTAS DE TRABAJOS PÚBLICOS =====

@app.route('/trabajos')
def ver_trabajos():
    trabajos = leer_json(TRABAJOS_FILE)
    trabajos_disponibles = [t for t in trabajos if t.get('estado') == 'disponible']
    categorias = list(set(t['categoria'] for t in trabajos_disponibles))
    
    categoria_filtro = request.args.get('categoria', '')
    if categoria_filtro:
        trabajos_filtrados = [t for t in trabajos_disponibles if t['categoria'] == categoria_filtro]
    else:
        trabajos_filtrados = trabajos_disponibles
    
    return render_template('trabajos.html', 
                         trabajos=trabajos_filtrados, 
                         categorias=categorias, 
                         categoria_actual=categoria_filtro)

@app.route('/trabajo/<trabajo_id>/aplicar', methods=['POST'])
def aplicar_trabajo(trabajo_id):
    if 'user_id' not in session or session['user_type'] != 'usuario':
        flash('Debes iniciar sesión como usuario para aplicar a trabajos', 'error')
        return redirect(url_for('login_usuario'))
    
    try:
        trabajos = leer_json(TRABAJOS_FILE)
        trabajo = next((t for t in trabajos if t['id'] == trabajo_id), None)
        
        if not trabajo:
            flash('Trabajo no encontrado', 'error')
            return redirect(url_for('ver_trabajos'))
        
        # Verificar si ya aplicó
        postulaciones = leer_json(POSTULACIONES_FILE)
        ya_aplico = any(p['usuario_id'] == session['user_id'] and p['trabajo_id'] == trabajo_id for p in postulaciones)
        
        if ya_aplico:
            flash('Ya has aplicado a este trabajo', 'error')
            return redirect(url_for('ver_trabajos'))
        
        # Crear postulación
        postulacion = {
            'id': str(len(postulaciones) + 1),
            'trabajo_id': trabajo_id,
            'usuario_id': session['user_id'],
            'empleador_id': trabajo['empleador_id'],
            'estado': 'pendiente',
            'fecha_postulacion': datetime.now().isoformat(),
            'mensaje': request.form.get('mensaje', '')
        }
        
        postulaciones.append(postulacion)
        escribir_json(POSTULACIONES_FILE, postulaciones)
        
        flash(f'¡Has aplicado al trabajo: {trabajo["titulo"]}!', 'success')
        return redirect(url_for('ver_trabajos'))
    
    except Exception as e:
        flash('Error al aplicar al trabajo', 'error')
        return redirect(url_for('ver_trabajos'))

# ===== RUTAS DE GESTIÓN DE POSTULACIONES =====

@app.route('/empleador/postulaciones/<trabajo_id>')
def ver_postulaciones(trabajo_id):
    if 'user_id' not in session or session['user_type'] != 'empleador':
        return redirect(url_for('login_empleador'))
    
    try:
        trabajos = leer_json(TRABAJOS_FILE)
        trabajo = next((t for t in trabajos if t['id'] == trabajo_id and t['empleador_id'] == session['user_id']), None)
        
        if not trabajo:
            flash('Trabajo no encontrado o no tienes permisos', 'error')
            return redirect(url_for('dashboard_empleador'))
        
        postulaciones = leer_json(POSTULACIONES_FILE)
        usuarios = leer_json(USUARIOS_FILE)
        
        # Obtener postulaciones para este trabajo con info de usuarios
        postulaciones_trabajo = []
        for postulacion in postulaciones:
            if postulacion['trabajo_id'] == trabajo_id:
                usuario = next((u for u in usuarios if u['id'] == postulacion['usuario_id']), None)
                if usuario:
                    postulacion_con_info = postulacion.copy()
                    postulacion_con_info['usuario_info'] = usuario
                    postulaciones_trabajo.append(postulacion_con_info)
        
        return render_template('ver_postulaciones.html', 
                             trabajo=trabajo, 
                             postulaciones=postulaciones_trabajo)
    
    except Exception as e:
        flash('Error al cargar las postulaciones', 'error')
        return redirect(url_for('dashboard_empleador'))

@app.route('/empleador/postulacion/<postulacion_id>/<accion>')
def gestionar_postulacion(postulacion_id, accion):
    if 'user_id' not in session or session['user_type'] != 'empleador':
        return redirect(url_for('login_empleador'))
    
    try:
        postulaciones = leer_json(POSTULACIONES_FILE)
        postulacion = next((p for p in postulaciones if p['id'] == postulacion_id), None)
        
        if not postulacion:
            flash('Postulación no encontrada', 'error')
            return redirect(url_for('dashboard_empleador'))
        
        # Verificar que el empleador es dueño del trabajo
        trabajos = leer_json(TRABAJOS_FILE)
        trabajo = next((t for t in trabajos if t['id'] == postulacion['trabajo_id'] and t['empleador_id'] == session['user_id']), None)
        
        if not trabajo:
            flash('No tienes permisos para gestionar esta postulación', 'error')
            return redirect(url_for('dashboard_empleador'))
        
        # Actualizar estado
        if accion in ['aceptar', 'rechazar']:
            for i, p in enumerate(postulaciones):
                if p['id'] == postulacion_id:
                    postulaciones[i]['estado'] = 'aceptado' if accion == 'aceptar' else 'rechazado'
                    postulaciones[i]['fecha_respuesta'] = datetime.now().isoformat()
                    
                    # Si se acepta, crear trabajo activo
                    if accion == 'aceptar':
                        trabajos_activos = leer_json(TRABAJOS_ACTIVOS_FILE)
                        
                        trabajo_activo = {
                            'id': str(len(trabajos_activos) + 1),
                            'postulacion_id': postulacion_id,
                            'trabajo_id': trabajo['id'],
                            'usuario_id': postulacion['usuario_id'],
                            'empleador_id': session['user_id'],
                            'titulo': trabajo['titulo'],
                            'descripcion': trabajo['descripcion'],
                            'pago': trabajo['pago'],
                            'horario_trabajo': trabajo['horario'],
                            'ubicacion': trabajo['ubicacion'],
                            'estado': 'activo',  # activo, finalizado, cancelado
                            'fecha_inicio': datetime.now().isoformat(),
                            'fecha_finalizacion': None
                        }
                        
                        trabajos_activos.append(trabajo_activo)
                        escribir_json(TRABAJOS_ACTIVOS_FILE, trabajos_activos)
                        
                        # Actualizar estado del trabajo a "ocupado"
                        for j, t in enumerate(trabajos):
                            if t['id'] == trabajo['id']:
                                trabajos[j]['estado'] = 'ocupado'
                                break
                        
                        escribir_json(TRABAJOS_FILE, trabajos)
                    
                    break
            
            escribir_json(POSTULACIONES_FILE, postulaciones)
            
            if accion == 'aceptar':
                flash('Postulación aceptada exitosamente. El trabajo ahora está activo.', 'success')
            else:
                flash('Postulación rechazada', 'success')
        
        return redirect(url_for('ver_postulaciones', trabajo_id=postulacion['trabajo_id']))
    
    except Exception as e:
        flash('Error al gestionar la postulación', 'error')
        return redirect(url_for('dashboard_empleador'))

# ===== RUTAS DE GESTIÓN DE TRABAJOS =====

@app.route('/empleador/editar-trabajo/<trabajo_id>', methods=['GET', 'POST'])
def editar_trabajo(trabajo_id):
    if 'user_id' not in session or session['user_type'] != 'empleador':
        return redirect(url_for('login_empleador'))
    
    try:
        trabajos = leer_json(TRABAJOS_FILE)
        trabajo = next((t for t in trabajos if t['id'] == trabajo_id and t['empleador_id'] == session['user_id']), None)
        
        if not trabajo:
            flash('Trabajo no encontrado o no tienes permisos', 'error')
            return redirect(url_for('dashboard_empleador'))
        
        if request.method == 'POST':
            # Validar pago
            if not validar_pago(request.form['pago']):
                flash('El pago debe ser un número positivo', 'error')
                return render_template('editar_trabajo.html', trabajo=trabajo)
            
            # Actualizar datos del trabajo
            trabajo['titulo'] = request.form['titulo']
            trabajo['descripcion'] = request.form['descripcion']
            trabajo['categoria'] = request.form['categoria']
            trabajo['pago'] = request.form['pago']
            trabajo['horario'] = request.form['horario']
            trabajo['ubicacion'] = request.form['ubicacion']
            trabajo['requisitos'] = request.form['requisitos']
            trabajo['estado'] = request.form['estado']
            
            # Guardar cambios
            for i, t in enumerate(trabajos):
                if t['id'] == trabajo_id:
                    trabajos[i] = trabajo
                    break
            
            escribir_json(TRABAJOS_FILE, trabajos)
            flash('Trabajo actualizado exitosamente', 'success')
            return redirect(url_for('dashboard_empleador'))
        
        return render_template('editar_trabajo.html', trabajo=trabajo)
    
    except Exception as e:
        flash('Error al editar el trabajo', 'error')
        return redirect(url_for('dashboard_empleador'))

@app.route('/empleador/eliminar-trabajo/<trabajo_id>')
def eliminar_trabajo(trabajo_id):
    if 'user_id' not in session or session['user_type'] != 'empleador':
        return redirect(url_for('login_empleador'))
    
    try:
        trabajos = leer_json(TRABAJOS_FILE)
        trabajo = next((t for t in trabajos if t['id'] == trabajo_id and t['empleador_id'] == session['user_id']), None)
        
        if not trabajo:
            flash('Trabajo no encontrado o no tienes permisos', 'error')
            return redirect(url_for('dashboard_empleador'))
        
        # Eliminar trabajo
        trabajos = [t for t in trabajos if t['id'] != trabajo_id]
        escribir_json(TRABAJOS_FILE, trabajos)
        
        # También eliminar postulaciones relacionadas
        postulaciones = leer_json(POSTULACIONES_FILE)
        postulaciones = [p for p in postulaciones if p['trabajo_id'] != trabajo_id]
        escribir_json(POSTULACIONES_FILE, postulaciones)
        
        flash('Trabajo eliminado exitosamente', 'success')
        return redirect(url_for('dashboard_empleador'))
    
    except Exception as e:
        flash('Error al eliminar el trabajo', 'error')
        return redirect(url_for('dashboard_empleador'))

# ===== RUTAS DE GESTIÓN DE TRABAJOS ACTIVOS =====

@app.route('/empleador/trabajos-activos')
def empleador_trabajos_activos():
    if 'user_id' not in session or session['user_type'] != 'empleador':
        return redirect(url_for('login_empleador'))
    
    try:
        trabajos_activos = leer_json(TRABAJOS_ACTIVOS_FILE)
        usuarios = leer_json(USUARIOS_FILE)
        
        # Filtrar trabajos activos del empleador
        trabajos_activos_empleador = []
        for trabajo in trabajos_activos:
            if trabajo['empleador_id'] == session['user_id']:
                usuario_info = next((u for u in usuarios if u['id'] == trabajo['usuario_id']), None)
                if usuario_info:
                    trabajo_con_info = trabajo.copy()
                    trabajo_con_info['usuario_info'] = usuario_info
                    trabajos_activos_empleador.append(trabajo_con_info)
        
        # Separar por estado
        trabajos_activos_list = [t for t in trabajos_activos_empleador if t['estado'] == 'activo']
        trabajos_finalizados_list = [t for t in trabajos_activos_empleador if t['estado'] == 'finalizado']
        
        return render_template('empleador_trabajos_activos.html', 
                             trabajos_activos=trabajos_activos_list,
                             trabajos_finalizados=trabajos_finalizados_list)
    
    except Exception as e:
        flash('Error al cargar los trabajos activos', 'error')
        return redirect(url_for('dashboard_empleador'))

# Login y registro de Usuarios
@app.route('/login/usuario', methods=['GET', 'POST'])
def login_usuario():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            usuarios = leer_json(USUARIOS_FILE)
            for usuario in usuarios:
                if usuario['email'] == email and check_password_hash(usuario['password'], password):
                    session['user_id'] = usuario['id']
                    session['user_type'] = 'usuario'
                    session['user_name'] = usuario['nombres']
                    flash(f'Bienvenido {usuario["nombres"]}!', 'success')
                    return redirect(url_for('dashboard_usuario'))
            
            flash('Credenciales incorrectas', 'error')
        
        except Exception as e:
            flash('Error al iniciar sesión', 'error')
    
    return render_template('login_usuario.html')

@app.route('/registro/usuario', methods=['GET', 'POST'])
def registro_usuario():
    if request.method == 'POST':
        try:
            datos = {
                'id': str(len(leer_json(USUARIOS_FILE)) + 1),
                'nombres': request.form['nombres'],
                'apellidos': request.form['apellidos'],
                'email': request.form['email'],
                'password': generate_password_hash(request.form['password']),
                'codigo_estudiante': request.form['codigo_estudiante'],
                'dni': request.form['dni'],
                'telefono': request.form['telefono'],
                'universidad': request.form['universidad'],
                'carrera': request.form['carrera'],
                'horario_clases': request.form.get('horario_clases', ''),
                'habilidades': request.form.get('habilidades', ''),
                'fecha_registro': datetime.now().isoformat()
            }
            
            # Validaciones
            if not validar_codigo_estudiante(datos['codigo_estudiante']):
                flash('Código de estudiante inválido. Formato: 231.0408.026', 'error')
                return render_template('registro_usuario.html')
            
            if not validar_dni(datos['dni']):
                flash('DNI debe tener 8 dígitos', 'error')
                return render_template('registro_usuario.html')
            
            if not validar_telefono(datos['telefono']):
                flash('Teléfono debe tener 9 dígitos', 'error')
                return render_template('registro_usuario.html')
            
            if not validar_email(datos['email']):
                flash('Email inválido', 'error')
                return render_template('registro_usuario.html')
            
            # Verificar si el email ya existe
            usuarios = leer_json(USUARIOS_FILE)
            if any(u['email'] == datos['email'] for u in usuarios):
                flash('El email ya está registrado', 'error')
                return render_template('registro_usuario.html')
            
            # Guardar usuario
            usuarios.append(datos)
            escribir_json(USUARIOS_FILE, usuarios)
            
            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login_usuario'))
        
        except Exception as e:
            flash('Error en el registro', 'error')
    
    return render_template('registro_usuario.html')

# Login y registro de Empleadores
@app.route('/login/empleador', methods=['GET', 'POST'])
def login_empleador():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            empleadores = leer_json(EMPLEADORES_FILE)
            for empleador in empleadores:
                if empleador['email'] == email and check_password_hash(empleador['password'], password):
                    session['user_id'] = empleador['id']
                    session['user_type'] = 'empleador'
                    session['user_name'] = empleador['empresa']
                    flash(f'Bienvenido {empleador["empresa"]}!', 'success')
                    return redirect(url_for('dashboard_empleador'))
            
            flash('Credenciales incorrectas', 'error')
        
        except Exception as e:
            flash('Error al iniciar sesión', 'error')
    
    return render_template('login_empleador.html')

@app.route('/registro/empleador', methods=['GET', 'POST'])
def registro_empleador():
    if request.method == 'POST':
        try:
            datos = {
                'id': str(len(leer_json(EMPLEADORES_FILE)) + 1),
                'empresa': request.form['empresa'],
                'ruc': request.form['ruc'],
                'dni_representante': request.form['dni_representante'],
                'nombre_representante': request.form['nombre_representante'],
                'email': request.form['email'],
                'password': generate_password_hash(request.form['password']),
                'telefono': request.form['telefono'],
                'direccion': request.form['direccion'],
                'rubro': request.form['rubro'],
                'fecha_registro': datetime.now().isoformat()
            }
            
            # Validaciones
            if not validar_ruc(datos['ruc']):
                flash('RUC debe tener 11 dígitos', 'error')
                return render_template('registro_empleador.html')
            
            if not validar_dni(datos['dni_representante']):
                flash('DNI debe tener 8 dígitos', 'error')
                return render_template('registro_empleador.html')
            
            if not validar_telefono(datos['telefono']):
                flash('Teléfono debe tener 9 dígitos', 'error')
                return render_template('registro_empleador.html')
            
            if not validar_email(datos['email']):
                flash('Email inválido', 'error')
                return render_template('registro_empleador.html')
            
            # Verificar si el RUC o email ya existen
            empleadores = leer_json(EMPLEADORES_FILE)
            if any(e['ruc'] == datos['ruc'] for e in empleadores):
                flash('El RUC ya está registrado', 'error')
                return render_template('registro_empleador.html')
            
            if any(e['email'] == datos['email'] for e in empleadores):
                flash('El email ya está registrado', 'error')
                return render_template('registro_empleador.html')
            
            # Guardar empleador
            empleadores.append(datos)
            escribir_json(EMPLEADORES_FILE, empleadores)
            
            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login_empleador'))
        
        except Exception as e:
            flash('Error en el registro', 'error')
    
    return render_template('registro_empleador.html')

# Dashboards
@app.route('/dashboard/usuario')
def dashboard_usuario():
    if 'user_id' not in session or session['user_type'] != 'usuario':
        return redirect(url_for('login_usuario'))
    
    try:
        limpiar_alertas_expiradas()
        usuario = next((u for u in leer_json(USUARIOS_FILE) if u['id'] == session['user_id']), None)
        trabajos = leer_json(TRABAJOS_FILE)
        
        # Obtener trabajos activos del usuario
        trabajos_activos = leer_json(TRABAJOS_ACTIVOS_FILE)
        trabajos_activos_usuario = [t for t in trabajos_activos if t['usuario_id'] == session['user_id'] and t['estado'] == 'activo']
        
        # Obtener alertas
        alertas = leer_json(ALERTAS_FILE)
        
        return render_template('dashboard_usuario.html', 
                             usuario=usuario, 
                             trabajos=trabajos,
                             trabajos_activos=trabajos_activos_usuario,
                             alertas=alertas)
    
    except Exception as e:
        flash('Error al cargar el dashboard', 'error')
        return redirect(url_for('login_usuario'))
    
@app.route('/dashboard/empleador')
def dashboard_empleador():
    if 'user_id' not in session or session.get('user_type') != 'empleador':
        flash('Debes iniciar sesión como empleador', 'error')
        return redirect(url_for('login_empleador'))
    
    try:
        empleadores = leer_json(EMPLEADORES_FILE)
        empleador = next((e for e in empleadores if e['id'] == session['user_id']), None)
        
        if not empleador:
            session.clear()
            flash('Sesión inválida', 'error')
            return redirect(url_for('login_empleador'))
        
        # Cargar todos los datos necesarios
        trabajos = [t for t in leer_json(TRABAJOS_FILE) if t.get('empleador_id') == session['user_id']]
        
        trabajos_activos = leer_json(TRABAJOS_ACTIVOS_FILE)
        trabajos_activos_empleador = [t for t in trabajos_activos if t.get('empleador_id') == session['user_id'] and t.get('estado') == 'activo']
        
        # Cargar usuarios para los trabajos activos
        usuarios = leer_json(USUARIOS_FILE)
        for trabajo in trabajos_activos_empleador:
            usuario_info = next((u for u in usuarios if u['id'] == trabajo['usuario_id']), None)
            trabajo['usuario_info'] = usuario_info
        
        alertas = leer_json(ALERTAS_FILE)
        
        return render_template('dashboard_empleador.html', 
                             empleador=empleador, 
                             trabajos=trabajos,
                             trabajos_activos=trabajos_activos_empleador,
                             alertas=alertas,
                             usuarios=usuarios)  # ← NUEVO: pasar usuarios al template
    
    except Exception as e:
        print(f"Error en dashboard empleador: {e}")
        flash('Error al cargar el dashboard. Por favor, intenta nuevamente.', 'error')
        return redirect(url_for('login_empleador'))

@app.route('/usuario/mis-postulaciones')
def ver_mis_postulaciones():
    if 'user_id' not in session or session['user_type'] != 'usuario':
        return redirect(url_for('login_usuario'))
    
    try:
        postulaciones = leer_json(POSTULACIONES_FILE)
        trabajos = leer_json(TRABAJOS_FILE)
        empleadores = leer_json(EMPLEADORES_FILE)
        
        mis_postulaciones = []
        for postulacion in postulaciones:
            if postulacion['usuario_id'] == session['user_id']:
                trabajo = next((t for t in trabajos if t['id'] == postulacion['trabajo_id']), None)
                if trabajo:
                    empleador = next((e for e in empleadores if e['id'] == trabajo['empleador_id']), None)
                    postulacion_con_info = postulacion.copy()
                    postulacion_con_info['trabajo_info'] = trabajo
                    postulacion_con_info['empleador_info'] = empleador
                    mis_postulaciones.append(postulacion_con_info)
        
        return render_template('mis_postulaciones.html', postulaciones=mis_postulaciones)
    
    except Exception as e:
        flash('Error al cargar las postulaciones', 'error')
        return redirect(url_for('dashboard_usuario'))

# ===== RUTAS DE EDICIÓN DE PERFIL =====
@app.route('/usuario/editar-perfil', methods=['GET', 'POST'])
def editar_perfil_usuario():
    if 'user_id' not in session or session['user_type'] != 'usuario':
        return redirect(url_for('login_usuario'))
    
    try:
        usuarios = leer_json(USUARIOS_FILE)
        usuario = next((u for u in usuarios if u['id'] == session['user_id']), None)
        
        if request.method == 'POST':
            # Actualizar datos
            usuario['nombres'] = request.form['nombres']
            usuario['apellidos'] = request.form['apellidos']
            usuario['telefono'] = request.form['telefono']
            usuario['universidad'] = request.form['universidad']
            usuario['carrera'] = request.form['carrera']
            usuario['habilidades'] = request.form['habilidades']
            usuario['horario_clases'] = request.form['horario_clases']
            
            # Validar teléfono
            if not validar_telefono(usuario['telefono']):
                flash('Teléfono debe tener 9 dígitos', 'error')
                return render_template('editar_perfil_usuario.html', usuario=usuario)
            
            # Guardar cambios
            for i, u in enumerate(usuarios):
                if u['id'] == session['user_id']:
                    usuarios[i] = usuario
                    break
            
            escribir_json(USUARIOS_FILE, usuarios)
            session['user_name'] = usuario['nombres']
            flash('Perfil actualizado exitosamente', 'success')
            return redirect(url_for('dashboard_usuario'))
        
        return render_template('editar_perfil_usuario.html', usuario=usuario)
    
    except Exception as e:
        flash('Error al editar el perfil', 'error')
        return redirect(url_for('dashboard_usuario'))

@app.route('/empleador/editar-perfil', methods=['GET', 'POST'])
def editar_perfil_empleador():
    if 'user_id' not in session or session['user_type'] != 'empleador':
        return redirect(url_for('login_empleador'))
    
    try:
        empleadores = leer_json(EMPLEADORES_FILE)
        empleador = next((e for e in empleadores if e['id'] == session['user_id']), None)
        
        if request.method == 'POST':
            # Actualizar datos
            empleador['empresa'] = request.form['empresa']
            empleador['nombre_representante'] = request.form['nombre_representante']
            empleador['telefono'] = request.form['telefono']
            empleador['direccion'] = request.form['direccion']
            empleador['rubro'] = request.form['rubro']
            
            # Validar teléfono
            if not validar_telefono(empleador['telefono']):
                flash('Teléfono debe tener 9 dígitos', 'error')
                return render_template('editar_perfil_empleador.html', empleador=empleador)
            
            # Guardar cambios
            for i, e in enumerate(empleadores):
                if e['id'] == session['user_id']:
                    empleadores[i] = empleador
                    break
            
            escribir_json(EMPLEADORES_FILE, empleadores)
            session['user_name'] = empleador['empresa']
            flash('Perfil actualizado exitosamente', 'success')
            return redirect(url_for('dashboard_empleador'))
        
        return render_template('editar_perfil_empleador.html', empleador=empleador)
    
    except Exception as e:
        flash('Error al editar el perfil', 'error')
        return redirect(url_for('dashboard_empleador'))

# ===== PUBLICAR TRABAJO =====

@app.route('/empleador/publicar-trabajo', methods=['GET', 'POST'])
def publicar_trabajo():
    if 'user_id' not in session or session['user_type'] != 'empleador':
        return redirect(url_for('login_empleador'))
    
    if request.method == 'POST':
        try:
            # Validar pago
            if not validar_pago(request.form['pago']):
                flash('El pago debe ser un número positivo', 'error')
                return render_template('publicar_trabajo.html')
            
            trabajo = {
                'id': str(len(leer_json(TRABAJOS_FILE)) + 1),
                'empleador_id': session['user_id'],
                'titulo': request.form['titulo'],
                'descripcion': request.form['descripcion'],
                'categoria': request.form['categoria'],
                'pago': request.form['pago'],
                'horario': request.form['horario'],
                'ubicacion': request.form['ubicacion'],
                'requisitos': request.form['requisitos'],
                'estado': 'disponible',
                'fecha_publicacion': datetime.now().isoformat()
            }
            
            trabajos = leer_json(TRABAJOS_FILE)
            trabajos.append(trabajo)
            escribir_json(TRABAJOS_FILE, trabajos)
            
            flash('Trabajo publicado exitosamente', 'success')
            return redirect(url_for('dashboard_empleador'))
        
        except Exception as e:
            flash('Error al publicar el trabajo', 'error')
    
    return render_template('publicar_trabajo.html')

# Login admin simple
@app.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == 'admin123':
            session['user_id'] = 'admin'
            session['user_type'] = 'admin'
            session['user_name'] = 'Administrador'
            return redirect(url_for('dashboard_admin'))
        else:
            flash('Credenciales de administrador incorrectas', 'error')
    
    return render_template('login_admin.html')

# ===== RUTAS ADMINISTRATIVAS =====

@app.route('/admin/usuarios')
def admin_usuarios():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))
    
    usuarios = leer_json(USUARIOS_FILE)
    return render_template('admin_usuarios.html', usuarios=usuarios)

@app.route('/admin/empleadores')
def admin_empleadores():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))
    
    empleadores = leer_json(EMPLEADORES_FILE)
    return render_template('admin_empleadores.html', empleadores=empleadores)

@app.route('/admin/debug/usuario/<user_id>')
def debug_usuario(user_id):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))
    
    datos = {
        'usuario': next((u for u in leer_json(USUARIOS_FILE) if u['id'] == user_id), None),
        'postulaciones': [p for p in leer_json(POSTULACIONES_FILE) if p['usuario_id'] == user_id],
        'trabajos_activos': [t for t in leer_json(TRABAJOS_ACTIVOS_FILE) if t['usuario_id'] == user_id],
        'calificaciones': [c for c in leer_json(CALIFICACIONES_FILE) if c['usuario_id'] == user_id],
        'mensajes_enviados': [m for m in leer_json(MENSAJES_FILE) if m['de_user_id'] == user_id],
        'mensajes_recibidos': [m for m in leer_json(MENSAJES_FILE) if m['para_user_id'] == user_id],
        'reportes_enviados': [r for r in leer_json(REPORTES_FILE) if r['reportador_id'] == user_id],
        'reportes_recibidos': [r for r in leer_json(REPORTES_FILE) if r['reportado_id'] == user_id]
    }
    
    return jsonify(datos)

@app.route('/admin/debug/empleador/<emp_id>')
def debug_empleador(emp_id):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))
    
    datos = {
        'empleador': next((e for e in leer_json(EMPLEADORES_FILE) if e['id'] == emp_id), None),
        'trabajos_publicados': [t for t in leer_json(TRABAJOS_FILE) if t['empleador_id'] == emp_id],
        'postulaciones_recibidas': [p for p in leer_json(POSTULACIONES_FILE) if p['empleador_id'] == emp_id],
        'trabajos_activos': [t for t in leer_json(TRABAJOS_ACTIVOS_FILE) if t['empleador_id'] == emp_id],
        'calificaciones_dadas': [c for c in leer_json(CALIFICACIONES_FILE) if c['empleador_id'] == emp_id],
        'mensajes_enviados': [m for m in leer_json(MENSAJES_FILE) if m['de_user_id'] == emp_id],
        'mensajes_recibidos': [m for m in leer_json(MENSAJES_FILE) if m['para_user_id'] == emp_id],
        'reportes_enviados': [r for r in leer_json(REPORTES_FILE) if r['reportador_id'] == emp_id],
        'reportes_recibidos': [r for r in leer_json(REPORTES_FILE) if r['reportado_id'] == emp_id]
    }
    
    return jsonify(datos)

@app.route('/admin/eliminar/usuario/<user_id>')
def admin_eliminar_usuario(user_id):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))
    
    try:
        # 1. Leer todos los archivos necesarios
        usuarios = leer_json(USUARIOS_FILE)
        trabajos = leer_json(TRABAJOS_FILE)
        postulaciones = leer_json(POSTULACIONES_FILE)
        trabajos_activos = leer_json(TRABAJOS_ACTIVOS_FILE)
        calificaciones = leer_json(CALIFICACIONES_FILE)
        mensajes = leer_json(MENSAJES_FILE)
        reportes = leer_json(REPORTES_FILE)
        
        # 2. Encontrar el usuario a eliminar
        usuario_eliminar = next((u for u in usuarios if u['id'] == user_id), None)
        if not usuario_eliminar:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('admin_usuarios'))
        
        # 3. Eliminar usuario de la lista de usuarios
        usuarios = [u for u in usuarios if u['id'] != user_id]
        escribir_json(USUARIOS_FILE, usuarios)
        
        # 4. Eliminar postulaciones del usuario
        postulaciones = [p for p in postulaciones if p['usuario_id'] != user_id]
        escribir_json(POSTULACIONES_FILE, postulaciones)
        
        # 5. Eliminar trabajos activos del usuario
        trabajos_activos = [t for t in trabajos_activos if t['usuario_id'] != user_id]
        escribir_json(TRABAJOS_ACTIVOS_FILE, trabajos_activos)
        
        # 6. Eliminar calificaciones del usuario
        calificaciones = [c for c in calificaciones if c['usuario_id'] != user_id]
        escribir_json(CALIFICACIONES_FILE, calificaciones)
        
        # 7. Eliminar mensajes del usuario (como remitente o destinatario)
        mensajes = [m for m in mensajes if m['de_user_id'] != user_id and m['para_user_id'] != user_id]
        escribir_json(MENSAJES_FILE, mensajes)
        
        # 8. Eliminar reportes donde el usuario es reportador o reportado
        reportes = [r for r in reportes if r['reportador_id'] != user_id and r['reportado_id'] != user_id]
        escribir_json(REPORTES_FILE, reportes)
        
        # 9. Para trabajos donde era empleador, cambiar el estado o eliminar
        # (Esto se maneja mejor en la eliminación de empleadores)
        
        flash(f'Usuario {usuario_eliminar["nombres"]} {usuario_eliminar["apellidos"]} eliminado exitosamente. Se limpiaron todos sus datos relacionados.', 'success')
        
    except Exception as e:
        print(f"Error eliminando usuario: {e}")
        flash('Error al eliminar el usuario', 'error')
    
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/eliminar/empleador/<emp_id>')
def admin_eliminar_empleador(emp_id):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))
    
    try:
        # 1. Leer todos los archivos necesarios
        empleadores = leer_json(EMPLEADORES_FILE)
        trabajos = leer_json(TRABAJOS_FILE)
        postulaciones = leer_json(POSTULACIONES_FILE)
        trabajos_activos = leer_json(TRABAJOS_ACTIVOS_FILE)
        calificaciones = leer_json(CALIFICACIONES_FILE)
        mensajes = leer_json(MENSAJES_FILE)
        reportes = leer_json(REPORTES_FILE)
        alertas = leer_json(ALERTAS_FILE)
        
        # 2. Encontrar el empleador a eliminar
        empleador_eliminar = next((e for e in empleadores if e['id'] == emp_id), None)
        if not empleador_eliminar:
            flash('Empleador no encontrado', 'error')
            return redirect(url_for('admin_empleadores'))
        
        # 3. Eliminar empleador de la lista
        empleadores = [e for e in empleadores if e['id'] != emp_id]
        escribir_json(EMPLEADORES_FILE, empleadores)
        
        # 4. Eliminar trabajos publicados por el empleador
        trabajos_eliminar_ids = [t['id'] for t in trabajos if t['empleador_id'] == emp_id]
        trabajos = [t for t in trabajos if t['empleador_id'] != emp_id]
        escribir_json(TRABAJOS_FILE, trabajos)
        
        # 5. Eliminar postulaciones relacionadas con los trabajos del empleador
        postulaciones = [p for p in postulaciones if p['empleador_id'] != emp_id and p['trabajo_id'] not in trabajos_eliminar_ids]
        escribir_json(POSTULACIONES_FILE, postulaciones)
        
        # 6. Eliminar trabajos activos del empleador
        trabajos_activos = [t for t in trabajos_activos if t['empleador_id'] != emp_id]
        escribir_json(TRABAJOS_ACTIVOS_FILE, trabajos_activos)
        
        # 7. Eliminar calificaciones dadas por el empleador
        calificaciones = [c for c in calificaciones if c['empleador_id'] != emp_id]
        escribir_json(CALIFICACIONES_FILE, calificaciones)
        
        # 8. Eliminar mensajes del empleador
        mensajes = [m for m in mensajes if m['de_user_id'] != emp_id and m['para_user_id'] != emp_id]
        escribir_json(MENSAJES_FILE, mensajes)
        
        # 9. Eliminar reportes donde el empleador es reportador o reportado
        reportes = [r for r in reportes if r['reportador_id'] != emp_id and r['reportado_id'] != emp_id]
        escribir_json(REPORTES_FILE, reportes)
        
        # 10. Eliminar alertas enviadas por el empleador (si es que puede enviar)
        # Normalmente solo admin envía alertas, pero por si acaso
        alertas = [a for a in alertas if a.get('admin_id') != emp_id]
        escribir_json(ALERTAS_FILE, alertas)
        
        flash(f'Empleador {empleador_eliminar["empresa"]} eliminado exitosamente. Se limpiaron todos sus trabajos y datos relacionados.', 'success')
        
    except Exception as e:
        print(f"Error eliminando empleador: {e}")
        flash('Error al eliminar el empleador', 'error')
    
    return redirect(url_for('admin_empleadores'))

# === SISTEMA DE MENSAJERÍA ===

@app.route('/mensajes')
def ver_mensajes():
    if 'user_id' not in session:
        return redirect(url_for('login_usuario'))
    
    try:
        mensajes = leer_json(MENSAJES_FILE)
        usuarios = leer_json(USUARIOS_FILE)
        empleadores = leer_json(EMPLEADORES_FILE)
        
        # Obtener conversaciones del usuario
        conversaciones = {}
        
        for mensaje in mensajes:
            if mensaje['de_user_id'] == session['user_id'] or mensaje['para_user_id'] == session['user_id']:
                otro_user_id = mensaje['para_user_id'] if mensaje['de_user_id'] == session['user_id'] else mensaje['de_user_id']
                
                if otro_user_id not in conversaciones:
                    # Buscar información del otro usuario
                    if session['user_type'] == 'usuario':
                        otro_user = next((e for e in empleadores if e['id'] == otro_user_id), None)
                        nombre = otro_user['empresa'] if otro_user else 'Usuario desconocido'
                    else:
                        otro_user = next((u for u in usuarios if u['id'] == otro_user_id), None)
                        nombre = f"{otro_user['nombres']} {otro_user['apellidos']}" if otro_user else 'Usuario desconocido'
                    
                    conversaciones[otro_user_id] = {
                        'user_id': otro_user_id,
                        'nombre': nombre,
                        'ultimo_mensaje': mensaje['mensaje'],
                        'fecha_ultimo': mensaje['fecha'],
                        'sin_leer': 0
                    }
        
        return render_template('mensajes.html', conversaciones=list(conversaciones.values()))
    
    except Exception as e:
        flash('Error al cargar los mensajes', 'error')
        return redirect(url_for('dashboard_usuario' if session['user_type'] == 'usuario' else 'dashboard_empleador'))

@app.route('/mensajes/<otro_user_id>', methods=['GET', 'POST'])
def ver_conversacion(otro_user_id):
    if 'user_id' not in session:
        return redirect(url_for('login_usuario'))
    
    try:
        if request.method == 'POST':
            # Enviar mensaje
            mensaje_texto = request.form['mensaje']
            
            if mensaje_texto.strip():
                mensajes = leer_json(MENSAJES_FILE)
                
                nuevo_mensaje = {
                    'id': str(len(mensajes) + 1),
                    'de_user_id': session['user_id'],
                    'para_user_id': otro_user_id,
                    'mensaje': mensaje_texto,
                    'fecha': datetime.now().isoformat(),
                    'leido': False
                }
                
                mensajes.append(nuevo_mensaje)
                escribir_json(MENSAJES_FILE, mensajes)
                
                return redirect(url_for('ver_conversacion', otro_user_id=otro_user_id))
        
        # Obtener mensajes de la conversación
        mensajes = leer_json(MENSAJES_FILE)
        conversacion = [m for m in mensajes if 
                       (m['de_user_id'] == session['user_id'] and m['para_user_id'] == otro_user_id) or 
                       (m['de_user_id'] == otro_user_id and m['para_user_id'] == session['user_id'])]
        
        # Marcar mensajes como leídos
        for mensaje in conversacion:
            if mensaje['para_user_id'] == session['user_id'] and not mensaje['leido']:
                mensaje['leido'] = True
        
        escribir_json(MENSAJES_FILE, mensajes)
        
        # Obtener información del otro usuario
        usuarios = leer_json(USUARIOS_FILE)
        empleadores = leer_json(EMPLEADORES_FILE)
        
        if session['user_type'] == 'usuario':
            otro_user = next((e for e in empleadores if e['id'] == otro_user_id), None)
            nombre_otro = otro_user['empresa'] if otro_user else 'Empleador'
        else:
            otro_user = next((u for u in usuarios if u['id'] == otro_user_id), None)
            nombre_otro = f"{otro_user['nombres']} {otro_user['apellidos']}" if otro_user else 'Usuario'
        
        return render_template('conversacion.html', 
                             mensajes=conversacion, 
                             otro_user_id=otro_user_id,
                             nombre_otro=nombre_otro)
    
    except Exception as e:
        flash('Error al cargar la conversación', 'error')
        return redirect(url_for('ver_mensajes'))

@app.route('/iniciar-chat/<user_id>')
def iniciar_chat(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login_usuario'))
    
    try:
        # Verificar que existe un trabajo activo entre estos usuarios (para empleadores)
        if session['user_type'] == 'empleador':
            trabajos_activos = leer_json(TRABAJOS_ACTIVOS_FILE)
            trabajo_activo = next((t for t in trabajos_activos if 
                                  t['usuario_id'] == user_id and 
                                  t['empleador_id'] == session['user_id'] and
                                  t['estado'] == 'activo'), None)
            
            if not trabajo_activo:
                flash('Solo puedes chatear con estudiantes que tengas en trabajos activos', 'error')
                return redirect(url_for('empleador_trabajos_activos'))
        
        # Para usuarios, verificar que tienen trabajo activo con el empleador
        elif session['user_type'] == 'usuario':
            trabajos_activos = leer_json(TRABAJOS_ACTIVOS_FILE)
            trabajo_activo = next((t for t in trabajos_activos if 
                                  t['empleador_id'] == user_id and 
                                  t['usuario_id'] == session['user_id'] and
                                  t['estado'] == 'activo'), None)
            
            if not trabajo_activo:
                flash('Solo puedes chatear con empleadores que te hayan contratado', 'error')
                return redirect(url_for('dashboard_usuario'))
        
        return redirect(url_for('ver_conversacion', otro_user_id=user_id))
    
    except Exception as e:
        flash('Error al iniciar el chat', 'error')
        return redirect(url_for('dashboard_usuario' if session['user_type'] == 'usuario' else 'dashboard_empleador'))

# === SISTEMA DE ALERTAS DEL ADMIN ===

@app.route('/admin/enviar-alerta', methods=['GET', 'POST'])
def admin_enviar_alerta():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))
    
    if request.method == 'POST':
        alerta = {
            'id': str(len(leer_json(ALERTAS_FILE)) + 1),
            'titulo': request.form['titulo'],
            'mensaje': request.form['mensaje'],
            'tipo': request.form['tipo'],
            'prioridad': request.form['prioridad'],
            'destinatario': request.form['destinatario'],
            'fecha_expiracion': request.form.get('fecha_expiracion', ''),
            'fecha_envio': datetime.now().isoformat(),
            'admin_id': session['user_id'],
            'estado': 'activa'
        }
        
        alertas = leer_json(ALERTAS_FILE)
        alertas.append(alerta)
        escribir_json(ALERTAS_FILE, alertas)
        
        flash('Alerta enviada exitosamente', 'success')
        return redirect(url_for('dashboard_admin'))
    
    # Pasar la fecha actual al template
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    return render_template('admin_enviar_alerta.html', fecha_actual=fecha_actual)

@app.route('/alertas')
def ver_alertas():
    if 'user_id' not in session:
        return redirect(url_for('login_usuario'))
    
    try:
        limpiar_alertas_expiradas()
        alertas = leer_json(ALERTAS_FILE)
        
        # Filtrar alertas relevantes para el usuario
        if session['user_type'] == 'usuario':
            alertas_relevantes = [a for a in alertas if a['destinatario'] in ['todos', 'usuarios']]
        else:
            alertas_relevantes = [a for a in alertas if a['destinatario'] in ['todos', 'empleadores']]
        
        return render_template('alertas.html', alertas=alertas_relevantes)
    
    except Exception as e:
        flash('Error al cargar las alertas', 'error')
        return redirect(url_for('dashboard_usuario' if session['user_type'] == 'usuario' else 'dashboard_empleador'))

@app.route('/admin/alertas')
def admin_ver_alertas():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))
    
    alertas = leer_json(ALERTAS_FILE)
    return render_template('admin_alertas.html', alertas=alertas)

# ===== GESTIÓN DE ALERTAS PARA USUARIOS/EMPLEADORES =====

@app.route('/alerta/<alerta_id>/marcar-leida')
def marcar_alerta_leida(alerta_id):
    if 'user_id' not in session:
        return redirect(url_for('login_usuario'))
    
    try:
        alertas = leer_json(ALERTAS_FILE)
        
        # Buscar la alerta y actualizar
        for i, alerta in enumerate(alertas):
            if alerta['id'] == alerta_id:
                # Si no existe el campo 'leida_por', crearlo
                if 'leida_por' not in alertas[i]:
                    alertas[i]['leida_por'] = []
                
                # Agregar el usuario actual a la lista de quienes han leído
                if session['user_id'] not in alertas[i]['leida_por']:
                    alertas[i]['leida_por'].append(session['user_id'])
                
                break
        
        escribir_json(ALERTAS_FILE, alertas)
        
        # Redirigir de vuelta a donde estaba el usuario
        referer = request.headers.get('Referer')
        if referer:
            return redirect(referer)
        else:
            return redirect(url_for('dashboard_usuario' if session['user_type'] == 'usuario' else 'dashboard_empleador'))
    
    except Exception as e:
        flash('Error al marcar la alerta como leída', 'error')
        return redirect(url_for('dashboard_usuario' if session['user_type'] == 'usuario' else 'dashboard_empleador'))

@app.route('/alertas/descartar-todas')
def descartar_todas_alertas():
    if 'user_id' not in session:
        return redirect(url_for('login_usuario'))
    
    try:
        alertas = leer_json(ALERTAS_FILE)
        
        # Marcar todas las alertas relevantes como leídas por este usuario
        for i, alerta in enumerate(alertas):
            # Verificar si la alerta es relevante para este usuario
            if ((session['user_type'] == 'usuario' and alerta['destinatario'] in ['todos', 'usuarios']) or
                (session['user_type'] == 'empleador' and alerta['destinatario'] in ['todos', 'empleadores'])):
                
                if 'leida_por' not in alertas[i]:
                    alertas[i]['leida_por'] = []
                
                if session['user_id'] not in alertas[i]['leida_por']:
                    alertas[i]['leida_por'].append(session['user_id'])
        
        escribir_json(ALERTAS_FILE, alertas)
        
        # Redirigir de vuelta
        referer = request.headers.get('Referer')
        if referer:
            return redirect(referer)
        else:
            return redirect(url_for('dashboard_usuario' if session['user_type'] == 'usuario' else 'dashboard_empleador'))
    
    except Exception as e:
        flash('Error al descartar las alertas', 'error')
        return redirect(url_for('dashboard_usuario' if session['user_type'] == 'usuario' else 'dashboard_empleador'))

# === MEJORAS PARA EL ADMIN ===

@app.route('/admin/usuario/<user_id>')
def admin_ver_usuario(user_id):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))
    
    try:
        usuarios = leer_json(USUARIOS_FILE)
        usuario = next((u for u in usuarios if u['id'] == user_id), None)
        
        if not usuario:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('admin_usuarios'))
        
        # Obtener postulaciones del usuario
        postulaciones = leer_json(POSTULACIONES_FILE)
        trabajos = leer_json(TRABAJOS_FILE)
        empleadores = leer_json(EMPLEADORES_FILE)
        
        postulaciones_usuario = []
        for postulacion in postulaciones:
            if postulacion['usuario_id'] == user_id:
                trabajo = next((t for t in trabajos if t['id'] == postulacion['trabajo_id']), None)
                if trabajo:
                    empleador = next((e for e in empleadores if e['id'] == trabajo['empleador_id']), None)
                    postulacion_con_info = postulacion.copy()
                    postulacion_con_info['trabajo_info'] = trabajo
                    postulacion_con_info['empleador_info'] = empleador
                    postulaciones_usuario.append(postulacion_con_info)
        
        return render_template('admin_detalle_usuario.html', 
                             usuario=usuario, 
                             postulaciones=postulaciones_usuario)
    
    except Exception as e:
        flash('Error al cargar los detalles del usuario', 'error')
        return redirect(url_for('admin_usuarios'))

@app.route('/admin/empleador/<emp_id>')
def admin_ver_empleador(emp_id):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))
    
    try:
        empleadores = leer_json(EMPLEADORES_FILE)
        empleador = next((e for e in empleadores if e['id'] == emp_id), None)
        
        if not empleador:
            flash('Empleador no encontrado', 'error')
            return redirect(url_for('admin_empleadores'))
        
        # Obtener trabajos del empleador
        trabajos = leer_json(TRABAJOS_FILE)
        trabajos_empleador = [t for t in trabajos if t['empleador_id'] == emp_id]
        
        # Obtener postulaciones para estos trabajos
        postulaciones = leer_json(POSTULACIONES_FILE)
        usuarios = leer_json(USUARIOS_FILE)
        
        # Estadísticas
        total_postulaciones = len([p for p in postulaciones if p['empleador_id'] == emp_id])
        postulaciones_aceptadas = len([p for p in postulaciones if p['empleador_id'] == emp_id and p['estado'] == 'aceptado'])
        
        return render_template('admin_detalle_empleador.html', 
                             empleador=empleador, 
                             trabajos=trabajos_empleador,
                             postulaciones=postulaciones,
                             usuarios=usuarios,
                             total_postulaciones=total_postulaciones,
                             postulaciones_aceptadas=postulaciones_aceptadas)
    
    except Exception as e:
        flash('Error al cargar los detalles del empleador', 'error')
        return redirect(url_for('admin_empleadores'))

# DASHBOARD ADMIN MEJORADO
@app.route('/dashboard/admin')
def dashboard_admin():
    if 'user_type' not in session or session['user_type'] != 'admin':
        flash('Debes iniciar sesión como administrador', 'error')
        return redirect(url_for('login_admin'))
    
    try:
        usuarios = leer_json(USUARIOS_FILE)
        empleadores = leer_json(EMPLEADORES_FILE)
        trabajos = leer_json(TRABAJOS_FILE)
        reportes = leer_json(REPORTES_FILE)
        postulaciones = leer_json(POSTULACIONES_FILE)
        alertas = leer_json(ALERTAS_FILE)
        
        # Estadísticas
        trabajos_activos = len([t for t in trabajos if t.get('estado') == 'disponible'])
        postulaciones_pendientes = len([p for p in postulaciones if p.get('estado') == 'pendiente'])
        reportes_pendientes = len([r for r in reportes if r.get('estado') == 'pendiente'])  # NUEVO
        
        return render_template('dashboard_admin.html', 
                             usuarios=usuarios, 
                             empleadores=empleadores, 
                             trabajos=trabajos, 
                             reportes=reportes,
                             postulaciones=postulaciones,
                             alertas=alertas,
                             trabajos_activos=trabajos_activos,
                             postulaciones_pendientes=postulaciones_pendientes,
                             reportes_pendientes=reportes_pendientes)  # NUEVO
    
    except Exception as e:
        flash('Error al cargar el dashboard de administración', 'error')
        return redirect(url_for('login_admin'))

# === SISTEMA DE CALIFICACIONES ===

# Ruta para que empleadores califiquen usuarios - MEJORADA
@app.route('/empleador/calificar/<trabajo_activo_id>', methods=['GET', 'POST'])
def calificar_usuario(trabajo_activo_id):
    if 'user_id' not in session or session['user_type'] != 'empleador':
        return redirect(url_for('login_empleador'))
    
    trabajos_activos = leer_json(TRABAJOS_ACTIVOS_FILE)
    trabajo_activo = next((t for t in trabajos_activos if t['id'] == trabajo_activo_id and t['empleador_id'] == session['user_id']), None)
    
    if not trabajo_activo:
        flash('Trabajo activo no encontrado o no tienes permisos', 'error')
        return redirect(url_for('empleador_trabajos_activos'))
    
    # Verificar que el trabajo está activo
    if trabajo_activo['estado'] != 'activo':
        flash('Este trabajo ya ha sido finalizado y calificado', 'error')
        return redirect(url_for('empleador_trabajos_activos'))
    
    usuarios = leer_json(USUARIOS_FILE)
    usuario = next((u for u in usuarios if u['id'] == trabajo_activo['usuario_id']), None)
    
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('empleador_trabajos_activos'))
    
    if request.method == 'POST':
        # Verificar si ya existe calificación para este trabajo
        calificaciones = leer_json(CALIFICACIONES_FILE)
        calificacion_existente = next((c for c in calificaciones if c['trabajo_activo_id'] == trabajo_activo_id), None)
        
        if calificacion_existente:
            flash('Ya has calificado este trabajo anteriormente', 'error')
            return redirect(url_for('empleador_trabajos_activos'))
        
        calificacion_data = {
            'id': str(len(calificaciones) + 1),
            'trabajo_activo_id': trabajo_activo_id,
            'empleador_id': session['user_id'],
            'usuario_id': trabajo_activo['usuario_id'],
            'puntuacion': int(request.form['puntuacion']),
            'comentario': request.form['comentario'],
            'fecha_calificacion': datetime.now().isoformat(),
            'trabajo_titulo': trabajo_activo['titulo']
        }
        
        # Guardar calificación
        calificaciones.append(calificacion_data)
        escribir_json(CALIFICACIONES_FILE, calificaciones)
        
        # Actualizar trabajo activo a "finalizado"
        for i, ta in enumerate(trabajos_activos):
            if ta['id'] == trabajo_activo_id:
                trabajos_activos[i]['estado'] = 'finalizado'
                trabajos_activos[i]['fecha_finalizacion'] = datetime.now().isoformat()
                break
        
        escribir_json(TRABAJOS_ACTIVOS_FILE, trabajos_activos)
        
        flash('Calificación enviada exitosamente. El trabajo ha sido marcado como finalizado.', 'success')
        return redirect(url_for('empleador_trabajos_activos'))
    
    return render_template('calificar_usuario.html', 
                         trabajo_activo=trabajo_activo, 
                         usuario=usuario)

@app.route('/usuario/mis-calificaciones')
def ver_mis_calificaciones():
    if 'user_id' not in session or session['user_type'] != 'usuario':
        return redirect(url_for('login_usuario'))
    
    try:
        calificaciones = leer_json(CALIFICACIONES_FILE)
        empleadores = leer_json(EMPLEADORES_FILE)
        trabajos_activos = leer_json(TRABAJOS_ACTIVOS_FILE)
        
        mis_calificaciones = []
        for calificacion in calificaciones:
            if calificacion['usuario_id'] == session['user_id']:
                empleador = next((e for e in empleadores if e['id'] == calificacion['empleador_id']), None)
                trabajo_activo = next((t for t in trabajos_activos if t['id'] == calificacion['trabajo_activo_id']), None)
                
                if empleador and trabajo_activo:
                    calificacion_con_info = calificacion.copy()
                    calificacion_con_info['empleador_info'] = empleador
                    calificacion_con_info['trabajo_info'] = trabajo_activo
                    mis_calificaciones.append(calificacion_con_info)
        
        # Calcular promedio
        promedio = 0
        if mis_calificaciones:
            promedio = sum(c['puntuacion'] for c in mis_calificaciones) / len(mis_calificaciones)
        
        return render_template('mis_calificaciones.html', 
                             calificaciones=mis_calificaciones, 
                             promedio=promedio)
    
    except Exception as e:
        flash('Error al cargar las calificaciones', 'error')
        return redirect(url_for('dashboard_usuario'))

# === SISTEMA DE REPORTES Y DENUNCIAS ===

@app.route('/reportar/<tipo_usuario>/<user_id>', methods=['GET', 'POST'])
def crear_reporte(tipo_usuario, user_id):
    if 'user_id' not in session:
        return redirect(url_for('login_usuario'))
    
    try:
        # Obtener información del usuario a reportar
        usuarios = leer_json(USUARIOS_FILE)
        empleadores = leer_json(EMPLEADORES_FILE)
        
        usuario_reportado = None
        if tipo_usuario == 'usuario':
            usuario_reportado = next((u for u in usuarios if u['id'] == user_id), None)
            nombre_reportado = f"{usuario_reportado['nombres']} {usuario_reportado['apellidos']}" if usuario_reportado else "Usuario"
        else:
            usuario_reportado = next((e for e in empleadores if e['id'] == user_id), None)
            nombre_reportado = usuario_reportado['empresa'] if usuario_reportado else "Empleador"
        
        if not usuario_reportado:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('dashboard_usuario' if session['user_type'] == 'usuario' else 'dashboard_empleador'))
        
        if request.method == 'POST':
            reporte = {
                'id': str(len(leer_json(REPORTES_FILE)) + 1),
                'reportador_id': session['user_id'],
                'reportador_tipo': session['user_type'],
                'reportado_id': user_id,
                'reportado_tipo': tipo_usuario,
                'reportado_nombre': nombre_reportado,
                'titulo': request.form['titulo'],
                'descripcion': request.form['descripcion'],
                'categoria': request.form['categoria'],
                'prioridad': request.form['prioridad'],
                'estado': 'pendiente',  # pendiente, revisado, resuelto
                'fecha_reporte': datetime.now().isoformat(),
                'respuesta_admin': None,
                'fecha_respuesta': None,
                'admin_id': None
            }
            
            reportes = leer_json(REPORTES_FILE)
            reportes.append(reporte)
            escribir_json(REPORTES_FILE, reportes)
            
            flash('Reporte enviado exitosamente. El administrador lo revisará pronto.', 'success')
            return redirect(url_for('dashboard_usuario' if session['user_type'] == 'usuario' else 'dashboard_empleador'))
        
        return render_template('crear_reporte.html', 
                             tipo_usuario=tipo_usuario, 
                             user_id=user_id,
                             usuario_reportado=nombre_reportado)
    
    except Exception as e:
        flash('Error al crear el reporte', 'error')
        return redirect(url_for('dashboard_usuario' if session['user_type'] == 'usuario' else 'dashboard_empleador'))

@app.route('/mis-reportes')
def mis_reportes():
    if 'user_id' not in session:
        return redirect(url_for('login_usuario'))
    
    try:
        reportes = leer_json(REPORTES_FILE)
        mis_reportes_lista = [r for r in reportes if r['reportador_id'] == session['user_id']]
        
        # Ordenar por fecha (más recientes primero)
        mis_reportes_lista.sort(key=lambda x: x['fecha_reporte'], reverse=True)
        
        return render_template('mis_reportes.html', reportes=mis_reportes_lista)
    
    except Exception as e:
        flash('Error al cargar los reportes', 'error')
        return redirect(url_for('dashboard_usuario' if session['user_type'] == 'usuario' else 'dashboard_empleador'))

@app.route('/admin/reportes')
def admin_reportes():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))
    
    try:
        reportes = leer_json(REPORTES_FILE)
        
        # Ordenar por fecha (más recientes primero)
        reportes.sort(key=lambda x: x['fecha_reporte'], reverse=True)
        
        # Contar reportes pendientes para la notificación
        reportes_pendientes = len([r for r in reportes if r['estado'] == 'pendiente'])
        
        # Obtener estadísticas
        estadisticas = {
            'total': len(reportes),
            'pendientes': reportes_pendientes,
            'revisados': len([r for r in reportes if r['estado'] == 'revisado']),
            'resueltos': len([r for r in reportes if r['estado'] == 'resuelto'])
        }
        
        return render_template('admin_reportes.html', 
                             reportes=reportes, 
                             reportes_pendientes=reportes_pendientes,
                             estadisticas=estadisticas)
    
    except Exception as e:
        flash('Error al cargar los reportes', 'error')
        return redirect(url_for('dashboard_admin'))

@app.route('/admin/reporte/<reporte_id>/responder', methods=['GET', 'POST'])
def admin_responder_reporte(reporte_id):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))
    
    try:
        reportes = leer_json(REPORTES_FILE)
        reporte = next((r for r in reportes if r['id'] == reporte_id), None)
        
        if not reporte:
            flash('Reporte no encontrado', 'error')
            return redirect(url_for('admin_reportes'))
        
        if request.method == 'POST':
            respuesta = request.form['respuesta']
            estado = request.form['estado']
            
            for i, r in enumerate(reportes):
                if r['id'] == reporte_id:
                    reportes[i]['respuesta_admin'] = respuesta
                    reportes[i]['estado'] = estado
                    reportes[i]['fecha_respuesta'] = datetime.now().isoformat()
                    reportes[i]['admin_id'] = session['user_id']
                    break
            
            escribir_json(REPORTES_FILE, reportes)
            flash('Respuesta enviada exitosamente', 'success')
            return redirect(url_for('admin_reportes'))
        
        return render_template('admin_responder_reporte.html', reporte=reporte)
    
    except Exception as e:
        flash('Error al responder al reporte', 'error')
        return redirect(url_for('admin_reportes'))

@app.route('/admin/reporte/<reporte_id>/eliminar')
def admin_eliminar_reporte(reporte_id):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))
    
    try:
        reportes = leer_json(REPORTES_FILE)
        reportes = [r for r in reportes if r['id'] != reporte_id]
        escribir_json(REPORTES_FILE, reportes)
        
        flash('Reporte eliminado exitosamente', 'success')
        return redirect(url_for('admin_reportes'))
    
    except Exception as e:
        flash('Error al eliminar el reporte', 'error')
        return redirect(url_for('admin_reportes'))

# Ruta para recrear datos de prueba (solo admin)
@app.route('/crear-datos-prueba')
def crear_datos_prueba_route():
    if 'user_type' not in session or session['user_type'] != 'admin':
        flash('No tienes permisos para esta acción', 'error')
        return redirect(url_for('login_admin'))
    
    crear_datos_prueba()
    flash('Datos de prueba recreados exitosamente!', 'success')
    return redirect(url_for('dashboard_admin'))

# Cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    inicializar_archivos()
    app.run(debug=True)