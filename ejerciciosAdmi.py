import tkinter as tk  
from tkinter import ttk, messagebox 
import mysql.connector 

# Conectar a la base de datos MySQL
conn = mysql.connector.connect(
    host="localhost",  
    user="root", 
    password="",  
    database="mathiotica" 
)
cursor = conn.cursor()  # Crea un cursor para ejecutar consultas en la base de datos

# Función para mostrar la tabla de ejercicios
def mostrar_ejercicios():
    ejercicios_win = tk.Toplevel(root)  # Crea una nueva ventana sobre la ventana principal
    ejercicios_win.title("Ejercicios")  # Título de la ventana

    # Crear un marco para la tabla y las barras de desplazamiento
    frame = tk.Frame(ejercicios_win)  # Crea un contenedor para la tabla
    frame.pack(expand=True, fill='both')  # Expande el marco y lo llena en ambas direcciones

    # Definir las columnas en el orden correcto
    cols = ("Valor 1", "Operación", "Valor 2", "=", "Resultado")  # Nombres de las columnas
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
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este ejercicio?"):  # Pregunta de confirmación
            cursor.execute("DELETE FROM ejercicios WHERE id_ejercicio = %s", (ejercicio_id,))  # Ejecuta la consulta para eliminar el ejercicio
            conn.commit()  # Guarda los cambios en la base de datos
            mostrar_ejercicios()  # Actualiza la tabla de ejercicios
            messagebox.showinfo("Éxito", "Ejercicio eliminado exitosamente.")  # Mensaje de éxito

    # Función para modificar ejercicio
    def modificar_ejercicio(ejercicio_id):
        # Crear una nueva ventana para modificar
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
        btn_guardar = tk.Button(modificar_win, text="Guardar cambios", command=guardar_modificacion)  # Crea el botón para guardar
        btn_guardar.grid(row=2, column=0, columnspan=2, pady=10)  # Coloca el botón en la ventana

    # Agregar filas a la tabla y botones
    for index, ejercicio in enumerate(ejercicios):  # Itera sobre todos los ejercicios
        tree.insert("", "end", values=(ejercicio[2], ejercicio[1], ejercicio[3], "=", ejercicio[4]))  # Inserta los datos en la tabla
        
        # Crear un nuevo frame para los botones
        botones_frame = tk.Frame(frame)  # Crea un marco para los botones
        botones_frame.pack(fill='x')  # Expande el marco horizontalmente

        # Crear un botón para modificar
        btn_modificar = tk.Button(botones_frame, text="Modificar", command=lambda id=ejercicio[0]: modificar_ejercicio(id))  # Botón para modificar el ejercicio
        btn_modificar.pack(side=tk.LEFT, padx=5, pady=5)  # Coloca el botón en el marco de botones

        # Crear un botón para eliminar
        btn_eliminar = tk.Button(botones_frame, text="Eliminar", command=lambda id=ejercicio[0]: eliminar_ejercicio(id))  # Botón para eliminar el ejercicio
        btn_eliminar.pack(side=tk.LEFT, padx=5, pady=5)  # Coloca el botón en el marco de botones

# Crear la ventana principal
root = tk.Tk()  # Crea la ventana principal
root.title("Gestor de Ejercicios Matemáticos")  # Título de la ventana

# Crear un botón que muestre la tabla de ejercicios
btn_ejercicios = tk.Button(root, text="Ejercicios", command=mostrar_ejercicios)  # Botón para mostrar ejercicios
btn_ejercicios.pack(pady=20)  # Coloca el botón en la ventana

# Función para cerrar la conexión al cerrar la ventana principal
def on_closing():
    conn.close()  # Cierra la conexión a la base de datos
    root.destroy()  # Cierra la ventana principal

# Configurar el evento de cierre de la ventana principal
root.protocol("WM_DELETE_WINDOW", on_closing)

# Iniciar el bucle de la interfaz gráfica
root.mainloop()