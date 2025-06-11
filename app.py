from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import os
import time
import numpy as np
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-me')
socketio = SocketIO(app)

# Variable global para almacenar la ruta del archivo seleccionado
selected_file_path = None
# Hilo y evento para monitorear archivos en tiempo real
monitor_thread = None
stop_event = None


def sanitize_filename(name):
    """Return a safe file name within the data directory or None if invalid."""
    if not isinstance(name, str):
        return None
    if os.path.isabs(name) or '..' in name or '/' in name or '\\' in name:
        return None
    return os.path.basename(name)

@app.route('/')
def index():
    """Renderiza la página principal de la aplicación.

    Returns
    -------
    str
        Plantilla HTML renderizada para el inicio.
    """
    return render_template('index.html')

@socketio.on('selected_file')
def handle_selected_file(json):
    """Procesa el evento de selección de archivo enviado por el cliente.

    Parameters
    ----------
    json : dict
        Datos recibidos que contienen el nombre del archivo y los parámetros
        experimentales.

    Returns
    -------
    None
        Inicia el monitoreo del archivo y no devuelve un valor explícito.
    """
    global selected_file_path, monitor_thread, stop_event
    # Guarda la ruta del archivo seleccionado
    filename = sanitize_filename(json.get('name'))
    if not filename:
        socketio.emit('error', {'message': 'Nombre de archivo inválido'})
        return
    selected_file_path = os.path.join('data', filename)
    print(f'Archivo seleccionado: {selected_file_path}')
    
    # Guardar los parámetros específicos
    sigma3 = json['sigma3']
    H0 = json['H0']
    D0 = json['D0']
    DH0 = json['DH0']
    DV0 = json['DV0']
    PP0 = json['PP0']
    
    # Detener el hilo anterior si está activo
    if stop_event is not None:
        stop_event.set()
    if monitor_thread is not None:
        monitor_thread.join()
    # Crear un nuevo evento y lanzar el hilo de monitoreo
    stop_event = threading.Event()
    monitor_thread = socketio.start_background_task(
        monitor_file, stop_event, sigma3=sigma3, H0=H0, D0=D0, DH0=DH0, DV0=DV0, PP0=PP0
    )

@socketio.on('load_static_files')
def handle_static_files(json):
    """Carga archivos estáticos y envía sus datos procesados al cliente.

    Parameters
    ----------
    json : dict
        Diccionario con las rutas de los archivos y parámetros asociados.

    Returns
    -------
    None
        Emite los datos leídos sin devolver un valor.
    """
    file_paths = json['file_paths']
    static_params = json['static_params']
    static_data = []
    for i, file_name in enumerate(file_paths):
        safe_name = sanitize_filename(file_name)
        if not safe_name:
            continue
        file_path = os.path.join('data', safe_name)
        params = static_params[i]
        data = read_static_file(file_path, params['sigma3'], params['H0'], params['D0'], params['DH0'], params['DV0'], params['PP0'])
        static_data.append({'file_path': safe_name, 'data': data})
    # Envía los datos estáticos al cliente
    socketio.emit('static_data', static_data)

