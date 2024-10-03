# Importar la biblioteca tkinter para crear interfaces gráficas
import tkinter as tk
# Importar ttkbootstrap para mejorar el estilo de los widgets de tkinter
import ttkbootstrap as ttk  # Cambiamos el uso de ttk a ttkbootstrap para más opciones de estilo
# Importar messagebox para mostrar cuadros de diálogo
from tkinter import messagebox
# Importar mysql.connector para conectar y operar con la base de datos MySQL
import mysql.connector
# Importar datetime para trabajar con fechas y horas
from datetime import datetime
# Importar time para medir el tiempo de respuesta
import time
# Importar Image y ImageTk para trabajar con imágenes
from PIL import Image, ImageTk

# Función para conectar a la base de datos MySQL
def conectar_bd():
    # Retorna una conexión a la base de datos mathiotica
    return mysql.connector.connect(
        host="localhost",  # Dirección del servidor de la base de datos
        user="root",  # Nombre de usuario para acceder a la base de datos
        password="",  # Contraseña para el usuario
        database="mathiotica"  # Nombre de la base de datos
    )

# Función para obtener el número de juego más alto e incrementarlo
def obtener_nuevo_nr_juego():
    conexion = conectar_bd()  # Establecer conexión a la base de datos
    cursor = conexion.cursor()  # Crear un cursor para ejecutar consultas
    # Consulta SQL para obtener el número de juego más alto y agregar 1
    query = "SELECT IFNULL(MAX(nrJuego), 0) + 1 AS nuevo_nrJuego FROM juegos"
    cursor.execute(query)  # Ejecutar la consulta
    resultado = cursor.fetchone()  # Obtener el resultado de la consulta
    nuevo_nr_juego = resultado[0]  # Extraer el nuevo número de juego
    cursor.close()  # Cerrar el cursor
    conexion.close()  # Cerrar la conexión
    return nuevo_nr_juego  # Retornar el nuevo número de juego

# Función para guardar los datos de cada operación en la tabla 'juegos'
def guardar_operacion(nrJuego, nombre, curso, tiempo, puntuacion, operacion, digitos, logrado):
    conexion = conectar_bd()  # Establecer conexión a la base de datos
    cursor = conexion.cursor()  # Crear un cursor para ejecutar consultas
    # Consulta SQL para insertar una nueva operación en la tabla 'juegos'
    query = "INSERT INTO juegos (nrJuego, nombre, curso, tiempo, fecha, puntuacion, operacion, digitos, logrado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    fecha_actual = datetime.now().date()  # Obtener la fecha actual
    # Ejecutar la consulta con los parámetros correspondientes
    cursor.execute(query, (nrJuego, nombre, curso, tiempo, fecha_actual, puntuacion, operacion, digitos, logrado))
    conexion.commit()  # Confirmar los cambios en la base de datos
    cursor.close()  # Cerrar el cursor
    conexion.close()  # Cerrar la conexión

# Función para obtener ejercicios de la base de datos
def obtener_ejercicios():
    conexion = conectar_bd()  # Establecer conexión a la base de datos
    cursor = conexion.cursor(dictionary=True)  # Crear un cursor que retorne resultados como diccionarios
    query = "SELECT * FROM ejercicios"  # Consulta SQL para obtener todos los ejercicios
    cursor.execute(query)  # Ejecutar la consulta
    ejercicios = cursor.fetchall()  # Obtener todos los resultados
    cursor.close()  # Cerrar el cursor
    conexion.close()  # Cerrar la conexión
    return ejercicios  # Retornar la lista de ejercicios

# Función para calcular la puntuación en base al tiempo de respuesta
def calcular_puntuacion(tiempo_respuesta, max_puntos):
    if tiempo_respuesta <= 3:
        return max_puntos  # Devuelve el máximo de puntos si el tiempo es menor o igual a 3 segundos
    elif tiempo_respuesta <= 15:
        # Calcula la puntuación proporcional basada en el tiempo de respuesta
        return max(0, max_puntos - ((tiempo_respuesta - 3) / 12) * max_puntos)
    else:
        return 0  # Devuelve 0 puntos si el tiempo es mayor a 15 segundos

