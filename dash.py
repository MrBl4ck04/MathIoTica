from flask import Flask, render_template, jsonify, request
import mysql.connector
import plotly.graph_objs as go
import plotly.io as pio
from datetime import datetime

app = Flask(__name__)

# Conectar a la base de datos
def conectar():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",  # Cambia esto
        password="",  # Cambia esto
        database="mathiotica"
    )
    return conexion

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Obtener los nombres y cursos para los filtros dinámicos
@app.route('/obtener_filtros', methods=['GET'])
def obtener_filtros():
    conexion = conectar()
    cursor = conexion.cursor()

    # Consulta para obtener los nombres y cursos únicos
    cursor.execute("SELECT DISTINCT nombre, curso FROM juegos")
    resultados = cursor.fetchall()

    nombres = list(set([fila[0] for fila in resultados]))
    cursos = list(set([fila[1] for fila in resultados]))

    cursor.close()
    conexion.close()

    return jsonify({"nombres": nombres, "cursos": cursos})

# Ruta para obtener los datos de las gráficas
@app.route('/datos_grafico', methods=['GET'])
def datos_grafico():
    filtro_nombre = request.args.get('nombre', default=None, type=str)
    filtro_curso = request.args.get('curso', default=None, type=str)

    conexion = conectar()
    cursor = conexion.cursor()

    query = "SELECT nombre, puntuacion, tiempo, operacion FROM juegos WHERE 1=1"
    parametros = []

    if filtro_nombre:
        query += " AND nombre = %s"
        parametros.append(filtro_nombre)
    if filtro_curso:
        query += " AND curso = %s"
        parametros.append(filtro_curso)

    cursor.execute(query, parametros)
    resultados = cursor.fetchall()

    cursor.close()
    conexion.close()

    # Procesar los datos para las gráficas
    nombres, puntuaciones, tiempos, operaciones = [], [], [], []

    for fila in resultados:
        nombres.append(fila[0])
        puntuaciones.append(fila[1])
        tiempos.append(fila[2])
        operaciones.append(fila[3])

    # Crear gráficos (puntuación promedio, tiempo promedio, etc.)
    graficas = crear_graficas(puntuaciones, tiempos, operaciones)

    return jsonify(graficas)

# Función para generar los gráficos en Plotly
def crear_graficas(puntuaciones, tiempos, operaciones):
    # Gráfico de puntuación promedio
    puntuacion_promedio = sum(puntuaciones) / len(puntuaciones) if puntuaciones else 0

    grafico1 = go.Bar(
        x=['Puntuación Promedio'],
        y=[puntuacion_promedio],
        name='Puntuación Promedio'
    )

    # Gráfico de número de ejercicios resueltos
    grafico2 = go.Bar(
        x=['Ejercicios Resueltos'],
        y=[len(puntuaciones)],
        name='Ejercicios Resueltos'
    )

    # Tiempo promedio de respuesta (convertir timedelta a segundos)
    tiempos_en_segundos = [t.total_seconds() for t in tiempos]
    tiempo_promedio = sum(tiempos_en_segundos) / len(tiempos_en_segundos) if tiempos_en_segundos else 0

    grafico3 = go.Bar(
        x=['Tiempo Promedio (s)'],
        y=[tiempo_promedio],
        name='Tiempo Promedio'
    )

    # Distribución de operaciones
    operaciones_dict = {"+": 0, "-": 0, "*": 0, "/": 0}
    for operacion in operaciones:
        operaciones_dict[operacion] += 1

    grafico4 = go.Pie(
        labels=list(operaciones_dict.keys()),
        values=list(operaciones_dict.values()),
        name='Distribución de Operaciones'
    )

    layout = go.Layout(
        title="Dashboard de Juego - Tiempo Real",
        xaxis_title="Categorías",
        yaxis_title="Valores"
    )

    fig = go.Figure(data=[grafico1, grafico2, grafico3, grafico4], layout=layout)
    return pio.to_json(fig)


if __name__ == "__main__":
    app.run(debug=True)