def calculate_effective_pq(sigma3, H0, D0, DH0, DV0, PP0, displacement, force, volume, pressure):
    """Calcula los esfuerzos efectivos y valores derivados.

    Parameters
    ----------
    sigma3, H0, D0, DH0, DV0, PP0 : float
        Valores de referencia obtenidos durante la consolidación.
    displacement, force, volume, pressure : float
        Medidas tomadas durante la fase de corte.

    Returns
    -------
    dict | None
        Diccionario con desplazamiento, esfuerzo desviador, presiones y
        parámetros "p", "q" y su cociente. Si ``p`` es cero, ``qp`` se
        define como ``0.0`` para evitar la división por cero.
    """
    V0 = (D0 ** 2) * np.pi / 4 * H0  # Volumen inicial del especimen
    H_C = H0 - DH0 / 10              # Altura del especimen al final de la consolidación
    A_C = (V0 - DV0) / H_C           # Área del especimen al final de la consolidación
    e_1 = 0.1 * displacement / H_C   # Deformacion unitaria axial
    A = A_C / (1 - e_1)              # Área del especimen durante el corte
    esf_desv = (force / A) * 10000   # Esfuerzo desviador durante la etapa de corte
    u = pressure - PP0               # Variación de la presión de poros durante el corte
    sigma3_e = sigma3 - u            # Esfuerzo de confinamiento efectivo
    sigma1_e = esf_desv + sigma3_e   # Esfuerzo principal efectivo
    p = (sigma1_e + sigma3_e) / 2
    q = (sigma1_e - sigma3_e) / 2
    if p == 0:
        qp = 0.0
    else:
        qp = q / p                   # normalizado
    return {
        'displacement': displacement,
        'force': force,
        'volume': volume,
        'pressure': pressure,
        'esf_desv': esf_desv,
        'q': q,
        'p': p,
        'qp': qp
    }

def read_static_file(file_path, sigma3, H0, D0, DH0, DV0, PP0):
    """Lee un archivo de datos y calcula trayectorias de esfuerzos efectivos.

    Parameters
    ----------
    file_path : str
        Ruta al archivo CSV dentro de la carpeta de datos.
    sigma3, H0, D0, DH0, DV0, PP0 : float
        Valores utilizados para el cálculo de esfuerzos.

    Returns
    -------
    list of dict
        Lista de diccionarios con los valores calculados para cada fila.
    """
    data = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:  # Omitir la primera línea si es un encabezado
            values = line.split(',')
            try:
                displacement = float(values[4])
                force = float(values[3])
                volume = float(values[5])
                pressure = float(values[6])

                # Utilizar función para calcular trayectorias de esfuerzos efectivos
                calculated_data = calculate_effective_pq(sigma3, H0, D0, DH0, DV0, PP0, displacement, force, volume, pressure)
                data.append(calculated_data)              
            except ValueError as e:
                print(f'Error de conversión en la línea: {line} - {e}')
    return data

def monitor_file(stop_event, sigma3, H0, D0, DH0, DV0, PP0):
    """Monitorea en tiempo real el archivo seleccionado y emite nuevos datos.

    Parameters
    ----------
    stop_event : threading.Event
        Evento utilizado para detener el monitoreo.
    sigma3, H0, D0, DH0, DV0, PP0 : float
        Parámetros necesarios para el cálculo de esfuerzos.

    Returns
    -------
    None
        Función de ejecución continua sin valor de retorno.
    """
    global selected_file_path
    if not selected_file_path:
        print('Archivo no seleccionado o no encontrado.')
        return
    print(f'Monitoreando archivo: {selected_file_path}')
    current_size = 0
    while not stop_event.is_set():
        new_size = os.path.getsize(selected_file_path)
        if new_size > current_size:
            with open(selected_file_path, 'r') as f:
                f.seek(current_size)
                lines = f.readlines()
                for line in lines:
                    values = line.split(',')
                    if len(values) < 7 or not values[0].strip().isdigit():  # Ignorar líneas incorrectas o encabezados
                        continue
                    try:
                        displacement = float(values[4])
                        force = float(values[3])
                        volume = float(values[5])
                        pressure = float(values[6])

                        # Utiliza la función para calcular las trayectorias de esfuerzos efectivos
                        data = calculate_effective_pq(sigma3, H0, D0, DH0, DV0, PP0, displacement, force, volume, pressure)

                        print(f'Emitiendo datos: {data}')
                        socketio.emit('new_data', data)
                    except ValueError as e:
                        print(f'Error de conversión en la línea: {line} - {e}')
            current_size = new_size
        time.sleep(1)

if __name__ == '__main__':
    socketio.run(app, debug=True)