# Función que maneja el flujo del juego
def iniciar_juego():
    nombre = nombre_entry.get()  # Obtener el nombre del campo de entrada
    curso = curso_var.get()  # Obtener el curso seleccionado

    # Validar si se ingresó el nombre y se seleccionó un curso
    if not nombre or not curso:
        messagebox.showerror("Error", "Por favor, ingresa tu nombre y selecciona un curso.")  # Mostrar error
        return  # Terminar la función si hay un error

    nr_juego = obtener_nuevo_nr_juego()  # Obtener el nuevo número de juego
    operaciones = obtener_ejercicios()  # Obtener ejercicios de la base de datos
    # Iniciar el ciclo de preguntas
    ejecutar_preguntas(nr_juego, nombre, curso, operaciones, 0, 0)

# Función para ejecutar cada pregunta del juego y medir el tiempo de respuesta
def ejecutar_preguntas(nrJuego, nombre, curso, operaciones, indice, puntuacion_total):
    if indice < len(operaciones):  # Verificar si hay más operaciones para realizar
        operacion = operaciones[indice]  # Obtener la operación actual
        pregunta_label.config(text=f"Resuelve: {operacion['valor1']} {operacion['operacion']} {operacion['valor2']}")  # Mostrar la pregunta
        tiempo_inicio = time.time()  # Registrar el tiempo de inicio

        # Función interna que maneja la respuesta del usuario
        def responder():
            respuesta_usuario = respuesta_entry.get()  # Obtener la respuesta del usuario
            tiempo_final = time.time()  # Registrar el tiempo final
            tiempo_respuesta = round(tiempo_final - tiempo_inicio, 2)  # Calcular el tiempo de respuesta

            respuesta_correcta = operacion['respuesta']  # Obtener la respuesta correcta
            logrado = int(respuesta_usuario == str(respuesta_correcta))  # Verificar si la respuesta es correcta
            max_puntos = 100 / len(operaciones)  # Calcular la puntuación máxima por pregunta
            # Calcular la puntuación basada en el tiempo de respuesta
            puntuacion = calcular_puntuacion(tiempo_respuesta, max_puntos) if logrado else 0
            puntuacion_total_nuevo = puntuacion_total + puntuacion  # Actualizar la puntuación total

            # Calcular el número de dígitos de la operación
            digitos = max(len(str(operacion['valor1'])), len(str(operacion['valor2'])))
            # Guardar la operación en la base de datos
            guardar_operacion(nrJuego, nombre, curso, tiempo_respuesta, puntuacion, operacion['operacion'], digitos, logrado)

            respuesta_entry.delete(0, tk.END)  # Limpiar la entrada de respuesta
            # Llamar nuevamente a la función para ejecutar la siguiente pregunta
            ejecutar_preguntas(nrJuego, nombre, curso, operaciones, indice + 1, puntuacion_total_nuevo)

        enviar_btn.config(command=responder)  # Configurar el botón para que llame a la función responder
    else:
        # Calcular el porcentaje logrado
        porcentaje_logrado = (puntuacion_total / 100) * 100
        # Mostrar mensaje de resultado según el porcentaje logrado
        if porcentaje_logrado >= 60:
            messagebox.showinfo("Resultado", "¡Juego completado con éxito!")  # Mensaje de éxito
        else:
            messagebox.showinfo("Resultado", "No lograste completar el juego.")  # Mensaje de fallo
        pregunta_label.config(text="¡Juego terminado!")  # Actualizar la etiqueta de pregunta

# Configuración de la ventana principal
ventana = ttk.Window(themename="flatly")  # Crear una ventana de ttkbootstrap con el tema "flatly"
ventana.title("MATHIOTICA")  # Establecer el título de la ventana
ventana.geometry("500x500")  # Definir el tamaño de la ventana

# Crear un canvas para colocar la imagen de fondo
canvas = tk.Canvas(ventana, width=400, height=400)  # Crear un canvas con dimensiones específicas
canvas.pack(fill="both", expand=True)  # Hacer que el canvas se expanda y llene la ventana

