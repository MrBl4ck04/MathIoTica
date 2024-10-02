import tkinter as tk  # Para crear la interfaz gráfica
from tkinter import messagebox  # Para mostrar mensajes de error o información
import mysql.connector  # Para conectar con la base de datos MySQL
from datetime import datetime  # Para manejar fechas y horas
import time  # Para medir el tiempo de respuesta

# Función para conectar a la base de datos
def conectar_bd():
    # Retorna una conexión a la base de datos 'mate' en el servidor local
    return mysql.connector.connect(
        host="localhost",  # El servidor de la base de datos
        user="root",  # Usuario de la base de datos
        password="",  # Contraseña del usuario
        database="mate"  # Nombre de la base de datos
    )

# Función para obtener el número de juego más alto e incrementarlo
def obtener_nuevo_nr_juego():
    # Conectamos a la base de datos
    conexion = conectar_bd()
    cursor = conexion.cursor()  # Creamos un cursor para ejecutar consultas
    
    # Consultamos el máximo número de juego existente y le sumamos 1
    query = "SELECT IFNULL(MAX(nrJuego), 0) + 1 AS nuevo_nrJuego FROM juegos"
    cursor.execute(query)  # Ejecutamos la consulta
    resultado = cursor.fetchone()  # Obtenemos el resultado
    nuevo_nr_juego = resultado[0]  # Extraemos el nuevo número de juego
    
    cursor.close()  # Cerramos el cursor
    conexion.close()  # Cerramos la conexión
    return nuevo_nr_juego  # Retornamos el nuevo número de juego

# Función para guardar los datos por cada operación en la tabla 'juegos'
def guardar_operacion(nrJuego, nombre, curso, tiempo, puntuacion, operacion, digitos, logrado):
    # Conectamos a la base de datos
    conexion = conectar_bd()
    cursor = conexion.cursor()  # Creamos un cursor

    # Consulta para insertar un nuevo registro en la tabla 'juegos'
    query = "INSERT INTO juegos (nrJuego, nombre, curso, tiempo, fecha, puntuacion, operacion, digitos, logrado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    fecha_actual = datetime.now().date()  # Obtenemos la fecha actual
    # Ejecutamos la consulta con los parámetros correspondientes
    cursor.execute(query, (nrJuego, nombre, curso, tiempo, fecha_actual, puntuacion, operacion, digitos, logrado))
    
    conexion.commit()  # Confirmamos los cambios en la base de datos
    cursor.close()  # Cerramos el cursor
    conexion.close()  # Cerramos la conexión

# Función para obtener ejercicios de la base de datos
def obtener_ejercicios():
    # Conectamos a la base de datos
    conexion = conectar_bd()
    cursor = conexion.cursor(dictionary=True)  # Cursor para obtener resultados como diccionarios
    
    # Consulta para obtener ejercicios de la tabla 'ejercicios'
    query = "SELECT * FROM ejercicios"
    cursor.execute(query)  # Ejecutamos la consulta
    ejercicios = cursor.fetchall()  # Obtenemos todos los ejercicios
    
    cursor.close()  # Cerramos el cursor
    conexion.close()  # Cerramos la conexión
    return ejercicios  # Retornamos la lista de ejercicios

# Función para calcular la puntuación en base al tiempo de respuesta
def calcular_puntuacion(tiempo_respuesta, max_puntos):
    # Si la respuesta es más rápida o igual a 3 segundos, el jugador recibe la puntuación máxima
    if tiempo_respuesta <= 3:
        return max_puntos  # Máxima puntuación
    elif tiempo_respuesta <= 15:
        # La puntuación disminuye linealmente después de los 3 segundos
        return max(0, max_puntos - ((tiempo_respuesta - 3) / 12) * max_puntos)
    else:
        return 0  # Si el tiempo de respuesta supera los 15 segundos, la puntuación es 0

# Función que maneja el flujo del juego
def iniciar_juego():
    nombre = nombre_entry.get()  # Obtenemos el nombre ingresado
    curso = curso_var.get()  # Obtenemos el curso seleccionado
    
    # Verificamos que el nombre y el curso no estén vacíos
    if not nombre or not curso:
        messagebox.showerror("Error", "Por favor, ingresa tu nombre y selecciona un curso.")  # Mensaje de error
        return  # Salimos de la función si hay un error

    # Obtener un nuevo número de juego para esta partida
    nr_juego = obtener_nuevo_nr_juego()  # Obtenemos el nuevo número de juego

    operaciones = obtener_ejercicios()  # Obtenemos los ejercicios
    ejecutar_preguntas(nr_juego, nombre, curso, operaciones, 0, 0)  # Iniciamos las preguntas

