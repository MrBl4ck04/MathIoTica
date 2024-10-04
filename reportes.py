import tkinter as tk  # Importa la librería tkinter y la renombra como tk
from tkinter import ttk, messagebox  # Importa ttk (widget de la interfaz) y messagebox (para mostrar mensajes)
import mysql.connector  # Importa el conector para MySQL
import csv  # Importa el módulo csv para trabajar con archivos CSV
import matplotlib.pyplot as plt  # Importa matplotlib para graficar
import pandas as pd  # Importa pandas para manejar datos en formato de tabla

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

            # Graficar curva de aprendizaje
            graficar_curva_aprendizaje(curso, usuario)  # Llama a la función para graficar

        except mysql.connector.Error as err:  # Manejo de errores de la conexión MySQL
            messagebox.showerror("Error", f"Error al conectarse a la base de datos: {err}")  # Muestra un mensaje de error

    # Función para graficar la curva de aprendizaje
    def graficar_curva_aprendizaje(curso, usuario):
        try:
            # Consulta para obtener la cantidad de logros y no logros por fecha
            query_logros = """
            SELECT fecha, COUNT(logrado) as logros
            FROM juegos
            WHERE curso = %s AND nombre = %s AND logrado = 1
            GROUP BY fecha
            ORDER BY fecha
            """
            query_no_logros = """
            SELECT fecha, COUNT(logrado) as no_logros
            FROM juegos
            WHERE curso = %s AND nombre = %s AND logrado = 0
            GROUP BY fecha
            ORDER BY fecha
            """

            # Ejecutar consultas y cargar los resultados en DataFrames
            df_logros = pd.read_sql(query_logros, conn, params=(curso, usuario))
            df_no_logros = pd.read_sql(query_no_logros, conn, params=(curso, usuario))

            if not df_logros.empty or not df_no_logros.empty:  # Si hay datos
                plt.figure(figsize=(10, 5))  # Define el tamaño de la figura

                # Grafica los logros
                plt.plot(df_logros['fecha'], df_logros['logros'], marker='o', label="Logros", color='green')
                # Grafica los no logros
                plt.plot(df_no_logros['fecha'], df_no_logros['no_logros'], marker='x', label="No logrados", color='red')

                # Configuración de la gráfica
                plt.title(f"Curva de Aprendizaje: {usuario} en {curso}")  # Título de la gráfica
                plt.xlabel("Fecha")  # Etiqueta del eje X
                plt.ylabel("Cantidad")  # Etiqueta del eje Y
                plt.xticks(rotation=45)  # Rota las etiquetas del eje X para mejor visibilidad
                plt.grid()  # Muestra la cuadrícula
                plt.legend()  # Muestra la leyenda
                plt.tight_layout()  # Ajusta el diseño
                plt.show()  # Muestra la gráfica
            else:
                messagebox.showinfo("Sin datos", "No se encontraron datos para graficar.")  # Muestra mensaje si no hay datos

        except Exception as e:
            messagebox.showerror("Error", f"Error al graficar la curva de aprendizaje: {e}")  # Muestra un mensaje de error

    # Tabla para mostrar los resultados
    columns = ["ID", "N° Juego", "Curso", "Nombre", "Tiempo", "Fecha", "Puntuación", "Operación", "Digitos", "Logrado"]  # Define los encabezados de la tabla
    tree = ttk.Treeview(reporte_window, columns=columns, show='headings')  # Crea una tabla (Treeview) para mostrar resultados
    # Crear un frame para contener la tabla y los scrollbars
    table_frame = tk.Frame(reporte_window)
    table_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    # Scroll vertical
    scrollbar_vertical = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
    scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y)

    # Scroll horizontal
    scrollbar_horizontal = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=tree.xview)
    scrollbar_horizontal.pack(side=tk.BOTTOM, fill=tk.X)

    # Configurar la tabla para que use los scrollbars
    tree.configure(yscrollcommand=scrollbar_vertical.set, xscrollcommand=scrollbar_horizontal.set)

    for col in columns:  # Itera sobre los encabezados de la tabla
        tree.heading(col, text=col)  # Establece el encabezado de cada columna
    tree.pack(pady=10, fill=tk.BOTH, expand=True)  # Muestra la tabla en la ventana

    # Botón para buscar
    buscar_btn = tk.Button(reporte_window, text="Buscar", command=buscar, bg="#008080",        
    fg="white",         
    font=('Arial', 12, 'bold'),  
    relief="raised",     
    bd=5)  # Crea un botón que ejecuta la función de búsqueda
    buscar_btn.pack(pady=10)  # Muestra el botón en la ventana

    # Función para guardar en CSV
    def guardar_csv():  # Define la función para guardar los resultados en un archivo CSV
        usuario = usuario_var.get()  # Obtiene el nombre del usuario seleccionado
        # Verificar si se seleccionó un usuario
        if not usuario:  # Si no se ha seleccionado usuario
            messagebox.showwarning("Advertencia", "Por favor, selecciona un usuario.")  # Muestra una advertencia
            return  # Sale de la función
        # Preguntar al usuario donde guardar el archivo CSV
        file_path = tk.filedialog.asksaveasfilename(defaultextension=".csv", 
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])  # Muestra un cuadro de diálogo para guardar el archivo
        if file_path:  # Si se ha seleccionado una ruta
            with open(file_path, mode='w', newline='') as file:  # Abre el archivo en modo escritura
                writer = csv.writer(file)  # Crea un objeto escritor para escribir en el archivo
                writer.writerow(columns)  # Escribe los encabezados en la primera fila
                for row in tree.get_children():  # Itera sobre los elementos de la tabla
                    writer.writerow(tree.item(row)['values'])  # Escribe los valores de cada fila en el archivo
            messagebox.showinfo("Éxito", "Los datos se han guardado correctamente en el archivo CSV.")  # Muestra un mensaje de éxito

    # Botón para guardar en CSV
    guardar_csv_btn = tk.Button(reporte_window, text="Guardar CSV", command=guardar_csv, bg="#008080", 
    fg="white", font=('Arial', 12, 'bold'), relief="raised", bd=5)  # Crea un botón para guardar en CSV
    guardar_csv_btn.pack(pady=10)  # Muestra el botón en la ventana

