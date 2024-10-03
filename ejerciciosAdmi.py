import tkinter as tk 
import webbrowser  # Importa la librería webbrowser
from tkinter import ttk, messagebox 
import mysql.connector 
from reportes import reportes
# Conectar a la base de datos MySQL
conn = mysql.connector.connect(
    host="192.168.243.2",  
    user="Franz", 
    password="",  
    database="mathiotica" 
)
cursor = conn.cursor()  # Crea un cursor para ejecutar consultas en la base de datos

# Variables globales para rastrear ventanas abiertas
ejercicios_win = None
modificar_win = None
agregar_win = None

# Función para abrir la ventana y agregar un nuevo ejercicio
def agregar_ejercicio():
    global agregar_win  # Variable global para la ventana de agregar
    if agregar_win is not None:
        agregar_win.destroy()  # Cierra la ventana si ya está abierta

    agregar_win = tk.Toplevel(root)  # Crea una nueva ventana sobre la ventana principal
    agregar_win.title("Agregar Ejercicio")  # Establece el título de la ventana

    # Crear campos del formulario
    lbl_valor1 = tk.Label(agregar_win, text="Valor 1")  # Crea una etiqueta para el primer valor
    lbl_valor1.grid(row=0, column=0, padx=10, pady=10)  # Coloca la etiqueta en la cuadrícula
    entry_valor1 = tk.Entry(agregar_win)  # Crea un campo de entrada para el primer valor
    entry_valor1.grid(row=0, column=1, padx=10, pady=10)  # Coloca el campo en la cuadrícula

    lbl_operacion = tk.Label(agregar_win, text="Operación")  # Crea una etiqueta para la operación
    lbl_operacion.grid(row=0, column=2, padx=10, pady=10)  # Coloca la etiqueta en la cuadrícula

    operacion_var = tk.StringVar()  # Variable para almacenar la operación seleccionada
    combo_operacion = ttk.Combobox(agregar_win, textvariable=operacion_var, values=["+", "-", "*", "/"])  # Crea un combo para seleccionar la operación
    combo_operacion.grid(row=0, column=3, padx=10, pady=10)  # Coloca el combo en la cuadrícula

    lbl_valor2 = tk.Label(agregar_win, text="Valor 2")  # Crea una etiqueta para el segundo valor
    lbl_valor2.grid(row=0, column=4, padx=10, pady=10)  # Coloca la etiqueta en la cuadrícula
    entry_valor2 = tk.Entry(agregar_win)  # Crea un campo de entrada para el segundo valor
    entry_valor2.grid(row=0, column=5, padx=10, pady=10)  # Coloca el campo en la cuadrícula

    lbl_respuesta = tk.Label(agregar_win, text="Resultado")  # Crea una etiqueta para el resultado
    lbl_respuesta.grid(row=1, column=0, padx=10, pady=10)  # Coloca la etiqueta en la cuadrícula
    entry_respuesta = tk.Entry(agregar_win)  # Crea un campo de entrada para el resultado
    entry_respuesta.grid(row=1, column=1, padx=10, pady=10)  # Coloca el campo en la cuadrícula

    # Función para agregar ejercicio a la base de datos
    def guardar_ejercicio():
        valor1 = entry_valor1.get()  # Obtiene el valor del primer campo de entrada
        valor2 = entry_valor2.get()  # Obtiene el valor del segundo campo de entrada
        operacion = combo_operacion.get()  # Obtiene la operación seleccionada
        respuesta = entry_respuesta.get()  # Obtiene el resultado del campo de entrada

        if not (valor1 and valor2 and operacion and respuesta):  # Verifica si todos los campos están completos
            messagebox.showwarning("Campos incompletos", "Por favor complete todos los campos.")  # Muestra un aviso si hay campos vacíos
            return  # Sale de la función si hay campos vacíos

        try:
            valor1 = int(valor1)  # Convierte el primer valor a entero
            valor2 = int(valor2)  # Convierte el segundo valor a entero
            respuesta = int(respuesta)  # Convierte el resultado a entero
        except ValueError:  # Captura el error si la conversión falla
            messagebox.showerror("Error", "Los valores y el resultado deben ser números.")  # Muestra un mensaje de error
            return  # Sale de la función si hay error

        # Insertar el ejercicio en la base de datos
        query = "INSERT INTO ejercicios (valor1, operacion, valor2, respuesta) VALUES (%s, %s, %s, %s)"  # Consulta SQL para insertar un nuevo ejercicio
        cursor.execute(query, (valor1, operacion, valor2, respuesta))  # Ejecuta la consulta con los valores obtenidos
        conn.commit()  # Guarda los cambios en la base de datos

        messagebox.showinfo("Éxito", "Ejercicio agregado exitosamente.")  # Muestra un mensaje de éxito
        agregar_win.destroy()  # Cierra la ventana de agregar ejercicio
        mostrar_ejercicios()  # Actualiza la tabla de ejercicios

    # Botón para guardar el ejercicio
    btn_guardar = tk.Button(agregar_win, text="Guardar Ejercicio", command=guardar_ejercicio,  bg="#008080",        
    fg="white",         
    font=('Arial', 11, 'bold'),  
    relief="raised",     
    bd=5,   )  # Crea un botón para guardar el ejercicio
    btn_guardar.grid(row=2, column=0, columnspan=2, pady=10)  # Coloca el botón en la cuadrícula