# Función para ejecutar cada pregunta del juego y medir el tiempo de respuesta
def ejecutar_preguntas(nrJuego, nombre, curso, operaciones, indice, puntuacion_total):
    # Si hay más operaciones para mostrar
    if indice < len(operaciones):
        operacion = operaciones[indice]  # Obtenemos la operación actual
        pregunta_label.config(text=f"Resuelve: {operacion['valor1']} {operacion['operacion']} {operacion['valor2']}")  # Mostramos la pregunta
        
        # Capturamos el tiempo de inicio antes de mostrar la pregunta
        tiempo_inicio = time.time()  # Tiempo actual en segundos

        def responder():
            respuesta_usuario = respuesta_entry.get()  # Obtenemos la respuesta ingresada por el usuario
            tiempo_final = time.time()  # Tiempo actual en segundos
            tiempo_respuesta = round(tiempo_final - tiempo_inicio, 2)  # Calculamos el tiempo de respuesta en segundos

            # Validar si la respuesta es correcta
            respuesta_correcta = operacion['respuesta']  # Obtenemos la respuesta correcta
            logrado = int(respuesta_usuario == str(respuesta_correcta))  # Verificamos si la respuesta del usuario es correcta

            # Calcular la puntuación máxima según el número total de ejercicios
            max_puntos = 100 / len(operaciones)  # Cada ejercicio vale 100 puntos dividido por el número de ejercicios

            # Calcular puntuación en base al tiempo y si la respuesta es correcta
            puntuacion = calcular_puntuacion(tiempo_respuesta, max_puntos) if logrado else 0  # Calculamos la puntuación
            puntuacion_total_nuevo = puntuacion_total + puntuacion  # Actualizamos la puntuación total

            digitos = max(len(str(operacion['valor1'])), len(str(operacion['valor2'])))  # Calculamos la cantidad de dígitos de los valores
            # Guardamos la operación en la base de datos
            guardar_operacion(nrJuego, nombre, curso, tiempo_respuesta, puntuacion, operacion['operacion'], digitos, logrado)

            respuesta_entry.delete(0, tk.END)  # Limpiar campo de respuesta
            # Llamamos a la función recursivamente para la siguiente pregunta
            ejecutar_preguntas(nrJuego, nombre, curso, operaciones, indice + 1, puntuacion_total_nuevo)

        enviar_btn.config(command=responder)  # Configuramos el botón de enviar para llamar a la función 'responder'
    else:
        # Si se han respondido todas las preguntas, mostramos el resultado final
        porcentaje_logrado = (puntuacion_total / 100) * 100  # Calculamos el porcentaje de la puntuación total
        if porcentaje_logrado >= 60:  # Si el porcentaje es 60 o más, el jugador tuvo éxito
            messagebox.showinfo("Resultado", "¡Juego completado con éxito!")
        else:
            messagebox.showinfo("Resultado", "No lograste completar el juego.")  # Mensaje de error
        pregunta_label.config(text="¡Juego terminado!")  # Cambiamos el texto de la pregunta

# Configuración de la ventana principal
ventana = tk.Tk()  # Creamos la ventana principal
ventana.title("Juego de Matemáticas")  # Título de la ventana

# Entrada del nombre
nombre_label = tk.Label(ventana, text="Nombre:")  # Etiqueta para el campo de nombre
nombre_label.pack()  # Agregamos la etiqueta a la ventana
nombre_entry = tk.Entry(ventana)  # Campo de entrada para el nombre
nombre_entry.pack()  # Agregamos el campo a la ventana

# Selección del curso
curso_label = tk.Label(ventana, text="Curso:")  # Etiqueta para seleccionar el curso
curso_label.pack()  # Agregamos la etiqueta a la ventana

curso_var = tk.StringVar()  # Variable para almacenar la opción del curso
curso_opciones = ["Primero", "Segundo", "Tercero", "Cuarto", "Quinto", "Sexto"]  # Opciones de curso
curso_menu = tk.OptionMenu(ventana, curso_var, *curso_opciones)  # Menú desplegable para seleccionar el curso
curso_menu.pack()  # Agregamos el menú a la ventana

# Botón para iniciar el juego
iniciar_btn = tk.Button(ventana, text="Iniciar Juego", command=iniciar_juego)  # Botón para iniciar el juego
iniciar_btn.pack()  # Agregamos el botón a la ventana

# Etiqueta para mostrar preguntas
pregunta_label = tk.Label(ventana, text="")  # Etiqueta para mostrar las preguntas
pregunta_label.pack()  # Agregamos la etiqueta a la ventana

# Campo de entrada para la respuesta
respuesta_label = tk.Label(ventana, text="Respuesta:")  # Etiqueta para la respuesta
respuesta_label.pack()  # Agregamos la etiqueta a la ventana
respuesta_entry = tk.Entry(ventana)  # Campo de entrada para la respuesta
respuesta_entry.pack()  # Agregamos el campo a la ventana

# Botón para enviar la respuesta
enviar_btn = tk.Button(ventana, text="Enviar Respuesta")  # Botón para enviar la respuesta
enviar_btn.pack()  # Agregamos el botón a la ventana

# Iniciar el bucle principal de la ventana
ventana.mainloop()  # Mantiene la ventana abierta
