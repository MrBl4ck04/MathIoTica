# Importa las librerías necesarias para la aplicación Flask, manejar plantillas, JSON y solicitudes
from flask import Flask, render_template, jsonify, request

# Importa el conector de MySQL para Python
import mysql.connector

# Importa los módulos de Plotly para generar gráficos
import plotly.graph_objs as go
import plotly.io as pio

# Importa la clase 'datetime' para manejar fechas y horas
from datetime import datetime

# Inicializa la aplicación Flask
app = Flask(__name__)

# Función para establecer la conexión con la base de datos MySQL
def conectar():
    # Se establece la conexión con la base de datos utilizando los parámetros de host, usuario, contraseña y nombre de la base de datos
    conexion = mysql.connector.connect(
        host="192.168.243.2",  # Dirección del servidor de la base de datos (local)
        user="Franz",       # Usuario de la base de datos (cambiar según tu configuración)
        password="",       # Contraseña del usuario (cambiar según tu configuración)
        database="mathiotica"  # Nombre de la base de datos
    )
    return conexion  # Retorna la conexión a la base de datos

# Define la ruta para la página principal de la aplicación
@app.route('/')
def index():
    # Renderiza la plantilla 'index.html' que corresponde a la interfaz principal
    return render_template('index.html')

# Define una ruta para obtener los nombres y cursos disponibles desde la base de datos
@app.route('/obtener_filtros', methods=['GET'])
def obtener_filtros():
    # Conecta a la base de datos llamando a la función 'conectar'
    conexion = conectar()
    cursor = conexion.cursor()  # Crea un cursor para ejecutar consultas SQL

    # Consulta SQL que obtiene los nombres y cursos únicos desde la tabla 'juegos'
    cursor.execute("SELECT DISTINCT nombre, curso FROM juegos")
    resultados = cursor.fetchall()  # Almacena todos los resultados de la consulta

    # Extrae los nombres únicos de los resultados y los convierte en una lista
    nombres = list(set([fila[0] for fila in resultados]))
    # Extrae los cursos únicos de los resultados y los convierte en una lista
    cursos = list(set([fila[1] for fila in resultados]))

    # Cierra el cursor y la conexión a la base de datos
    cursor.close()
    conexion.close()

    # Devuelve los nombres y cursos en formato JSON, para ser utilizados en la interfaz
    return jsonify({"nombres": nombres, "cursos": cursos})

# Define una ruta para obtener los datos de las gráficas según los filtros aplicados
@app.route('/datos_grafico', methods=['GET'])
def datos_grafico():
    # Obtiene los parámetros del filtro desde la solicitud (nombre, curso, resuelto, fecha de inicio y fecha de fin)
    filtro_nombre = request.args.get('nombre', default=None, type=str)
    filtro_curso = request.args.get('curso', default=None, type=str)
    filtro_resuelto = request.args.get('resuelto', default=None, type=str)
    filtro_fecha_inicio = request.args.get('fecha_inicio', default=None, type=str)
    filtro_fecha_fin = request.args.get('fecha_fin', default=None, type=str)

    # Conecta a la base de datos llamando a la función 'conectar'
    conexion = conectar()
    cursor = conexion.cursor()  # Crea un cursor para ejecutar consultas SQL

    # Define la consulta base para seleccionar datos de la tabla 'juegos'
    query = "SELECT nombre, puntuacion, tiempo, operacion, logrado, fecha FROM juegos WHERE 1=1"
    parametros = []  # Lista para almacenar los parámetros que se usarán en la consulta

    # Aplica el filtro por nombre si está seleccionado y no es "todos"
    if filtro_nombre and filtro_nombre != 'todos':
        query += " AND nombre = %s"  # Agrega la condición SQL para filtrar por nombre
        parametros.append(filtro_nombre)  # Añade el valor del filtro a los parámetros

    # Aplica el filtro por curso si está seleccionado y no es "todos"
    if filtro_curso and filtro_curso != 'todos':
        query += " AND curso = %s"  # Agrega la condición SQL para filtrar por curso
        parametros.append(filtro_curso)  # Añade el valor del filtro a los parámetros

    # Aplica el filtro para ejercicios resueltos o no resueltos
    if filtro_resuelto == 'resuelto':
        query += " AND logrado = 1"  # 1 indica que el ejercicio fue resuelto
    elif filtro_resuelto == 'no_resuelto':
        query += " AND logrado = 0"  # 0 indica que el ejercicio no fue resuelto

    # Aplica el filtro por rango de fechas, si se proporciona una fecha de inicio
    if filtro_fecha_inicio:
        query += " AND fecha >= %s"  # Condición SQL para filtrar por fecha de inicio
        parametros.append(filtro_fecha_inicio)  # Añade la fecha de inicio a los parámetros

    # Aplica el filtro por fecha de fin, si se proporciona
    if filtro_fecha_fin:
        query += " AND fecha <= %s"  # Condición SQL para filtrar por fecha de fin
        parametros.append(filtro_fecha_fin)  # Añade la fecha de fin a los parámetros

    # Ejecuta la consulta SQL con los parámetros seleccionados
    cursor.execute(query, parametros)
    resultados = cursor.fetchall()  # Obtiene todos los resultados de la consulta

    # Cierra el cursor y la conexión a la base de datos
    cursor.close()
    conexion.close()

    # Inicializa listas vacías para almacenar los datos obtenidos
    nombres, puntuaciones, tiempos, operaciones = [], [], [], []

    # Procesa cada fila de los resultados obtenidos y llena las listas correspondientes
    for fila in resultados:
        nombres.append(fila[0])  # Nombre del jugador
        puntuaciones.append(fila[1])  # Puntuación obtenida
        tiempos.append(fila[2])  # Tiempo tomado
        operaciones.append(fila[3])  # Tipo de operación matemática (suma, resta, etc.)

    # Llama a la función 'crear_graficas' para generar los gráficos con los datos obtenidos
        graficas = crear_graficas(puntuaciones, tiempos, operaciones, nombres)

    # Devuelve los gráficos en formato JSON
    return jsonify(graficas)