# Función para mostrar la tabla de ejercicios
def mostrar_ejercicios():
    global ejercicios_win  # Utiliza la variable global
    # Cierra la ventana anterior si está abierta
    if ejercicios_win is not None:
        ejercicios_win.destroy()

    ejercicios_win = tk.Toplevel(root)  # Crea una nueva ventana sobre la ventana principal
    ejercicios_win.title("Ejercicios")  # Título de la ventana

    # Crear un marco para la tabla y las barras de desplazamiento
    frame = tk.Frame(ejercicios_win)  # Crea un contenedor para la tabla
    frame.pack(expand=True, fill='both')  # Expande el marco y lo llena en ambas direcciones

    # Botón para agregar nuevo ejercicio
    btn_agregar = tk.Button(ejercicios_win, text="Agregar Ejercicio", command=agregar_ejercicio, bg="#008080",        
    fg="white",         
    font=('Arial', 11, 'bold'),  
    relief="raised",     
    bd=5)
    btn_agregar.pack(pady=10)


    # Definir las columnas en el orden correcto
    cols = ("ID","Valor 1", "Operación", "Valor 2", "=", "Resultado")  # Nombres de las columnas
    tree = ttk.Treeview(frame, columns=cols, show='headings')  # Crea una tabla con las columnas definidas

    # Configurar encabezados de las columnas
    for col in cols:
        tree.heading(col, text=col)  # Establece el texto del encabezado para cada columna

    # Ajustar el ancho de las columnas
    tree.column("=", width=30, anchor="center")  # Ajusta la columna del "=" para que quede centrada
    tree.pack(side=tk.LEFT, expand=True, fill='both')  # Empaqueta la tabla en el marco

    # Agregar barra de desplazamiento vertical
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)  # Crea una barra de desplazamiento
    scrollbar.pack(side=tk.RIGHT, fill='y')  # Coloca la barra de desplazamiento a la derecha
    tree.configure(yscroll=scrollbar.set)  # Configura la tabla para que use la barra de desplazamiento

    # Obtener datos de la base de datos
    cursor.execute("SELECT * FROM ejercicios")  # Ejecuta la consulta para obtener todos los ejercicios
    ejercicios = cursor.fetchall()  # Recupera todos los resultados de la consulta

    # Función para eliminar ejercicio
    def eliminar_ejercicio(ejercicio_id):
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de que deseas eliminar este ejercicio? (Id:{ejercicio_id})"):  # Pregunta de confirmación
            cursor.execute("DELETE FROM ejercicios WHERE id_ejercicio = %s", (ejercicio_id,))  # Ejecuta la consulta para eliminar el ejercicio
            conn.commit()  # Guarda los cambios en la base de datos
            mostrar_ejercicios()  # Actualiza la tabla de ejercicios
            messagebox.showinfo("Éxito", "Ejercicio eliminado exitosamente.")  # Mensaje de éxito

    # Función para modificar ejercicio
    def modificar_ejercicio(ejercicio_id):
        global modificar_win  # Utiliza la variable global
        # Cierra la ventana anterior si está abierta
        if modificar_win is not None:
            modificar_win.destroy()

        modificar_win = tk.Toplevel(root)  # Crea una nueva ventana para modificar
        modificar_win.title("Modificar Ejercicio")  # Título de la ventana de modificación

        # Obtener los valores actuales del ejercicio
        cursor.execute("SELECT * FROM ejercicios WHERE id_ejercicio = %s", (ejercicio_id,))  # Recupera el ejercicio específico
        ejercicio = cursor.fetchone()  # Obtiene los datos del ejercicio

        # Campos para modificar el ejercicio
        lbl_valor1 = tk.Label(modificar_win, text="Valor 1")  # Etiqueta para "Valor 1"
        lbl_valor1.grid(row=0, column=0, padx=10, pady=10)  # Coloca la etiqueta en la ventana
        entry_valor1 = tk.Entry(modificar_win)  # Campo de entrada para "Valor 1"
        entry_valor1.insert(0, ejercicio[2])  # Inserta el valor actual en el campo
        entry_valor1.grid(row=0, column=1, padx=10, pady=10)  # Coloca el campo de entrada en la ventana

        lbl_operacion = tk.Label(modificar_win, text="Operación")  # Etiqueta para "Operación"
        lbl_operacion.grid(row=0, column=2, padx=10, pady=10)  # Coloca la etiqueta
        combo_operacion = ttk.Combobox(modificar_win, values=["+", "-", "*", "/"])  # Combo para seleccionar operación
        combo_operacion.set(ejercicio[1])  # Establece la operación actual en el combo
        combo_operacion.grid(row=0, column=3, padx=10, pady=10)

        lbl_valor2 = tk.Label(modificar_win, text="Valor 2")  # Etiqueta para "Valor 2"
        lbl_valor2.grid(row=0, column=4, padx=10, pady=10)  # Coloca la etiqueta
        entry_valor2 = tk.Entry(modificar_win)  # Campo de entrada para "Valor 2"
        entry_valor2.insert(0, ejercicio[3])  # Inserta el valor actual en el campo
        entry_valor2.grid(row=0, column=5, padx=10, pady=10)  # Coloca el campo en la ventana

        lbl_respuesta = tk.Label(modificar_win, text="Resultado")  # Etiqueta para "Resultado"
        lbl_respuesta.grid(row=1, column=0, padx=10, pady=10)  # Coloca la etiqueta
        entry_respuesta = tk.Entry(modificar_win)  # Campo de entrada para "Resultado"
        entry_respuesta.insert(0, ejercicio[4])  # Inserta el resultado actual en el campo
        entry_respuesta.grid(row=1, column=1, padx=10, pady=10)  # Coloca el campo en la ventana

        # Función para guardar cambios
        def guardar_modificacion():
            valor1 = entry_valor1.get()  # Obtiene el valor de "Valor 1"
            valor2 = entry_valor2.get()  # Obtiene el valor de "Valor 2"
            operacion = combo_operacion.get()  # Obtiene la operación seleccionada
            respuesta = entry_respuesta.get()  # Obtiene el resultado

            if not (valor1 and valor2 and operacion and respuesta):  # Verifica si todos los campos están completos
                messagebox.showwarning("Campos incompletos", "Por favor complete todos los campos.")  # Mensaje de advertencia
                return  # Sale de la función si hay campos vacíos

            try:
                valor1 = int(valor1)  # Convierte "Valor 1" a entero
                valor2 = int(valor2)  # Convierte "Valor 2" a entero
                respuesta = int(respuesta)  # Convierte el resultado a entero
            except ValueError:  # Captura error si la conversión falla
                messagebox.showerror("Error", "Los valores y el resultado deben ser números.")  # Mensaje de error
                return  # Sale de la función si hay error

            # Actualizar el ejercicio en la base de datos
            query = "UPDATE ejercicios SET valor1=%s, operacion=%s, valor2=%s, respuesta=%s WHERE id_ejercicio=%s"  # Consulta de actualización
            cursor.execute(query, (valor1, operacion, valor2, respuesta, ejercicio_id))  # Ejecuta la consulta
            conn.commit()  # Guarda los cambios en la base de datos

            messagebox.showinfo("Éxito", "Ejercicio modificado exitosamente.")  # Mensaje de éxito
            modificar_win.destroy()  # Cierra la ventana de modificación
            mostrar_ejercicios()  # Actualiza la tabla de ejercicios

        # Botón para guardar los cambios
        btn_guardar = tk.Button(modificar_win, text="Guardar cambios", command=guardar_modificacion,  bg="#008080",        
    fg="white",         
    font=('Arial', 11, 'bold'),  
    relief="raised",     
    bd=5)  # Crea el botón para guardar
        btn_guardar.grid(row=2, column=0, columnspan=2, pady=10)  # Coloca el botón en la ventana

    # Agregar filas a la tabla y botones
    for index, ejercicio in enumerate(ejercicios):  # Itera sobre todos los ejercicios
        tree.insert("", "end", values=(ejercicio[0], ejercicio[2], ejercicio[1], ejercicio[3], "=", ejercicio[4]))  # Inserta los datos en la tabla
        
        # Crear un nuevo frame para los botones
        botones_frame = tk.Frame(frame)  # Crea un marco para los botones
        botones_frame.pack(fill='x')  # Expande el marco horizontalmente

        # Crear un botón para modificar
        btn_modificar = tk.Button(botones_frame, text="Modificar", command=lambda id=ejercicio[0]: modificar_ejercicio(id), bg="#2082AA",        
    fg="white",         
    font=('Arial', 6, 'bold'))  # Botón para modificar el ejercicio
        btn_modificar.pack(side=tk.LEFT, padx=5, pady=5)  # Coloca el botón en el marco de botones

        # Crear un botón para eliminar
        btn_eliminar = tk.Button(botones_frame, text="Eliminar", command=lambda id=ejercicio[0]: eliminar_ejercicio(id), bg="#008080",        
    fg="white",         
    font=('Arial', 6, 'bold'))  # Botón para eliminar el ejercicio
        btn_eliminar.pack(side=tk.LEFT, padx=5, pady=5)  # Coloca el botón en el marco de botones

