import json
import os

def leer_json_debug(archivo):
    """Función para debuggear archivos JSON"""
    print(f"\n=== DEBUG: Verificando {archivo} ===")
    
    if not os.path.exists(archivo):
        print(f"❌ El archivo {archivo} NO existe")
        return None
    
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read().strip()
            print(f"✅ Archivo existe - Tamaño: {len(contenido)} caracteres")
            
            if not contenido:
                print("⚠️ Archivo está vacío")
                return []
            
            datos = json.loads(contenido)
            print(f"✅ JSON válido - {len(datos)} registros")
            return datos
            
    except Exception as e:
        print(f"❌ Error leyendo JSON: {e}")
        return None

def verificar_empleador(empleador_id):
    """Verificar si un empleador existe y tiene datos correctos"""
    print(f"\n=== DEBUG: Verificando empleador ID {empleador_id} ===")
    
    # Verificar archivo de empleadores
    empleadores = leer_json_debug('data/empleadores.json')
    if empleadores is None:
        return False
    
    empleador = next((e for e in empleadores if e.get('id') == empleador_id), None)
    
    if not empleador:
        print(f"❌ Empleador con ID {empleador_id} NO encontrado")
        return False
    
    print(f"✅ Empleador encontrado: {empleador.get('empresa', 'Sin nombre')}")
    print(f"   ID: {empleador.get('id')}")
    print(f"   Email: {empleador.get('email')}")
    
    # Verificar que tenga los campos necesarios
    campos_requeridos = ['id', 'empresa', 'email', 'ruc']
    for campo in campos_requeridos:
        if campo not in empleador:
            print(f"⚠️  Falta campo requerido: {campo}")
    
    return True

def verificar_archivos_relacionados(empleador_id):
    """Verificar archivos relacionados con el empleador"""
    print(f"\n=== DEBUG: Verificando archivos relacionados ===")
    
    archivos = [
        'data/trabajos.json',
        'data/trabajos_activos.json', 
        'data/postulaciones.json',
        'data/alertas.json'
    ]
    
    for archivo in archivos:
        datos = leer_json_debug(archivo)
        if datos is not None:
            # Contar registros relacionados con este empleador
            if 'trabajos' in archivo:
                relacionados = [t for t in datos if t.get('empleador_id') == empleador_id]
                print(f"   Trabajos del empleador: {len(relacionados)}")
            elif 'trabajos_activos' in archivo:
                relacionados = [t for t in datos if t.get('empleador_id') == empleador_id]
                print(f"   Trabajos activos: {len(relacionados)}")
            elif 'postulaciones' in archivo:
                relacionados = [p for p in datos if p.get('empleador_id') == empleador_id]
                print(f"   Postulaciones: {len(relacionados)}")

def diagnostico_completo():
    """Diagnóstico completo del sistema"""
    print("🚀 INICIANDO DIAGNÓSTICO DEL DASHBOARD EMPLEADOR")
    print("=" * 50)
    
    # Verificar que la carpeta data existe
    if not os.path.exists('data'):
        print("❌ La carpeta 'data' NO existe")
        return
    
    print("✅ Carpeta 'data' existe")
    
    # Listar archivos en data
    archivos_data = os.listdir('data')
    print(f"📁 Archivos en data: {archivos_data}")
    
    # Verificar empleadores
    empleadores = leer_json_debug('data/empleadores.json')
    if empleadores:
        print(f"\n📊 Total empleadores en sistema: {len(empleadores)}")
        for i, emp in enumerate(empleadores[:3]):  # Mostrar primeros 3
            print(f"   {i+1}. {emp.get('empresa', 'Sin nombre')} (ID: {emp.get('id')})")
    
    # Si hay empleadores, verificar el primero
    if empleadores and len(empleadores) > 0:
        primer_empleador_id = empleadores[0]['id']
        if verificar_empleador(primer_empleador_id):
            verificar_archivos_relacionados(primer_empleador_id)
    
    print("\n" + "=" * 50)
    print("🎯 SUGERENCIAS:")
    print("1. Si algún archivo JSON está corrupto, elimínalo y reinicia la app")
    print("2. Verifica que todos los archivos tengan formato JSON válido")
    print("3. Si los empleadores existen pero el dashboard falla, revisa la sesión")

if __name__ == "__main__":
    diagnostico_completo()