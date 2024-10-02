import tkinter as tk  # Importa la librería tkinter y la renombra como tk
from tkinter import ttk, messagebox  # Importa ttk (widget de la interfaz) y messagebox (para mostrar mensajes)
import mysql.connector  # Importa el conector para MySQL
import csv  # Importa el módulo csv para trabajar con archivos CSV

def reportes(root, conn):  # Define la función 'reportes' que recibe la ventana principal 'root' y la conexión a la base de datos 'conn'
    # Crear ventana de reportes
    reporte_window = tk.Toplevel(root)  # Crea una nueva ventana como hija de 'root'
    reporte_window.title("Reportes")  # Establece el título de la ventana

    # Variables para las entradas
    curso_var = tk.StringVar()  # Variable para almacenar el curso seleccionado
    usuario_var = tk.StringVar()  # Variable para almacenar el usuario seleccionado

    # Entradas para curso y usuario
    tk.Label(reporte_window, text="Curso:").pack(pady=5)  # Crea y muestra una etiqueta para "Curso"
    curso_combo = ttk.Combobox(reporte_window, textvariable=curso_var)  # Crea un combobox para seleccionar cursos
    curso_combo.pack(pady=5)  # Muestra el combobox en la ventana

    tk.Label(reporte_window, text="Usuario:").pack(pady=5)  # Crea y muestra una etiqueta para "Usuario"
    usuario_combo = ttk.Combobox(reporte_window, textvariable=usuario_var)  # Crea un combobox para seleccionar usuarios
    usuario_combo.pack(pady=5)  # Muestra el combobox en la ventana

    # Función para llenar los comboboxes con cursos y usuarios únicos
    def cargar_cursos_y_usuarios():  # Define la función que carga los cursos y usuarios
        try:
            cursor = conn.cursor()  # Crea un cursor para ejecutar consultas en la base de datos
            # Cargar cursos únicos
            cursor.execute("SELECT DISTINCT curso FROM juegos")  # Ejecuta una consulta para obtener cursos únicos
            cursos = cursor.fetchall()  # Recupera todos los resultados de la consulta
            curso_combo['values'] = [curso[0] for curso in cursos]  # Agrega los cursos al combobox

            # Cargar usuarios únicos
            cursor.execute("SELECT DISTINCT nombre FROM juegos")  # Ejecuta una consulta para obtener usuarios únicos
            usuarios = cursor.fetchall()  # Recupera todos los resultados de la consulta
            usuario_combo['values'] = [usuario[0] for usuario in usuarios]  # Agrega los usuarios al combobox

            cursor.close()  # Cierra el cursor
        except mysql.connector.Error as err:  # Manejo de errores de la conexión MySQL
            messagebox.showerror("Error", f"Error al cargar cursos y usuarios: {err}")  # Muestra un mensaje de error

    # Llamar a la función para cargar los cursos y usuarios al inicio
    cargar_cursos_y_usuarios()  # Llama a la función para llenar los comboboxes al abrir la ventana

    # Función para buscar en la base de datos
    def buscar():  # Define la función que realiza la búsqueda
        curso = curso_var.get()  # Obtiene el curso seleccionado
        usuario = usuario_var.get()  # Obtiene el usuario seleccionado

        # Verificar si se seleccionaron curso y usuario
        if not curso or not usuario:  # Si no se ha seleccionado curso o usuario
            messagebox.showwarning("Advertencia", "Por favor, selecciona un curso y un usuario.")  # Muestra una advertencia
            return  # Sale de la función

        try:
            cursor = conn.cursor()  # Crea un cursor para ejecutar consultas en la base de datos
            query = """  # Define la consulta SQL para buscar datos en la tabla 'juegos'
            SELECT * FROM juegos WHERE curso = %s AND nombre = %s
            """
            cursor.execute(query, (curso, usuario))  # Ejecuta la consulta con los parámetros seleccionados
            resultados = cursor.fetchall()  # Recupera todos los resultados de la consulta

            # Limpiar tabla existente
            for i in tree.get_children():  # Itera sobre los elementos existentes en la tabla
                tree.delete(i)  # Elimina cada elemento de la tabla

            # Llenar la tabla con los resultados
            if resultados:  # Si hay resultados
                for row in resultados:  # Itera sobre cada fila de resultados
                    tree.insert("", "end", values=row)  # Agrega la fila a la tabla
            else:  # Si no hay resultados
                messagebox.showinfo("Sin resultados", "No se encontraron resultados para la búsqueda.")  # Muestra un mensaje informativo

            cursor.close()  # Cierra el cursor

        except mysql.connector.Error as err:  # Manejo de errores de la conexión MySQL
            messagebox.showerror("Error", f"Error al conectarse a la base de datos: {err}")  # Muestra un mensaje de error

    # Tabla para mostrar los resultados
    columns = ["ID", "Curso", "Nombre", "Tiempo", "Fecha", "Puntuación", "Operación", "Digitos", "Logrado"]  # Define los encabezados de la tabla
    tree = ttk.Treeview(reporte_window, columns=columns, show='headings')  # Crea una tabla (Treeview) para mostrar resultados
    for col in columns:  # Itera sobre los encabezados de la tabla
        tree.heading(col, text=col)  # Establece el encabezado de cada columna
    tree.pack(pady=10, fill=tk.BOTH, expand=True)  # Muestra la tabla en la ventana

    # Botón para buscar
    buscar_btn = tk.Button(reporte_window, text="Buscar", command=buscar)  # Crea un botón que ejecuta la función de búsqueda
    buscar_btn.pack(pady=10)  # Muestra el botón en la ventana

    # Función para guardar en CSV
    def guardar_csv():  # Define la función para guardar los resultados en un archivo CSV
        usuario = usuario_var.get()  # Obtiene el nombre del usuario seleccionado
        # Verifica que el usuario tenga un nombre válido para usar como parte del nombre del archivo
        if not usuario:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un usuario antes de guardar.")  # Muestra advertencia si no hay usuario
            return  # Sale de la función

        # Crear nombre de archivo con el nombre del usuario
        nombre_archivo = f"{usuario}_reportes.csv"  # Define el nombre del archivo usando el nombre del usuario

        with open(nombre_archivo, "w", newline="") as archivo:  # Abre (o crea) un archivo CSV para escribir con el nombre definido
            writer = csv.writer(archivo)  # Crea un escritor de CSV
            writer.writerow(columns)  # Escribe los encabezados en el archivo
            
            for row in tree.get_children():  # Itera sobre los elementos en la tabla
                writer.writerow(tree.item(row)["values"])  # Escribe los valores de cada fila en el archivo CSV
        
        messagebox.showinfo("Éxito", f"Datos guardados en '{nombre_archivo}'")  # Muestra un mensaje de éxito

    # Botón para guardar como CSV
    guardar_btn = tk.Button(reporte_window, text="Guardar como CSV", command=guardar_csv)  # Crea un botón que ejecuta la función para guardar en CSV
    guardar_btn.pack(pady=10)  # Muestra el botón en la ventana