# Cargar la imagen como fondo
imagen_fondo = Image.open("math.png")  # Abrir la imagen de fondo
# Redimensionar la imagen para que encaje en la ventana
imagen_fondo = imagen_fondo.resize((500, 500), Image.Resampling.LANCZOS)
imagen_fondo_tk = ImageTk.PhotoImage(imagen_fondo)  # Convertir la imagen a formato que tkinter puede usar

# Colocar la imagen en el canvas
canvas.create_image(0, 0, image=imagen_fondo_tk, anchor="nw")  # Colocar la imagen en la esquina superior izquierda

# Añadir el título "MATHIOTICA" en Times New Roman, Bold 14
titulo_label = tk.Label(ventana, text="MATHIOTICA", font=("Times New Roman", 15, "bold"), bg='#FFB6C1')  # Crear etiqueta para el título
titulo_label_window = canvas.create_window(200, 10, anchor="nw", window=titulo_label)  # Colocar la etiqueta en el canvas

# Configurar el estilo para todas las etiquetas y entradas
fuente = ("Arial Rounded MT Bold", 10)  # Definir fuente para las etiquetas y entradas

# Añadir los widgets sobre el canvas
# Etiqueta para el nombre
nombre_label = tk.Label(ventana, text="Nombre:", font=fuente, bg='#FFB6C1')  # Crear etiqueta para nombre
nombre_label_window = canvas.create_window(100, 50, anchor="nw", window=nombre_label)  # Colocar etiqueta en el canvas

# Campo de entrada para el nombre
nombre_entry = tk.Entry(ventana, font=fuente)  # Crear entrada para nombre
nombre_entry_window = canvas.create_window(180, 50, anchor="nw", window=nombre_entry)  # Colocar entrada en el canvas

# Etiqueta para el curso
curso_label = tk.Label(ventana, text="Curso:", font=fuente, bg='#FFB6C1')  # Crear etiqueta para curso
curso_label_window = canvas.create_window(100, 100, anchor="nw", window=curso_label)  # Colocar etiqueta en el canvas

# Variable para almacenar el curso seleccionado
curso_var = tk.StringVar()  # Crear variable para almacenar el curso
# Lista de opciones de curso
curso_opciones = ["Primero", "Segundo", "Tercero", "Cuarto", "Quinto", "Sexto"]
# Menú desplegable para seleccionar el curso
curso_menu = tk.OptionMenu(ventana, curso_var, *curso_opciones)  # Crear menú desplegable
curso_menu.config(font=fuente)  # Configurar la fuente del menú
curso_menu_window = canvas.create_window(180, 100, anchor="nw", window=curso_menu)  # Colocar menú en el canvas

# Botón beige redondeado con ttkbootstrap para iniciar el juego
iniciar_btn = ttk.Button(ventana, text="Iniciar Juego", bootstyle="warning", command=iniciar_juego)  # Crear botón para iniciar el juego
iniciar_btn_window = canvas.create_window(150, 150, anchor="nw", window=iniciar_btn)  # Colocar botón en el canvas

# Etiqueta para mostrar la pregunta
pregunta_label = tk.Label(ventana, text="", font=fuente, bg='#FFB6C1')  # Crear etiqueta para mostrar la pregunta
pregunta_label_window = canvas.create_window(150, 200, anchor="nw", window=pregunta_label)  # Colocar etiqueta en el canvas

# Etiqueta para la respuesta
respuesta_label = tk.Label(ventana, text="Respuesta:", font=fuente, bg='#FFB6C1')  # Crear etiqueta para la respuesta
respuesta_label_window = canvas.create_window(100, 250, anchor="nw", window=respuesta_label)  # Colocar etiqueta en el canvas

# Campo de entrada para la respuesta
respuesta_entry = tk.Entry(ventana, font=fuente)  # Crear entrada para la respuesta
respuesta_entry_window = canvas.create_window(200, 250, anchor="nw", window=respuesta_entry)  # Colocar entrada en el canvas

# Botón para enviar la respuesta
enviar_btn = ttk.Button(ventana, text="Enviar Respuesta", bootstyle="success")  # Crear botón para enviar respuesta
enviar_btn_window = canvas.create_window(150, 300, anchor="nw", window=enviar_btn)  # Colocar botón en el canvas

# Iniciar el bucle principal de la ventana
ventana.mainloop()  # Ejecutar el bucle principal de la interfaz gráfica