# Ventana principal
root = tk.Tk()  
root.title("Gestor de Ejercicios")  
#root.configure(bg="#E6E6FA")
# Crear un Label para el título
titulo_label = tk.Label(root, text="MathIoTica", font=('Arial', 40, 'bold'), fg="#004040")  # Estilo del título
titulo_label.pack(padx=20, pady=30)  # Coloca el Label en la ventana principal

titulo_label2 = tk.Label(root, text="Bienvenido Docente!", font=('Arial', 20, 'bold'), fg="#004040")  # Estilo del título
titulo_label2.pack(padx=20, pady=10)  # Coloca el Label en la ventana principal

# Botón para mostrar ejercicios
btn_ejercicios = tk.Button(
    root, 
    text="Ejercicios", 
    command=mostrar_ejercicios, 
    bg="#008080",        # Color de fondo
    fg="white",         # Color del texto
    font=('Arial', 16, 'bold'),  # Fuente más grande y en negrita
    relief="raised",     # Estilo del borde
    bd=5,                # Grosor del borde
    activebackground="#1E88E5"  # Color al presionar
)  
btn_ejercicios.pack(pady=20) 


btn_dashboard = tk.Button(
    root, 
    text="Dashboard", 
    command=lambda: webbrowser.open('http://127.0.0.1:5000/'),  # Abre el dashboard en el navegador
    bg="#008080",        
    fg="white",         
    font=('Arial', 16, 'bold'),  
    relief="raised",     
    bd=5,                
    activebackground="#1E88E5"  
) 
btn_dashboard.pack(pady=20) 

btn_reporte = tk.Button(
    root, 
    text="Reportes", 
    command=lambda:reportes(root, conn),  # Placeholder para el dashboard
    bg="#008080",        
    fg="white",         
    font=('Arial', 16, 'bold'),  
    relief="raised",     
    bd=5,                
    activebackground="#1E88E5"  
)  
btn_reporte.pack(pady=20) 

root.mainloop()  # Inicia el bucle de eventos de la ventana principal