# Función para generar las gráficas utilizando Plotly
# Función para generar las gráficas utilizando Plotly
# Función para generar las gráficas utilizando Plotly
def crear_graficas(puntuaciones, tiempos, operaciones, nombres):
    # Diccionario para almacenar las puntuaciones y tiempos por estudiante
    puntuaciones_por_estudiante = {}
    tiempos_por_estudiante = {}
    
    # Agrupa las puntuaciones y tiempos por estudiante
    for i, nombre in enumerate(nombres):
        if nombre not in puntuaciones_por_estudiante:
            puntuaciones_por_estudiante[nombre] = []
            tiempos_por_estudiante[nombre] = []
        puntuaciones_por_estudiante[nombre].append(puntuaciones[i])
        tiempos_por_estudiante[nombre].append(tiempos[i].total_seconds())  # Convierte timedelta a segundos
    
    # Listas para almacenar los nombres de estudiantes y sus promedios
    nombres_estudiantes = []
    promedios_estudiantes_puntuacion = []
    promedios_estudiantes_tiempo = []
    
    # Calcula el promedio de puntuación y tiempo por estudiante
    for nombre, puntuaciones in puntuaciones_por_estudiante.items():
        promedio_puntuacion = sum(puntuaciones) / len(puntuaciones) if puntuaciones else 0
        promedio_tiempo = sum(tiempos_por_estudiante[nombre]) / len(tiempos_por_estudiante[nombre]) if tiempos_por_estudiante[nombre] else 0
        nombres_estudiantes.append(nombre)
        promedios_estudiantes_puntuacion.append(promedio_puntuacion)
        promedios_estudiantes_tiempo.append(promedio_tiempo)
    
    # Gráfico de barras que muestra la puntuación promedio por estudiante
    grafico1 = go.Bar(
        x=nombres_estudiantes,  # Nombres de los estudiantes en el eje X
        y=promedios_estudiantes_puntuacion,  # Puntuación promedio en el eje Y
        name='Puntuación Promedio por Estudiante'  # Nombre del gráfico
    )
    
    # Gráfico de barras que muestra el tiempo promedio por estudiante
    grafico2 = go.Bar(
        x=nombres_estudiantes,  # Nombres de los estudiantes en el eje X
        y=promedios_estudiantes_tiempo,  # Tiempo promedio en segundos en el eje Y
        name='Tiempo Promedio por Estudiante (segundos)'  # Nombre del gráfico
    )
    

    # Diccionario para contar la distribución de operaciones (suma, resta, multiplicación, división)
    operaciones_dict = {"+": 0, "-": 0, "*": 0, "/": 0}
    for operacion in operaciones:
        operaciones_dict[operacion] += 1  # Incrementa el contador de cada operación

    # Gráfico circular que muestra la distribución de operaciones
    grafico3 = go.Pie(
        labels=list(operaciones_dict.keys()),   # Etiquetas de las operaciones
        values=list(operaciones_dict.values()), # Cantidad de veces que se usó cada operación
        name='Distribución de Operaciones Matemáticas'  # Nombre del gráfico
    )

    # Define el diseño general de los gráficos
    layout = go.Layout(
        title="Dashboard de Juego - Análisis de Rendimiento",  # Título del dashboard
        xaxis_title="Estudiantes",                # Título del eje X
    )

    # Crea la figura con los gráficos y el layout, y devuelve el resultado en formato JSON
    fig = go.Figure(data=[grafico1, grafico2, grafico3], layout=layout)
    return pio.to_json(fig)  # Convierte la figura en JSON para su envío al frontend

# Punto de entrada de la aplicación
if __name__ == '__main__':
    # Ejecuta la aplicación Flask en modo de depuración
    app.run(debug=True)
