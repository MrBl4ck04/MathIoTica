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
    graficas = crear_graficas(puntuaciones, tiempos, operaciones)

    # Devuelve los gráficos en formato JSON
    return jsonify(graficas)

# Función para generar las gráficas utilizando Plotly
def crear_graficas(puntuaciones, tiempos, operaciones):
    # Calcula la puntuación promedio
    puntuacion_promedio = sum(puntuaciones) / len(puntuaciones) if puntuaciones else 0

    # Gráfico de barras que muestra la puntuación promedio
    grafico1 = go.Bar(
        x=['Puntuación Promedio'],  # Etiqueta del eje X
        y=[puntuacion_promedio],    # Valor de la puntuación promedio
        name='Puntuación Promedio'  # Nombre del gráfico
    )

    # Gráfico de barras que muestra el número total de ejercicios resueltos
    grafico2 = go.Bar(
        x=['Ejercicios Resueltos'],  # Etiqueta del eje X
        y=[len(puntuaciones)],       # Número total de puntuaciones (equivale a ejercicios resueltos)
        name='Ejercicios Resueltos'  # Nombre del gráfico
    )

    # Convierte los tiempos de timedelta a segundos
    tiempos_en_segundos = [t.total_seconds() for t in tiempos]
    # Calcula el tiempo promedio en segundos
    tiempo_promedio = sum(tiempos_en_segundos) / len(tiempos_en_segundos) if tiempos_en_segundos else 0

    # Gráfico de barras que muestra el tiempo promedio en segundos
    grafico3 = go.Bar(
        x=['Tiempo Promedio (s)'],  # Etiqueta del eje X
        y=[tiempo_promedio],        # Valor del tiempo promedio en segundos
        name='Tiempo Promedio'      # Nombre del gráfico
    )

    # Diccionario para contar la distribución de operaciones (suma, resta, multiplicación, división)
    operaciones_dict = {"+": 0, "-": 0, "*": 0, "/": 0}
    for operacion in operaciones:
        operaciones_dict[operacion] += 1  # Incrementa el contador de cada operación

    # Gráfico circular que muestra la distribución de operaciones
    grafico4 = go.Pie(
        labels=list(operaciones_dict.keys()),   # Etiquetas de las operaciones
        values=list(operaciones_dict.values()), # Cantidad de veces que se usó cada operación
        name='Distribución de Operaciones'      # Nombre del gráfico
    )

    # Define el diseño general de los gráficos
    layout = go.Layout(
        title="Dashboard de Juego - Tiempo Real",  # Título del dashboard
        xaxis_title="Categorías",                 # Título del eje X
        yaxis_title="Valores"                     # Título del eje Y
    )

    # Crea la figura con los gráficos y el layout, y devuelve el resultado en formato JSON
    fig = go.Figure(data=[grafico1, grafico2, grafico3, grafico4], layout=layout)
    return pio.to_json(fig)  # Convierte la figura en JSON para su envío al frontend

# Punto de entrada de la aplicación
if __name__ == '__main__':
    # Ejecuta la aplicación Flask en modo de depuración
    app.run(debug=True)
