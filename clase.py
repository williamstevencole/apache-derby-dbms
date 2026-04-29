import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import jaydebeapi
import pickle
import atexit
import os

DERBY_CLIENT_JAR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'db-derby-10.17.1.0-bin', 'lib', 'derbyclient.jar'
)

class SQLDeveloperEmulator:
    def __init__(self, root):
        self.root = root
        self.root.title("デー タベース管理シ")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(True, True)

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#2e2e2e", foreground="white", borderwidth=0)
        style.configure("TNotebook.Tab", background="#3e3e3e", foreground="white")
        style.map("TNotebook.Tab", background=[("selected", "#1c1c1c")])

        self.conn = None
        self.connections = {}
        self.selected_connection = None
        self.selected_schema = None

        frame_izquierdo = tk.Frame(root, width=150, bg="#2e2e2e", bd=2, relief=tk.SUNKEN)
        frame_izquierdo.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(frame_izquierdo, text="Conexiones", bg="#2e2e2e", fg="white").pack(pady=5)

        self.connection_listbox = tk.Listbox(frame_izquierdo, bg="#1e1e1e", fg="white", selectbackground="#3e3e3e")
        self.connection_listbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.connection_listbox.bind('<<ListboxSelect>>', self.select_connection)

        self.agregarConexionBtn = tk.Button(frame_izquierdo, text="Crear", bg="#3e3e3e", fg="black", command=self.show_new_connection_form)
        self.agregarConexionBtn.pack(pady=2)

        self.modificarConexionBtn = tk.Button(frame_izquierdo, text="Modificar", bg="#3e3e3e", fg="black", command=self.show_modify_connection_form, state="disabled")
        self.modificarConexionBtn.pack(pady=2)

        self.eliminarConexionBtn = tk.Button(frame_izquierdo, text="Eliminar", bg="#3e3e3e", fg="black", command=self.delete_connection, state="disabled")
        self.eliminarConexionBtn.pack(pady=2)

        self.conectarBtn = tk.Button(frame_izquierdo, text="Conectar", bg="#3e3e3e", fg="black", command=self.connect_to_selected_connection, state="disabled")
        self.conectarBtn.pack(pady=2)

        self.desconectarBtn = tk.Button(frame_izquierdo, text="Desconectar", bg="#3e3e3e", fg="black", command=self.disconnect_from_connection, state="disabled")
        self.desconectarBtn.pack(pady=2)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        titulos = ["Tablas", "Indices", "Procedimientos Almacenados", "Funciones Almacenadas","Triggers", "Vistas", "Checks", "Esquemas", "Query"]
        for titulo in titulos:
            self.crear_tab(titulo)

        tk.Label(root, text="QUERY", bg="#1e1e1e", fg="white").pack(anchor=tk.W, padx=5)
        self.query_text = tk.Text(root, height=2, bg="#2e2e2e", fg="white", insertbackground="white")
        self.query_text.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(root, text="RESULTADO", bg="#1e1e1e", fg="white").pack(anchor=tk.W, padx=5)
        self.resultado_text = tk.Text(root, height=8, bg="#1e1e1e", fg="white", insertbackground="white")
        self.resultado_text.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)
        atexit.register(self.insert_connections_to_file)
        self.load_connections_from_file()

    def crear_tab(self, titulo):
        tab = ttk.Frame(self.notebook, style="TNotebook.Tab")
        self.notebook.add(tab, text=titulo)

        sub_notebook = ttk.Notebook(tab)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        if titulo == "Query":
            operations = ["Console"]
        else:
            operations = ["Listar", "Crear", "Modificar", "Borrar"]

        for operation in operations:
            sub_tab = ttk.Frame(sub_notebook)
            sub_notebook.add(sub_tab, text=operation)

            if operation == "Listar":
                btn_listar = tk.Button(sub_tab, text="Ejecutar", bg="#3e3e3e", fg="black", command=lambda t=titulo: self.list_items(t))
                btn_listar.pack(pady=5)
            elif titulo == "Tablas":
                if operation == "Crear":
                    self.create_table_form(sub_tab)
                elif operation == "Modificar":
                    self.modify_table_form(sub_tab)
                elif operation == "Borrar":
                    self.delete_table_form(sub_tab)
            elif titulo == "Indices":
                if operation == "Crear":
                    self.create_index_form(sub_tab)
                elif operation == "Modificar":
                    self.modify_index_form(sub_tab)
                elif operation == "Borrar":
                    self.delete_index_form(sub_tab)
            elif titulo == "Procedimientos Almacenados":
                if operation == "Crear":
                    self.create_stored_procedure_form(sub_tab)
                elif operation == "Modificar":
                    self.modify_stored_procedure_form(sub_tab)
                elif operation == "Borrar":
                    self.delete_stored_procedure_form(sub_tab)
            elif titulo == "Funciones Almacenadas":
                if operation == "Crear":
                    self.create_stored_function_form(sub_tab)
                elif operation == "Modificar":
                    self.show_modify_stored_function_form(sub_tab)
                elif operation == "Borrar":
                    self.delete_stored_function_form(sub_tab)
            elif titulo == "Triggers":
                if operation == "Crear":
                    self.create_trigger_form(sub_tab)
                elif operation == "Modificar":
                    self.modify_trigger_form(sub_tab)
                elif operation == "Borrar":
                    self.delete_trigger_form(sub_tab)
            elif titulo == "Vistas":
                if operation == "Crear":
                    self.create_view_form(sub_tab)
                elif operation == "Modificar":
                    self.modify_view_form(sub_tab)
                elif operation == "Borrar":
                    self.delete_view_form(sub_tab)
            elif titulo == "Checks":
                if operation == "Crear":
                    self.create_check_form(sub_tab)
                elif operation == "Modificar":
                    self.modify_check_form(sub_tab)
                elif operation == "Borrar":
                    self.delete_check_form(sub_tab)
            elif titulo == "Esquemas":
                if operation == "Crear":
                    self.create_schema_form(sub_tab)
                elif operation == "Modificar":
                    self.modify_schema_form(sub_tab)
                elif operation == "Borrar":
                    self.delete_schema_form(sub_tab)
            elif titulo == "Query":
                self.create_query_form(sub_tab)

#=======================================================================================================================
#CREATE FORMS

    def create_query_form(self, parent):
        tk.Label(parent, text="Escribe tu Query:", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        query_input = tk.Text(parent, height=5, bg="#2e2e2e", fg="white", insertbackground="white")
        query_input.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="we")

        def execute_query():

            query = query_input.get("1.0", tk.END).strip()

            if not query:
                messagebox.showerror("Error", "Debe ingresar una consulta.")
                return

            try:
                if not self.conn:
                    messagebox.showerror("Error", "Debe seleccionar una conexión para ejecutar el query.")
                    return

                print(self.schema_var.get())
                self.query_text.delete(1.0, tk.END)
                self.query_text.insert(tk.END, query)

                cursor = self.conn.cursor()
                cursor.execute(f"SET SCHEMA '{self.schema_var.get()}'")

                # Ejecutar el query
                cursor.execute(query)

                # Verificar si la consulta devuelve resultados (SELECT, VALUES, etc.)
                try:
                    results = cursor.fetchall()
                    result_text = ""

                    for row in results:
                        result_text += f"{row}\n"

                    self.resultado_text.delete(1.0, tk.END)
                    self.resultado_text.insert(tk.END, result_text if result_text else "No hay resultados para mostrar.")
                except:
                    # Si no devuelve resultados, entonces es otro tipo de consulta (INSERT, UPDATE, DELETE)
                    self.conn.commit()
                    self.resultado_text.delete(1.0, tk.END)
                    self.resultado_text.insert(tk.END, "Consulta ejecutada correctamente. Filas afectadas: {}".format(cursor.rowcount))

                cursor.close()

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al ejecutar el query: {str(e)}")

        tk.Button(parent, text="Ejecutar", command=execute_query, bg="#3e3e3e", fg="black").grid(row=2, column=0, padx=5, pady=10, sticky="e")

    def create_table_form(self, parent):
        tk.Label(parent, text="Nombre de la Tabla:", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        table_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=table_name_var, bg="#2e2e2e", fg="white").grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Ajustar el frame de las columnas para expandir en toda la página
        column_frame = tk.Frame(parent, bg="#2e2e2e")
        column_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Tabla de columnas expandida
        columns_tree = ttk.Treeview(column_frame, columns=("name", "data_type", "size", "not_null", "pk", "fk"), show="headings", height=6)
        columns_tree.grid(row=1, column=0, columnspan=6, pady=5, sticky="nsew")
        column_frame.grid_rowconfigure(1, weight=1)
        column_frame.grid_columnconfigure(0, weight=1)

        # Encabezados de las columnas
        columns_tree.heading("name", text="Nombre")
        columns_tree.heading("data_type", text="Tipo de Dato")
        columns_tree.heading("size", text="Tamaño")
        columns_tree.heading("not_null", text="Not Null")
        columns_tree.heading("pk", text="PK")
        columns_tree.heading("fk", text="FK")

        # Ajustar ancho de las columnas
        columns_tree.column("name", width=100, anchor='center')
        columns_tree.column("data_type", width=100, anchor='center')
        columns_tree.column("size", width=50, anchor='center')
        columns_tree.column("not_null", width=70, anchor='center')
        columns_tree.column("pk", width=50, anchor='center')
        columns_tree.column("fk", width=150, anchor='center')

        # Función para agregar columna
        def add_column():
            if not name_var.get() or not data_type_var.get() or (data_type_var.get() != "INT" and not size_var.get()):
                messagebox.showerror("Error", "Debe ingresar el nombre, tipo de dato y tamaño de la columna.")
                return
            fk_value = fk_var.get() if fk_var.get() else ""
            columns_tree.insert("", "end", values=(name_var.get(), data_type_var.get(), size_var.get(), "NOT NULL" if not_null_var.get() else "", "PK" if pk_var.get() else "", fk_value))

        # Función para eliminar columna
        def delete_column():
            selected_item = columns_tree.selection()
            if selected_item:
                columns_tree.delete(selected_item)

        # Entradas para los detalles de las columnas
        name_var = tk.StringVar()
        tk.Entry(column_frame, textvariable=name_var, width=15, bg="white", fg="black").grid(row=2, column=0, padx=5, pady=5)

        data_type_var = tk.StringVar()
        data_type_combobox = ttk.Combobox(column_frame, textvariable=data_type_var, values=["VARCHAR", "INT", "FLOAT"], state="readonly")
        data_type_combobox.grid(row=2, column=1, padx=5, pady=5)

        size_var = tk.StringVar()
        tk.Entry(column_frame, textvariable=size_var, width=5, bg="white", fg="black").grid(row=2, column=2, padx=5, pady=5)

        not_null_var = tk.BooleanVar()
        tk.Checkbutton(column_frame, text="Not Null", variable=not_null_var, bg="#2e2e2e", fg="white").grid(row=2, column=3, padx=5, pady=5)

        pk_var = tk.BooleanVar()
        tk.Checkbutton(column_frame, text="PK", variable=pk_var, bg="#2e2e2e", fg="white").grid(row=2, column=4, padx=5, pady=5)

        fk_var = tk.StringVar()
        tk.Entry(column_frame, textvariable=fk_var, width=15, bg="white", fg="black").grid(row=2, column=5, padx=5, pady=5)

        # Botones para agregar y eliminar columnas
        tk.Button(column_frame, text="Agregar Columna", command=add_column, bg="#3e3e3e", fg="black").grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="w")
        tk.Button(column_frame, text="Eliminar Columna", command=delete_column, bg="#3e3e3e", fg="black").grid(row=3, column=3, columnspan=3, padx=5, pady=5, sticky="e")

        # Función para crear la tabla
        def create_table():
            if not self.conn:
                messagebox.showerror("Error", "Debe seleccionar una conexión para ejecutar el DDL.")
                return

            cursor = self.conn.cursor()

            try:
                table_name = table_name_var.get()
                columns = [columns_tree.item(item, "values") for item in columns_tree.get_children()]

                ddl = f"CREATE TABLE {table_name} (\n"
                column_definitions = []
                primary_keys = []
                foreign_keys = []

                for col in columns:
                    if col[1] == "INT" or col[1] == "FLOAT":
                        column_def = f"  {col[0]} {col[1]}"
                    else:
                        column_def = f"  {col[0]} {col[1]}({col[2]})"

                    if col[3]:
                        column_def += " NOT NULL"
                    if col[4] == "PK":
                        primary_keys.append(col[0])
                    if col[5]:
                        foreign_keys.append((col[0], col[5]))

                    column_definitions.append(column_def)

                # Agregar definición de llaves primarias
                if primary_keys:
                    column_definitions.append(f"  PRIMARY KEY ({', '.join(primary_keys)})")

                # Agregar definición de llaves foráneas
                for fk in foreign_keys:
                    column_definitions.append(f"  FOREIGN KEY ({fk[0]}) REFERENCES {fk[1]}")

                ddl += ",\n".join(column_definitions) + "\n)"

                # Mostrar el DDL en el cuadro de texto de consulta
                self.query_text.delete(1.0, tk.END)
                self.query_text.insert(tk.END, ddl)

                # Ejecutar la consulta para crear la tabla
                cursor.execute(ddl)
                self.conn.commit()

                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Tabla '{table_name}' creada exitosamente.")

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al crear la tabla: {str(e)}")

            finally:
                cursor.close()

        # Botones OK y Cancelar
        tk.Button(parent, text="OK", command=create_table, bg="#3e3e3e", fg="black").grid(row=4, column=0, padx=5, pady=10, sticky="e")
        tk.Button(parent, text="Cancelar", command=parent.quit, bg="#3e3e3e", fg="black").grid(row=4, column=1, padx=5, pady=10, sticky="w")



    def update_schema(self):
        if self.selected_connection:
            connection_info = self.connections[self.selected_connection]
            schema = connection_info.get("schema", "")
            self.schema_var.set(schema)

    def create_trigger_form(self, parent):
        tk.Label(parent, text="Crear Trigger", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=2, pady=2)

        tk.Label(parent, text="Nombre:", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=2, pady=2, sticky="e")
        trigger_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=trigger_name_var, width=10, bg="#4a4a4a", fg="white").grid(row=2, column=1, padx=2, pady=2)

        self.schema_var = tk.StringVar()

        tk.Label(parent, text="Esquema:", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=2, pady=2, sticky="e")
        tk.Entry(parent, textvariable=self.schema_var, width=10, bg="#4a4a4a", fg="white",  state="readonly").grid(row=1, column=1, padx=2, pady=2)

        tk.Label(parent, text="Base Type:", bg="#2e2e2e", fg="white").grid(row=3, column=0, padx=2, pady=2, sticky="e")
        base_type_var = tk.StringVar()
        base_type_combobox = ttk.Combobox(parent, textvariable=base_type_var, values=["TABLE"], width=8, state="readonly")
        base_type_combobox.grid(row=3, column=1, padx=2, pady=2)

        tk.Label(parent, text="Objeto (Tabla):", bg="#2e2e2e", fg="white").grid(row=4, column=0, padx=2, pady=2, sticky="e")
        base_object_var = tk.StringVar()
        tk.Entry(parent, textvariable=base_object_var, width=10, bg="#4a4a4a", fg="white").grid(row=4, column=1, padx=2, pady=2)

        tk.Label(parent, text="Timing:", bg="#2e2e2e", fg="white").grid(row=5, column=0, padx=2, pady=2, sticky="e")
        timing_var = tk.StringVar()
        timing_combobox = ttk.Combobox(parent, textvariable=timing_var, values=["AFTER"], width=8, state="readonly")
        timing_combobox.grid(row=5, column=1, padx=2, pady=2)

        tk.Label(parent, text="Eventos:", bg="#2e2e2e", fg="white").grid(row=6, column=0, padx=2, pady=2, sticky="e")
        event_var = tk.StringVar()
        available_events = ttk.Combobox(parent, textvariable=event_var, values=["INSERT", "UPDATE", "DELETE"], width=8, state="readonly")
        available_events.grid(row=6, column=1, padx=2, pady=2)

        tk.Label(parent, text="Referenciar Old:", bg="#2e2e2e", fg="white").grid(row=7, column=0, padx=2, pady=2, sticky="e")
        referencing_old_var = tk.StringVar()
        tk.Entry(parent, textvariable=referencing_old_var, width=10, bg="#4a4a4a", fg="white").grid(row=7, column=1, padx=2, pady=2)

        tk.Label(parent, text="Referenciar New:", bg="#2e2e2e", fg="white").grid(row=8, column=0, padx=2, pady=2, sticky="e")
        referencing_new_var = tk.StringVar()
        tk.Entry(parent, textvariable=referencing_new_var, width=10, bg="#4a4a4a", fg="white").grid(row=8, column=1, padx=2, pady=2)

        statement_level_var = tk.BooleanVar()
        tk.Checkbutton(parent, text="Nivel Sentencia", variable=statement_level_var, bg="#2e2e2e", fg="white").grid(row=9, column=1, sticky="w", padx=2, pady=2)

        tk.Label(parent, text="SQL Body:", bg="#2e2e2e", fg="white").grid(row=10, column=0, padx=2, pady=2, sticky="e")
        sql_body_text = tk.Text(parent, height=3, width=25, bg="#4a4a4a", fg="white")
        sql_body_text.grid(row=10, column=1, padx=2, pady=2)

        def create_trigger():
            trigger_name = trigger_name_var.get()
            timing = timing_var.get()
            base_object = base_object_var.get()
            selected_event = event_var.get()
            sql_body = sql_body_text.get("1.0", tk.END).strip()
            old_ref = referencing_old_var.get()
            new_ref = referencing_new_var.get()

            if not trigger_name or not base_object or not timing or not selected_event:
                messagebox.showerror("Error", "Por favor completa todos los campos.")
                return

            ddl = f"CREATE TRIGGER {trigger_name} {timing} {selected_event} ON {base_object}\n"

            referencing_clause = []
            if old_ref and selected_event in ["UPDATE", "DELETE"]:
                referencing_clause.append(f"OLD AS {old_ref}")
            if new_ref and selected_event in ["UPDATE", "INSERT"]:
                referencing_clause.append(f"NEW AS {new_ref}")

            if referencing_clause:
                ddl += f"REFERENCING {' '.join(referencing_clause)}\n"

            ddl += f"FOR EACH {'STATEMENT' if statement_level_var.get() else 'ROW'}\n"
            ddl += f"{sql_body}"

            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, ddl)

            if not self.conn:
                messagebox.showerror("Error", "Debe seleccionar una conexión para ejecutar el DDL.")
                return

            cursor = self.conn.cursor()
            try:
                cursor.execute(ddl)
                self.conn.commit()

                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Trigger '{trigger_name}' creado exitosamente.")

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al crear el trigger: {str(e)}")

            cursor.close()

        tk.Button(parent, text="Crear Trigger", command=create_trigger, bg="#3e3e3e", fg="black").grid(row=11, column=1, padx=2, pady=2)

    def create_view_form(self, parent):
        tk.Label(parent, text="Crear Vista", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        tk.Label(parent, text="Nombre de la Vista:", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        view_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=view_name_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=5, pady=5, sticky="we")

        tk.Label(parent, text="SQL Query:", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        query_input = tk.Text(parent, height=10, bg="#2e2e2e", fg="white", insertbackground="white")
        query_input.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="we")

        def check_syntax():
            query = query_input.get("1.0", tk.END).strip()
            if not query.lower().startswith("select"):
                messagebox.showerror("Error", "La consulta debe comenzar con una instrucción SELECT.")
                return
            messagebox.showinfo("Sintaxis", "La sintaxis parece correcta.")

        def create_view():
            view_name = view_name_var.get()
            query = query_input.get("1.0", tk.END).strip()

            if not view_name or not query:
                messagebox.showerror("Error", "Debe proporcionar el nombre de la vista y la consulta SQL.")
                return

            ddl = f"CREATE VIEW {view_name} AS {query}"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, ddl)

            try:
                cursor = self.conn.cursor()
                cursor.execute(ddl)
                self.conn.commit()
                cursor.close()
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Vista '{view_name}' creada exitosamente.")
            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al crear la vista: {str(e)}")

        tk.Button(parent, text="Check Syntax", command=check_syntax, bg="#3e3e3e", fg="black").grid(row=4, column=0, padx=5, pady=10, sticky="e")

        tk.Button(parent, text="Crear Vista", command=create_view, bg="#3e3e3e", fg="black").grid(row=4, column=1, padx=5, pady=10, sticky="w")


    def create_check_form(self, parent):
        tk.Label(parent, text="Crear CHECK Constraint", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Seleccionar Tabla:", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        table_name_var = tk.StringVar()
        table_combobox = ttk.Combobox(parent, textvariable=table_name_var, state="readonly")
        table_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        def load_tables():
            tables = self.get_tables()
            if tables:
                table_combobox['values'] = tables

        tk.Button(parent, text="Cargar Tablas", command=load_tables, bg="#3e3e3e", fg="black").grid(row=1, column=2, padx=5, pady=5)

        tk.Label(parent, text="Nombre de la Columna:", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        column_name_var = tk.StringVar()
        column_name_entry = tk.Entry(parent, textvariable=column_name_var, bg="#2e2e2e", fg="white")
        column_name_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(parent, text="Nombre de la Restricción:", bg="#2e2e2e", fg="white").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        constraint_name_var = tk.StringVar()
        constraint_name_entry = tk.Entry(parent, textvariable=constraint_name_var, bg="#2e2e2e", fg="white")
        constraint_name_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        tk.Label(parent, text="Condición del CHECK:", bg="#2e2e2e", fg="white").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        check_condition_var = tk.StringVar()
        tk.Entry(parent, textvariable=check_condition_var, bg="#2e2e2e", fg="white").grid(row=4, column=1, padx=5, pady=5, sticky="w")

        def create_check():
            table_name = table_name_var.get()
            column_name = column_name_var.get()
            constraint_name = constraint_name_var.get()
            check_condition = check_condition_var.get()

            if not table_name or not column_name or not constraint_name or not check_condition:
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
                return

            ddl = f"""
            ALTER TABLE {table_name}
            ADD CONSTRAINT {constraint_name} CHECK ({check_condition})
            """
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, ddl)

            try:
                cursor = self.conn.cursor()
                cursor.execute(ddl)
                self.conn.commit()
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"CHECK Constraint '{constraint_name}' añadida exitosamente.")
                cursor.close()
            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al añadir la CHECK Constraint: {str(e)}")

        tk.Button(parent, text="Crear CHECK", command=create_check, bg="#3e3e3e", fg="black").grid(row=5, column=1, padx=5, pady=10, sticky="e")

    def get_tables(self):
        if not self.conn:
            messagebox.showerror("Error", "Debe seleccionar una conexión para cargar las tablas.")
            return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT TABLENAME FROM SYS.SYSTABLES WHERE TABLETYPE='T'")
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return tables
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar las tablas: {str(e)}")
            return []

    def create_schema_form(self, parent):
        tk.Label(parent, text="Crear Esquema", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Nombre del Esquema:", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        schema_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=schema_name_var, bg="#4a4a4a", fg="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Label(parent, text="Usuario Autorizado (Opcional):", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        user_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=user_name_var, bg="#4a4a4a", fg="white").grid(row=2, column=1, padx=5, pady=5)

        def create_schema():
            schema_name = schema_name_var.get()
            user_name = user_name_var.get()

            if not schema_name:
                messagebox.showerror("Error", "El nombre del esquema es obligatorio.")
                return

            if user_name:
                query = f"CREATE SCHEMA {schema_name} AUTHORIZATION {user_name}"
            else:
                query = f"CREATE SCHEMA {schema_name}"

            if not self.conn:
                messagebox.showerror("Error", "Debe seleccionar una conexión para ejecutar el DDL.")
                return

            try:
                cursor = self.conn.cursor()
                self.query_text.delete(1.0, tk.END)
                self.query_text.insert(tk.END, query)
                cursor.execute(query)
                self.conn.commit()

                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Esquema '{schema_name}' creado exitosamente.")
                cursor.close()
            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al crear el esquema: {str(e)}")

        tk.Button(parent, text="Crear Esquema", bg="#3e3e3e", fg="black", command=create_schema).grid(row=3, column=0, columnspan=2, pady=10)

#=======================================================================================================================
#MODIFY-FORMS
    def modify_table_form(self, parent):
        tk.Label(parent, text="Seleccione la Tabla:", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        table_name_var = tk.StringVar()
        table_name_combobox = ttk.Combobox(parent, textvariable=table_name_var, state="readonly")
        table_name_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Button(parent, text="Cargar Tablas", command=lambda: self.load_tables(table_name_combobox), bg="#3e3e3e", fg="black").grid(row=0, column=2, padx=5, pady=5)

        ddl_frame = tk.Frame(parent, bg="#2e2e2e")
        ddl_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        ddl_text = tk.Text(ddl_frame, height=10, bg="#1e1e1e", fg="white", insertbackground="white")
        ddl_text.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        def load_table_ddl():

            table_name = table_name_var.get()
            schema_name = self.schema_var.get()

            if not table_name:
                messagebox.showerror("Error", "Debe seleccionar una tabla.")
                return

            try:
                cursor = self.conn.cursor()

                query = f"""
                SELECT C.COLUMNNAME,
                    CASE
                        WHEN CAST(C.COLUMNDATATYPE AS VARCHAR(128)) = 'VARCHAR' THEN 'VARCHAR(' || C.COLUMNDATATYPE || ')'
                        WHEN CAST(C.COLUMNDATATYPE AS VARCHAR(128)) = 'CHAR' THEN 'CHAR(' || C.COLUMNDATATYPE || ')'
                        WHEN CAST(C.COLUMNDATATYPE AS VARCHAR(128)) = 'INTEGER' THEN 'INT'
                        WHEN CAST(C.COLUMNDATATYPE AS VARCHAR(128)) = 'DOUBLE' THEN 'DOUBLE PRECISION'
                        ELSE CAST(C.COLUMNDATATYPE AS VARCHAR(128))
                    END AS COLUMNDATATYPE,
                    C.COLUMNDEFAULT,
                    CASE WHEN C.AUTOINCREMENTVALUE IS NOT NULL THEN 'AUTO_INCREMENT' ELSE '' END AS AUTOINCREMENT
                FROM SYS.SYSSCHEMAS S
                JOIN SYS.SYSTABLES T ON S.SCHEMAID = T.SCHEMAID
                JOIN SYS.SYSCOLUMNS C ON T.TABLEID = C.REFERENCEID
                WHERE CAST(S.SCHEMANAME AS VARCHAR(128)) = '{schema_name.upper()}'
                AND CAST(T.TABLENAME AS VARCHAR(128)) = '{table_name.upper()}'
                """
                cursor.execute(query)
                columns = cursor.fetchall()

                ddl = f"CREATE TABLE {schema_name}.{table_name} (\n"
                column_definitions = []
                for column in columns:
                    column_name = column[0]
                    column_type = column[1]
                    auto_increment = column[3]
                    column_def = f"    {column_name} {column_type}"
                    if auto_increment:
                        column_def += f" {auto_increment}"
                    column_definitions.append(column_def)
                ddl += ",\n".join(column_definitions) + "\n)"

                ddl_text.delete(1.0, tk.END)
                ddl_text.insert(tk.END, ddl)

                cursor.close()

            except Exception as e:
                ddl_text.delete(1.0, tk.END)
                ddl_text.insert(tk.END, f"Error al cargar el DDL de la tabla: {str(e)}")

        tk.Button(parent, text="Cargar DDL", command=load_table_ddl, bg="#3e3e3e", fg="black").grid(row=2, column=2, padx=5, pady=5)

        def execute_ddl():

            #get the table name from the ddl
            nombretabla = ddl_text.get(1.0, tk.END).strip()
            nombretabla = nombretabla.split(" ")[2]
            nombretabla = nombretabla.split(".")[1]
            print(nombretabla)

            try:
                cursor = self.conn.cursor()

                table_name = table_name_var.get()
                schema_name = self.schema_var.get()

                if not table_name or not schema_name:
                    messagebox.showerror("Error", "Debe seleccionar una tabla y un esquema.")
                    return

                ddl = ddl_text.get(1.0, tk.END).strip()

                if not ddl.startswith(f"CREATE TABLE {schema_name}.{table_name}"):
                    messagebox.showerror("Error", "El DDL no coincide con la tabla seleccionada.")
                    return

                print(table_name_combobox.get())

                if table_name_combobox.get() != nombretabla:
                    messagebox.showerror("Error", "El nombre de la tabla no coincide con el nombre del DDL proporcionado.")
                    return

                drop_query = f"DROP TABLE {schema_name}.{table_name}"
                try:
                    cursor.execute(drop_query)
                    self.conn.commit()
                    self.resultado_text.delete(1.0, tk.END)
                except Exception as e:
                    self.resultado_text.delete(1.0, tk.END)
                    self.resultado_text.insert(tk.END, f"Advertencia: No se pudo eliminar la tabla o no existe: {str(e)}\n")

                self.query_text.delete(1.0, tk.END)
                self.query_text.insert(tk.END, ddl)

                cursor.execute(ddl)
                self.conn.commit()

                self.resultado_text.insert(tk.END, "DDL ejecutado exitosamente.")

                cursor.close()

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al ejecutar el DDL: {str(e)}")

        tk.Button(parent, text="Ejecutar DDL", command=execute_ddl, bg="#3e3e3e", fg="black").grid(row=4, column=0, padx=5, pady=10, sticky="e")
        tk.Button(parent, text="Cancelar", command=parent.quit, bg="#3e3e3e", fg="black").grid(row=4, column=1, padx=5, pady=10, sticky="w")

    def load_tables(self, table_combobox):
        """Carga las tablas disponibles en la base de datos en el combobox."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT TABLENAME FROM SYS.SYSTABLES WHERE TABLETYPE='T'")
            tables = cursor.fetchall()

            table_combobox['values'] = [table[0] for table in tables]
            if tables:
                table_combobox.current(0)

            cursor.close()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar las tablas: {str(e)}")

    def modify_trigger_form(self, parent):
            tk.Label(parent, text="Modificar Trigger", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

            # Label y ComboBox para seleccionar el trigger
            tk.Label(parent, text="Nombre del Trigger:", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
            trigger_name_var = tk.StringVar()
            trigger_combobox = ttk.Combobox(parent, textvariable=trigger_name_var, state="readonly")
            trigger_combobox.grid(row=1, column=1, padx=5, pady=5)

            # Botón para cargar los triggers
            tk.Button(parent, text="Cargar Triggers", command=lambda: self.load_triggers(trigger_combobox), bg="#3e3e3e", fg="black").grid(row=1, column=2, padx=5, pady=5)

            # Textbox para mostrar el DDL del trigger
            tk.Label(parent, text="Definición del Trigger (DDL):", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=5, pady=5, sticky="w")
            ddl_text = tk.Text(parent, height=10, bg="#2e2e2e", fg="white", insertbackground="white")
            ddl_text.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="we")

        # Función para cargar el DDL del trigger seleccionado
            def load_trigger_ddl():
                trigger_name = trigger_name_var.get()
                if not trigger_name:
                    messagebox.showerror("Error", "Debe seleccionar un trigger.")
                    return

                try:
                    cursor = self.conn.cursor()
                    query = f"SELECT TRIGGERDEFINITION FROM SYS.SYSTRIGGERS WHERE TRIGGERNAME = '{trigger_name}'"
                    cursor.execute(query)
                    ddl = cursor.fetchone()[0]

                    # Mostrar el DDL en el textbox
                    ddl_text.delete(1.0, tk.END)
                    ddl_text.insert(tk.END, ddl)
                    cursor.close()

                except Exception as e:
                    ddl_text.delete(1.0, tk.END)
                    ddl_text.insert(tk.END, f"Error al cargar el DDL del trigger: {str(e)}")

            # Botón para cargar el DDL del trigger seleccionado
            tk.Button(parent, text="Cargar DDL", command=load_trigger_ddl, bg="#3e3e3e", fg="black").grid(row=4, column=1, padx=5, pady=10, sticky="e")

            def modify_trigger():
                ddl = ddl_text.get("1.0", tk.END).strip()
                if not ddl:
                    messagebox.showerror("Error", "Debe ingresar el DDL del trigger.")
                    return

                try:
                    cursor = self.conn.cursor()

                    # Ejecutar el DDL modificado
                    cursor.execute(ddl)
                    self.conn.commit()

                    self.resultado_text.delete(1.0, tk.END)
                    self.resultado_text.insert(tk.END, f"Trigger '{trigger_name_var.get()}' modificado exitosamente.")

                    cursor.close()

                except Exception as e:
                    self.resultado_text.delete(1.0, tk.END)
                    self.resultado_text.insert(tk.END, f"Error al modificar el trigger: {str(e)}")

            tk.Button(parent, text="Modificar Trigger", command=modify_trigger, bg="#3e3e3e", fg="black").grid(row=5, column=1, padx=5, pady=10, sticky="e")



    def load_triggers(self, combobox):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT TRIGGERNAME FROM SYS.SYSTRIGGERS")
            triggers = [row[0] for row in cursor.fetchall()]
            cursor.close()

            # Cargar los triggers en el ComboBox
            combobox["values"] = triggers

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los triggers: {str(e)}")


    def modify_check_form(self, parent):
        tk.Label(parent, text="Modificar CHECK Constraint", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        # Seleccionar tabla
        tk.Label(parent, text="Seleccionar Tabla:", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        table_name_var = tk.StringVar()
        table_combobox = ttk.Combobox(parent, textvariable=table_name_var, values=[], state="readonly")
        table_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Botón para cargar tablas
        tk.Button(parent, text="Cargar Tablas", command=lambda: self.load_tables(table_combobox), bg="#3e3e3e", fg="black").grid(row=1, column=2, padx=5, pady=5)

        # Seleccionar CHECK constraint
        tk.Label(parent, text="Seleccionar CHECK Constraint:", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        check_name_var = tk.StringVar()
        check_combobox = ttk.Combobox(parent, textvariable=check_name_var, values=[], state="readonly")
        check_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Button(parent, text="Cargar CHECKs", command=lambda: load_checks(table_name_var.get(), check_combobox), bg="#3e3e3e", fg="black").grid(row=2, column=2, padx=5, pady=5)

        # Cambiar nombre del CHECK
        tk.Label(parent, text="Nuevo Nombre del CHECK:", bg="#2e2e2e", fg="white").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        new_check_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=new_check_name_var, bg="#2e2e2e", fg="white").grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Modificar la condición del CHECK
        tk.Label(parent, text="Nueva Condición del CHECK:", bg="#2e2e2e", fg="white").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        new_check_condition_var = tk.StringVar()
        tk.Entry(parent, textvariable=new_check_condition_var, bg="#2e2e2e", fg="white").grid(row=4, column=1, padx=5, pady=5, sticky="w")

        def load_checks(table_name, check_combobox):
            if not table_name:
                messagebox.showerror("Error", "Debe seleccionar una tabla primero.")
                return

            try:
                cursor = self.conn.cursor()

                query = f"""
                SELECT c.CONSTRAINTNAME
                FROM SYS.SYSCONSTRAINTS c
                JOIN SYS.SYSCHECKS ch ON c.CONSTRAINTID = ch.CONSTRAINTID
                WHERE c.TABLEID IN (SELECT t.TABLEID FROM SYS.SYSTABLES t WHERE t.TABLENAME='{table_name}')
                """

                cursor.execute(query)
                checks = [row[0] for row in cursor.fetchall()]
                check_combobox['values'] = checks
                cursor.close()
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar los CHECKs: {str(e)}")

        def modify_check():
            table_name = table_name_var.get()
            check_name = check_name_var.get()
            new_check_name = new_check_name_var.get()
            new_condition = new_check_condition_var.get()

            if not table_name or not check_name or not new_check_name or not new_condition:
                messagebox.showerror("Error", "Debe completar todos los campos.")
                return

            # Drop the old CHECK and add the new one
            ddl_drop = f"ALTER TABLE {table_name} DROP CONSTRAINT {check_name}"
            ddl_add = f"ALTER TABLE {table_name} ADD CONSTRAINT {new_check_name} CHECK ({new_condition})"

            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, f"{ddl_drop};\n{ddl_add};")

            try:
                cursor = self.conn.cursor()
                cursor.execute(ddl_drop)
                cursor.execute(ddl_add)
                self.conn.commit()
                cursor.close()

                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"CHECK Constraint '{new_check_name}' modificada exitosamente.")

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al modificar la CHECK Constraint: {str(e)}")

        tk.Button(parent, text="Modificar CHECK", command=modify_check, bg="#3e3e3e", fg="black").grid(row=5, column=1, padx=5, pady=10, sticky="e")


    def modify_view_form(self, parent):
        tk.Label(parent, text="Modificar Vista", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        view_name_var = tk.StringVar()
        view_combobox = ttk.Combobox(parent, textvariable=view_name_var, state="readonly")
        view_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        def load_views():
            views = self.get_views()
            if views:
                view_combobox["values"] = views
            else:
                view_combobox["values"] = []

        tk.Button(parent, text="Cargar Vistas", command=load_views, bg="#3e3e3e", fg="black").grid(row=1, column=1, padx=5, pady=5)

        tk.Label(parent, text="Consulta SQL de la Vista:", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        query_text = tk.Text(parent, height=5, bg="#2e2e2e", fg="white", insertbackground="white")
        query_text.grid(row=2, column=1, padx=5, pady=5, sticky="we")


        def load_view_ddl():
            view_name = view_name_var.get()
            if not view_name:
                messagebox.showerror("Error", "Debe seleccionar una vista.")
                return

            try:
                cursor = self.conn.cursor()
                cursor.execute(f"SELECT V.VIEWDEFINITION FROM SYS.SYSVIEWS V JOIN SYS.SYSTABLES T ON V.TABLEID = T.TABLEID WHERE T.TABLENAME = '{view_name}'")
                result = cursor.fetchone()

                if result:
                    query_text.delete(1.0, tk.END)
                    query_text.insert(tk.END, result[0])
                else:
                    messagebox.showerror("Error", "No se pudo cargar el DDL de la vista.")
                cursor.close()

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al cargar el DDL: {str(e)}")


        def modify_view():
            view_name = view_name_var.get()
            modified_query = query_text.get("1.0", tk.END).strip()

            if not view_name or not modified_query:
                messagebox.showerror("Error", "Debe completar los campos de nombre y consulta SQL.")
                return

            nombrevista = modified_query.split(" ")[2]

            if nombrevista.upper() != view_combobox.get():
                messagebox.showerror("Error", "El nombre de la vista no coincide con el nombre seleccionado.")
                return

            try:
                cursor = self.conn.cursor()
                cursor.execute(f"DROP VIEW {view_name}")
                cursor.execute(modified_query)
                self.conn.commit()

                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Vista '{view_name}' modificada exitosamente.")
                cursor.close()

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al modificar la vista: {str(e)}")

        # Button to load the view DDL
        tk.Button(parent, text="Cargar DDL", command=load_view_ddl, bg="#3e3e3e", fg="black").grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Button to modify the view
        tk.Button(parent, text="Modificar Vista", command=modify_view, bg="#3e3e3e", fg="black").grid(row=4, column=1, padx=5, pady=10, sticky="w")

    def get_views(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT TABLENAME FROM SYS.SYSTABLES WHERE TABLETYPE='V'")
            views = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return views
        except Exception as e:
            if hasattr(self, 'resultado_text'):
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al obtener las vistas: {str(e)}")
            else:
                messagebox.showerror("Error", f"Error al obtener las vistas: {str(e)}")
            return []



    def modify_schema_form(self, parent):
            # Título del formulario
        tk.Label(parent, text="Modificar Permisos", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        # ComboBox para seleccionar el esquema
        tk.Label(parent, text="Seleccionar Esquema:", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        schema_name_var = tk.StringVar()
        schema_combobox = ttk.Combobox(parent, textvariable=schema_name_var, state="readonly", width=30)
        schema_combobox.grid(row=1, column=1, padx=5, pady=5)

        # Botón para cargar los esquemas en el ComboBox
        tk.Button(parent, text="Cargar Esquemas", bg="#3e3e3e", fg="black", command=lambda: self.populate_schemas_combobox(schema_combobox)).grid(row=2, column=0, columnspan=2, pady=10)

        # Campo para ingresar el nombre del usuario
        tk.Label(parent, text="Usuario:", bg="#2e2e2e", fg="white").grid(row=3, column=0, padx=5, pady=5)
        user_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=user_name_var, bg="#4a4a4a", fg="white").grid(row=3, column=1, padx=5, pady=5)

        # Lista de permisos a otorgar o revocar
        tk.Label(parent, text="Seleccionar Permisos:", bg="#2e2e2e", fg="white").grid(row=4, column=0, padx=5, pady=5)
        permissions_var = tk.StringVar()
        permissions_combobox = ttk.Combobox(parent, textvariable=permissions_var, state="readonly", width=30, values=["SELECT", "INSERT", "UPDATE", "DELETE"])
        permissions_combobox.grid(row=4, column=1, padx=5, pady=5)

        # Seleccionar acción: GRANT o REVOKE
        tk.Label(parent, text="Acción:", bg="#2e2e2e", fg="white").grid(row=5, column=0, padx=5, pady=5)
        action_var = tk.StringVar()
        action_combobox = ttk.Combobox(parent, textvariable=action_var, state="readonly", width=30, values=["GRANT", "REVOKE"])
        action_combobox.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(parent, text="Tabla:", bg="#2e2e2e", fg="white").grid(row=6, column=0, padx=5, pady=5)
        table_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=table_name_var, bg="#4a4a4a", fg="white").grid(row=6, column=1, padx=5, pady=5)

        # Función para otorgar o revocar permisos
        def modify_permissions():
            schema_name = schema_name_var.get()
            user_name = user_name_var.get()
            permission = permissions_var.get()
            action = action_var.get()
            table_name = table_name_var.get()

            if not schema_name or not user_name or not permission or not action or not table_name:
                messagebox.showerror("Error", "Debe completar todos los campos obligatorios.")
                return

            if table_name:
                if action == "GRANT":
                    query = f'GRANT {permission} ON {table_name} TO "{user_name.upper()}"'
                elif action == "REVOKE":
                    query = f'REVOKE {permission} ON {table_name} FROM "{user_name.upper()}"'

            if not self.conn:
                messagebox.showerror("Error", "Debe seleccionar una conexión para ejecutar el DDL.")
                return

            # Ejecutar la consulta
            try:
                cursor = self.conn.cursor()
                self.query_text.delete(1.0, tk.END)
                self.query_text.insert(tk.END, query)
                cursor.execute(query)
                self.conn.commit()

                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Permiso '{permission}' {action.lower()}ado exitosamente para el usuario '{user_name}'.")
                cursor.close()
            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al {action.lower()} permisos: {str(e)}")

        # Botón para aplicar los cambios de permisos
        tk.Button(parent, text="Aplicar Permisos", bg="#3e3e3e", fg="black", command=modify_permissions).grid(row=7, column=0, columnspan=2, pady=10)



#=======================================================================================================================
#DELETE-FORMS
    def delete_table_form(self, parent):
        tk.Label(parent, text="Eliminar Tabla", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        table_frame = tk.Frame(parent, bg="#2e2e2e")
        table_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        tk.Label(parent, text="Seleccione una tabla:", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)

        selected_table_var = tk.StringVar()
        self.table_combobox = ttk.Combobox(parent, textvariable=selected_table_var, state="readonly")
        self.table_combobox.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(parent, text="Cargar Tablas", command=lambda: self.load_tables(self.table_combobox), bg="#3e3e3e", fg="black").grid(row=2, column=1, padx=5, pady=5)

        def delete_table():
            table_name = selected_table_var.get()

            if not table_name:
                messagebox.showerror("Error", "Debe seleccionar una tabla para eliminar.")
                return

            try:
                cursor = self.conn.cursor()
                ddl = f"DROP TABLE {table_name}"
                self.query_text.delete(1.0, tk.END)
                self.query_text.insert(tk.END, ddl)
                cursor.execute(ddl)
                self.conn.commit()

                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Tabla '{table_name}' eliminada exitosamente.")

                cursor.close()

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al eliminar la tabla: {str(e)}")

        tk.Button(parent, text="Eliminar", command=delete_table, bg="#3e3e3e", fg="black").grid(row=3, column=0, padx=5, pady=10, sticky="e")
        tk.Button(parent, text="Cancelar", command=parent.quit, bg="#3e3e3e", fg="black").grid(row=3, column=1, padx=5, pady=10, sticky="w")


    def load_tables(self, table_combobox):
        """Carga las tablas disponibles en la base de datos en el combobox."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT tablename FROM sys.systables WHERE tabletype='T'")
            tables = cursor.fetchall()

            table_combobox['values'] = [table[0] for table in tables]
            if tables:
                table_combobox.current(0)

            cursor.close()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar las tablas: {str(e)}")


    def delete_trigger_form(self, parent):
        tk.Label(parent, text="Borrar Trigger", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        # Label y ComboBox para seleccionar el trigger a borrar
        tk.Label(parent, text="Nombre del Trigger:", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        trigger_name_var = tk.StringVar()
        trigger_combobox = ttk.Combobox(parent, textvariable=trigger_name_var, state="readonly")
        trigger_combobox.grid(row=1, column=1, padx=5, pady=5)

        # Botón para cargar los triggers disponibles
        tk.Button(parent, text="Cargar Triggers", command=lambda: self.load_triggers(trigger_combobox), bg="#3e3e3e", fg="black").grid(row=1, column=2, padx=5, pady=5)

        # Función para eliminar el trigger seleccionado
        def delete_trigger():
            trigger_name = trigger_name_var.get()
            if not trigger_name:
                messagebox.showerror("Error", "Debe seleccionar un trigger.")
                return

            confirm = messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar el trigger '{trigger_name}'?")
            if not confirm:
                return

            try:
                cursor = self.conn.cursor()
                query = f"DROP TRIGGER {trigger_name}"
                cursor.execute(query)
                self.conn.commit()

                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Trigger '{trigger_name}' eliminado exitosamente.")

                self.load_triggers(trigger_combobox)

                cursor.close()

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al eliminar el trigger: {str(e)}")


        tk.Button(parent, text="Borrar Trigger", command=delete_trigger, bg="#3e3e3e", fg="black").grid(row=2, column=1, padx=5, pady=10, sticky="e")


    def delete_check_form(self, parent):
        tk.Label(parent, text="Borrar CHECK Constraint", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        # Seleccionar tabla
        tk.Label(parent, text="Seleccionar Tabla:", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        table_name_var = tk.StringVar()
        table_combobox = ttk.Combobox(parent, textvariable=table_name_var, values=[], state="readonly")
        table_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Botón para cargar tablas
        tk.Button(parent, text="Cargar Tablas", command=lambda: self.load_tables(table_combobox), bg="#3e3e3e", fg="black").grid(row=1, column=2, padx=5, pady=5)

        # Seleccionar CHECK constraint
        tk.Label(parent, text="Seleccionar CHECK Constraint:", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        check_name_var = tk.StringVar()
        check_combobox = ttk.Combobox(parent, textvariable=check_name_var, values=[], state="readonly")
        check_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Button(parent, text="Cargar CHECKs", command=lambda: load_checks(table_name_var.get(), check_combobox), bg="#3e3e3e", fg="black").grid(row=2, column=2, padx=5, pady=5)

        def load_checks(table_name, check_combobox):
            if not table_name:
                messagebox.showerror("Error", "Debe seleccionar una tabla primero.")
                return

            try:
                cursor = self.conn.cursor()

                query = f"""
                SELECT c.CONSTRAINTNAME
                FROM SYS.SYSCONSTRAINTS c
                JOIN SYS.SYSCHECKS ch ON c.CONSTRAINTID = ch.CONSTRAINTID
                WHERE c.TABLEID IN (SELECT t.TABLEID FROM SYS.SYSTABLES t WHERE t.TABLENAME='{table_name}')
                """

                cursor.execute(query)
                checks = [row[0] for row in cursor.fetchall()]
                check_combobox['values'] = checks
                cursor.close()
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar los CHECKs: {str(e)}")

        def delete_check():
            table_name = table_name_var.get()
            check_name = check_name_var.get()

            if not table_name or not check_name:
                messagebox.showerror("Error", "Debe seleccionar una tabla y un CHECK constraint.")
                return

            ddl_drop = f"ALTER TABLE {table_name} DROP CONSTRAINT {check_name}"

            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, ddl_drop)

            try:
                cursor = self.conn.cursor()
                cursor.execute(ddl_drop)
                self.conn.commit()
                cursor.close()

                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"CHECK Constraint '{check_name}' eliminada exitosamente.")

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al eliminar la CHECK Constraint: {str(e)}")

        tk.Button(parent, text="Borrar CHECK", command=delete_check, bg="#3e3e3e", fg="black").grid(row=3, column=1, padx=5, pady=10, sticky="e")


    def delete_view_form(self, parent):
        tk.Label(parent, text="Borrar Vista", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Seleccionar Vista:", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky="e")


        view_name_var = tk.StringVar()

        view_combobox = ttk.Combobox(parent, textvariable=view_name_var, values=[], state="readonly")
        view_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Button(parent, text="Cargar Vistas", command=lambda: self.load_views(view_combobox), bg="#3e3e3e", fg="black").grid(row=1, column=2, padx=5, pady=5, sticky="w")

        def delete_view():
            view_name = view_name_var.get()
            if not view_name:
                messagebox.showerror("Error", "Debe seleccionar una vista para eliminar.")
                return

            try:
                cursor = self.conn.cursor()
                cursor.execute(f"DROP VIEW {view_name}")
                self.conn.commit()
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Vista '{view_name}' eliminada exitosamente.")
                cursor.close()

                self.load_views(view_combobox)

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al borrar la vista: {str(e)}")

        tk.Button(parent, text="Borrar Vista", command=delete_view, bg="#3e3e3e", fg="black").grid(row=2, column=1, padx=5, pady=10, sticky="w")

    def load_views(self, combobox):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT TABLENAME FROM SYS.SYSTABLES WHERE TABLETYPE = 'V'")
            views = [row[0] for row in cursor.fetchall()]
            cursor.close()
            combobox["values"] = views

        except Exception as e:
            if hasattr(self, 'resultado_text'):
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al cargar las vistas: {str(e)}")
            else:
                messagebox.showerror("Error", f"Error al cargar las vistas: {str(e)}")


    def delete_schema_form(self, parent):
        tk.Label(parent, text="Borrar Esquema", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Seleccionar Esquema:", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        schema_name_var = tk.StringVar()
        schema_combobox = ttk.Combobox(parent, textvariable=schema_name_var, state="readonly", width=30)
        schema_combobox.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(parent, text="Cargar Esquemas", bg="#3e3e3e", fg="black", command=lambda: self.populate_schemas_combobox(schema_combobox)).grid(row=2, column=0, columnspan=2, pady=10)

        # Función para borrar el esquema seleccionado
        def delete_schema():
            schema_name = schema_name_var.get()

            if not schema_name:
                messagebox.showerror("Error", "Debe seleccionar un esquema para borrar.")
                return

            # Crear la consulta SQL para borrar el esquema
            query = f"DROP SCHEMA {schema_name} RESTRICT"

            if not self.conn:
                messagebox.showerror("Error", "Debe seleccionar una conexión para ejecutar el DDL.")
                return

            # Ejecutar la consulta
            try:
                cursor = self.conn.cursor()
                self.query_text.delete(1.0, tk.END)
                self.query_text.insert(tk.END, query)
                cursor.execute(query)
                self.conn.commit()

                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Esquema '{schema_name}' borrado exitosamente.")
                cursor.close()
            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al borrar el esquema: {str(e)}")

        # Botón para borrar el esquema
        tk.Button(parent, text="Borrar Esquema", bg="#3e3e3e", fg="black", command=delete_schema).grid(row=3, column=0, columnspan=2, pady=10)


#=======================================================================================================================
#DATABASE-OPERATIONS
    def get_schemas(self, connection_info):
        try:
            jdbc_driver = DERBY_CLIENT_JAR
            driver_class = 'org.apache.derby.client.ClientAutoloadedDriver'

            db_url = f'jdbc:derby://{connection_info["hostname"]}:{connection_info["port"]}/{connection_info["sid"]};create=true'

            username = connection_info.get("username")
            password = connection_info.get("password")

            conn = jaydebeapi.connect(driver_class, db_url, [username, password], jdbc_driver)

            # Obtener los esquemas
            cursor = conn.cursor()
            cursor.execute("SELECT SCHEMANAME FROM SYS.SYSSCHEMAS")
            schemas = [row[0] for row in cursor.fetchall()]

            cursor.close()
            conn.close()

            return schemas
        except Exception as e:
            messagebox.showerror("Error", "La conexion no tiene una contraseña")
            self.set_password_connection(self.selected_connection)

            return []


    def select_connection(self, event):
        try:
            widget = event.widget
            selection = widget.curselection()
            if selection:
                self.selected_connection = widget.get(selection[0])
                connection_info = self.connections.get(self.selected_connection, {})
                schemas = self.get_schemas(connection_info)
                if hasattr(self, 'schema_combobox'):
                    self.schema_combobox['values'] = schemas
                    if schemas:
                        self.schema_combobox.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

    def populate_schemas(self):
        if not self.selected_connection:
            return
        connection_info = self.connections[self.selected_connection]
        try:
            jdbc_driver = DERBY_CLIENT_JAR
            driver_class = 'org.apache.derby.client.ClientAutoloadedDriver'
            db_url = f'jdbc:derby://{connection_info["hostname"]}:{connection_info["port"]}/{connection_info["sid"]};create=true;currentSchema={connection_info.get("schema")}'
            conn = jaydebeapi.connect(driver_class, db_url, [connection_info["username"], connection_info["password"]], jdbc_driver)
            cursor = conn.cursor()
            cursor.execute("SELECT SCHEMANAME FROM SYS.SYSSCHEMAS")
            schemas = [row[0] for row in cursor.fetchall()]
            self.schema_combobox['values'] = schemas
            if connection_info.get('schema') in schemas:
                self.schema_combobox.set(connection_info.get('schema'))
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener esquemas: {str(e)}")

    def populate_schemas_combobox(self, combobox):
        if not self.selected_connection:
            return
        connection_info = self.connections[self.selected_connection]
        try:
            jdbc_driver = DERBY_CLIENT_JAR
            driver_class = 'org.apache.derby.client.ClientAutoloadedDriver'
            db_url = f'jdbc:derby://{connection_info["hostname"]}:{connection_info["port"]}/{connection_info["sid"]};create=true;currentSchema={connection_info.get("schema")}'
            conn = jaydebeapi.connect(driver_class, db_url, [connection_info["username"], connection_info["password"]], jdbc_driver)
            cursor = conn.cursor()
            cursor.execute("SELECT SCHEMANAME FROM SYS.SYSSCHEMAS")
            schemas = [row[0] for row in cursor.fetchall()]
            combobox['values'] = schemas
            if connection_info.get('schema') in schemas:
                combobox.set(connection_info.get('schema'))
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener esquemas: {str(e)}")

    def insert_connections_to_file(self):
        try:
            with open('connections.pkl', 'wb') as file:
                connections = {name: {k: v for k, v in data.items() if k != 'password'} for name, data in self.connections.items()}
                pickle.dump(connections, file)
            messagebox.showinfo("Guardar Conexiones", "Conexiones guardadas correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al guardar las conexiones: {str(e)}")


    def load_connections_from_file(self):
        try:
            with open('connections.pkl', 'rb') as file:
                self.connections = pickle.load(file)

            print("Conexiones cargadas:", self.connections)

            self.update_connections()
            messagebox.showinfo("Cargar Conexiones", "Conexiones cargadas correctamente.")
        except FileNotFoundError:
            messagebox.showwarning("Advertencia", "No se encontró el archivo de conexiones.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar las conexiones: {str(e)}")


    def show_new_connection_form(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("Nueva Conexión")
        new_window.geometry("400x350")
        new_window.configure(bg="#1e1e1e")

        name_var = tk.StringVar()
        username_var = tk.StringVar()
        password_var = tk.StringVar()
        hostname_var = tk.StringVar()
        port_var = tk.StringVar()
        sid_var = tk.StringVar()

        tk.Label(new_window, text="Nombre", bg="#1e1e1e", fg="white").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(new_window, textvariable=name_var, bg="#2e2e2e", fg="white").grid(row=0, column=1, padx=5, pady=5)

        tk.Label(new_window, text="Usuario", bg="#1e1e1e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(new_window, textvariable=username_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Label(new_window, text="Contraseña", bg="#1e1e1e", fg="white").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(new_window, textvariable=password_var, show="*", bg="#2e2e2e", fg="white").grid(row=2, column=1, padx=5, pady=5)

        tk.Label(new_window, text="Hostname", bg="#1e1e1e", fg="white").grid(row=3, column=0, padx=5, pady=5)
        tk.Entry(new_window, textvariable=hostname_var, bg="#2e2e2e", fg="white").grid(row=3, column=1, padx=5, pady=5)

        tk.Label(new_window, text="Puerto", bg="#1e1e1e", fg="white").grid(row=4, column=0, padx=5, pady=5)
        tk.Entry(new_window, textvariable=port_var, bg="#2e2e2e", fg="white").grid(row=4, column=1, padx=5, pady=5)

        tk.Label(new_window, text="SID", bg="#1e1e1e", fg="white").grid(row=5, column=0, padx=5, pady=5)
        tk.Entry(new_window, textvariable=sid_var, bg="#2e2e2e", fg="white").grid(row=5, column=1, padx=5, pady=5)

        def save_connection():
            connection_info = {
                "name": name_var.get(),
                "username": username_var.get(),
                "password": password_var.get(),
                "hostname": hostname_var.get(),
                "port": port_var.get(),
                "sid": sid_var.get(),
                "schema": None
            }
            self.connections[name_var.get()] = connection_info
            self.update_connections()
            new_window.destroy()

        tk.Button(new_window, text="Probar Conexión", bg="#3e3e3e", fg="black",
                command=lambda: self.test_connection(hostname_var.get(), port_var.get(), sid_var.get(), username_var.get(), password_var.get())
                ).grid(row=6, column=0, columnspan=2, pady=5)

        tk.Button(new_window, text="Guardar Conexión", bg="#3e3e3e", fg="black", command=save_connection).grid(row=7, column=0, columnspan=2, pady=5)
        tk.Button(new_window, text="Cancelar", bg="#3e3e3e", fg="black", command=new_window.destroy).grid(row=8, column=0, columnspan=2, pady=5)

    def test_connection(self, hostname, port, sid, username, password):
        try:
            jdbc_driver = DERBY_CLIENT_JAR
            driver_class = 'org.apache.derby.client.ClientAutoloadedDriver'
            db_url = f'jdbc:derby://{hostname}:{port}/{sid};create=true'
            conn = jaydebeapi.connect(driver_class, db_url, [username, password], jdbc_driver)
            conn.close()
            messagebox.showinfo("Test de Conexión", "Prueba de conexión realizada exitosamente")
        except Exception as e:
            messagebox.showerror("Error de conexión", str(e))

    def save_connection(self, name, hostname, port, sid, username, password, schema):
        connection_info = {
            "name": name,
            "username": username,
            "password": password,
            "hostname": hostname,
            "port": port,
            "sid": sid,
            "schema": schema
        }
        self.connections[name] = connection_info
        self.update_connections()
        messagebox.showinfo("Conexión guardada", f"Conexión {name} guardada correctamente.")

    def update_connections(self):
        self.connection_listbox.delete(0, tk.END)
        for connection_name in self.connections:
            self.connection_listbox.insert(tk.END, connection_name)
        if self.connections:
            self.modificarConexionBtn.config(state="normal")
            self.eliminarConexionBtn.config(state="normal")
            self.conectarBtn.config(state="normal")
            self.desconectarBtn.config(state="normal")
        else:
            self.modificarConexionBtn.config(state="disabled")
            self.eliminarConexionBtn.config(state="disabled")
            self.conectarBtn.config(state="disabled")
            self.desconectarBtn.config(state="disabled")

    def set_password_connection(self, connection_name):
        password = simpledialog.askstring("Contraseña", f"Ingrese la contraseña para la conexión {connection_name}", show="*")
        if password:
            self.connections[connection_name]["password"] = password
            self.update_connections()

    def connect_to_selected_connection(self):
        if self.selected_connection:
            connection_info = self.connections.get(self.selected_connection, {})

            if not connection_info.get('password'):
                messagebox.showwarning("Advertencia", "Debe ingresar la contraseña para la conexión seleccionada.")
                self.set_password_connection(self.selected_connection)
                return


            try:
                # Intentamos realizar la conexión
                jdbc_driver = DERBY_CLIENT_JAR
                driver_class = 'org.apache.derby.client.ClientAutoloadedDriver'
                db_url = f'jdbc:derby://{connection_info.get("hostname")}:{connection_info.get("port")}/{connection_info.get("sid")};create=true'
                self.conn = jaydebeapi.connect(driver_class, db_url, [connection_info["username"], connection_info["password"]], jdbc_driver)

                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Conexión con {self.selected_connection} realizada exitosamente.")

                # Aquí llamamos a la función para mostrar el ComboBox de esquemas y llenarlo
                self.show_schema_selection()

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                messagebox.showerror("Error de conexión", f"Error al conectar con {self.selected_connection}, Verifique la informacion registrada: {str(e)}")
                self.show_modify_connection_form()


    def connect_to_database(self, connection_info):
        try:
            jdbc_driver = DERBY_CLIENT_JAR
            driver_class = 'org.apache.derby.client.ClientAutoloadedDriver'
            db_url = f'jdbc:derby://{connection_info.get("hostname")}:{connection_info.get("port")}/{connection_info.get("sid")};create=true'


            username = connection_info.get("username")
            password = connection_info.get("password")

            if not username:
                messagebox.showerror("Error de conexión", "Debe ingresar un nombre de usuario válido.")
                return
            if not password:
                messagebox.showerror("Error de conexión", "Debe ingresar una contraseña válida.")
                return

            print(f"Intentando conectar con el usuario: {username}")

            self.conn = jaydebeapi.connect(driver_class, db_url, [username, password], jdbc_driver)

            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Conexión con {self.selected_connection} realizada exitosamente.")
            self.update_schema()

        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al conectar con {self.selected_connection}: {str(e)}")

    def show_schema_selection(self):
        schema_window = tk.Toplevel(self.root)
        schema_window.title("Conexion realizada de manera exitosa")
        schema_window.geometry("400x200")
        schema_window.configure(bg="#1e1e1e")

        tk.Label(schema_window, text="Con que esquema desea entrar a la DB?", bg="#1e1e1e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        schema_var = tk.StringVar()
        schema_combobox = ttk.Combobox(schema_window, textvariable=schema_var, state="readonly")
        schema_combobox.grid(row=1, column=0, padx=5, pady=5)

        schemas = self.get_schemas(self.connections[self.selected_connection])
        schema_combobox['values'] = schemas

        def select_schema():
            selected_schema = schema_var.get()
            if not selected_schema:
                messagebox.showerror("Error", "Debe seleccionar un esquema.")
                return

            self.connections[self.selected_connection]["schema"] = selected_schema
            self.update_schema()  # Llamar a la función cuando se cargue el formulario
            schema_window.destroy()

        tk.Button(schema_window, text="Seleccionar", bg="#3e3e3e", fg="black", command=select_schema).grid(row=2, column=0, columnspan=2, pady=10)

    def show_modify_connection_form(self):
        if not self.selected_connection:
            messagebox.showwarning("Advertencia", "No hay ninguna conexión seleccionada.")
            return

        connection_info = self.connections[self.selected_connection]

        username = connection_info.get('username')
        password = connection_info.get('password')


        modify_window = tk.Toplevel(self.root)
        modify_window.title("Modificar Conexión")
        modify_window.geometry("400x350")
        modify_window.configure(bg="#2e2e2e")

        # Mostrar campos para modificar la conexión
        tk.Label(modify_window, text="Nombre", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)
        name_var = tk.StringVar(value=self.selected_connection)
        tk.Entry(modify_window, textvariable=name_var, bg="#1e1e1e", fg="white").grid(row=0, column=1, padx=5, pady=5)

        tk.Label(modify_window, text="Hostname", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        hostname_var = tk.StringVar(value=connection_info['hostname'])
        tk.Entry(modify_window, textvariable=hostname_var, bg="#1e1e1e", fg="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Label(modify_window, text="Port", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=5, pady=5)
        port_var = tk.StringVar(value=connection_info['port'])
        tk.Entry(modify_window, textvariable=port_var, bg="#1e1e1e", fg="white").grid(row=2, column=1, padx=5, pady=5)

        tk.Label(modify_window, text="SID", bg="#2e2e2e", fg="white").grid(row=3, column=0, padx=5, pady=5)
        sid_var = tk.StringVar(value=connection_info['sid'])
        tk.Entry(modify_window, textvariable=sid_var, bg="#1e1e1e", fg="white").grid(row=3, column=1, padx=5, pady=5)

        # Validar si los valores de username y password están correctamente cargados
        tk.Label(modify_window, text="Username", bg="#2e2e2e", fg="white").grid(row=4, column=0, padx=5, pady=5)
        username_var = tk.StringVar(value=username)
        tk.Entry(modify_window, textvariable=username_var, bg="#1e1e1e", fg="white").grid(row=4, column=1, padx=5, pady=5)

        tk.Label(modify_window, text="Password", bg="#2e2e2e", fg="white").grid(row=5, column=0, padx=5, pady=5)
        password_var = tk.StringVar(value=password)
        tk.Entry(modify_window, textvariable=password_var, show="*", bg="#1e1e1e", fg="white").grid(row=5, column=1, padx=5, pady=5)

        def save_changes():
            new_name = name_var.get()
            self.connections.pop(self.selected_connection)
            self.connections[new_name] = {
                'hostname': hostname_var.get(),
                'port': port_var.get(),
                'sid': sid_var.get(),
                'username': username_var.get(),
                'password': password_var.get(),
            }
            self.update_connections()
            modify_window.destroy()

        tk.Button(modify_window, text="Guardar", bg="#3e3e3e", fg="black", command=save_changes).grid(row=7, column=0, columnspan=2, pady=10)
        tk.Button(modify_window, text="Cancelar", bg="#3e3e3e", fg="black", command=modify_window.destroy).grid(row=8, column=0, columnspan=2, pady=5)

    def disconnect_from_connection(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, "Conexión cerrada exitosamente.")
            self.update_schema()
        else:
            messagebox.showwarning("Advertencia", "No hay ninguna conexión activa.")

    def delete_connection(self):
        if not self.selected_connection:
            messagebox.showwarning("Advertencia", "No hay ninguna conexión seleccionada.")
            return
        del self.connections[self.selected_connection]
        self.update_connections()
        messagebox.showinfo("Conexión eliminada", f"Conexión {self.selected_connection} ha sido eliminada.")
        self.selected_connection = None

#=======================================================================================================================




#=======================================================================================================================
    def create_stored_procedure_form(self, parent):
        tk.Label(parent, text="Crear Procedimiento Almacenado", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        # Nombre del procedimiento
        tk.Label(parent, text="Nombre del Procedimiento", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        self.procedure_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=self.procedure_name_var, bg="#2e2e2e", fg="white", width=30).grid(row=1, column=1, padx=5, pady=5)

        column_frame = tk.Frame(parent, bg="#2e2e2e")
        column_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Tabla de parámetros
        self.columns_tree = ttk.Treeview(column_frame, columns=("name", "mode", "data_type", "size"), show="headings", height=6)
        self.columns_tree.grid(row=1, column=0, columnspan=4, pady=5)
        self.columns_tree.heading("name", text="Nombre")
        self.columns_tree.heading("mode", text="Modo")
        self.columns_tree.heading("data_type", text="Tipo de Dato")
        self.columns_tree.heading("size", text="Tamaño")

        self.columns_tree.column("name", width=150)
        self.columns_tree.column("mode", width=90)
        self.columns_tree.column("data_type", width=120)
        self.columns_tree.column("size", width=60)

        # Campos para atributos
        name_var = tk.StringVar()
        tk.Entry(column_frame, textvariable=name_var, width=15, bg="white", fg="black").grid(row=2, column=0, padx=5, pady=5)

        mode_var = tk.StringVar()
        mode_combobox = ttk.Combobox(column_frame, textvariable=mode_var, values=["IN", "OUT", "INOUT"], state="readonly", width=8)
        mode_combobox.grid(row=2, column=1, padx=5, pady=5)

        data_type_var = tk.StringVar()
        data_type_combobox = ttk.Combobox(column_frame, textvariable=data_type_var, values=["VARCHAR", "INT", "FLOAT"], state="readonly", width=10)
        data_type_combobox.grid(row=2, column=2, padx=5, pady=5)

        size_var = tk.StringVar()
        tk.Entry(column_frame, textvariable=size_var, width=5, bg="white", fg="black").grid(row=2, column=3, padx=5, pady=5)

        def add_column():
            if not name_var.get() or not mode_var.get() or not data_type_var.get():
                messagebox.showerror("Error", "Debe ingresar todos los valores del atributo.")
                return
            size = size_var.get() if data_type_var.get() == "VARCHAR" else ""
            self.columns_tree.insert("", "end", values=(name_var.get(), mode_var.get(), data_type_var.get(), size))

        def delete_column():
            selected_item = self.columns_tree.selection()
            if selected_item:
                self.columns_tree.delete(selected_item)

        tk.Button(column_frame, text="Agregar Atributo", command=add_column, bg="#3e3e3e", fg="black").grid(row=3, column=0, padx=5)
        tk.Button(column_frame, text="Eliminar Atributo", command=delete_column, bg="#3e3e3e", fg="black").grid(row=3, column=1, padx=5)

        # Área para el cuerpo del procedimiento
        tk.Label(parent, text="Cuerpo del Procedimiento", bg="#2e2e2e", fg="white").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        procedure_body_text = tk.Text(parent, height=10, width=60, bg="#1e1e1e", fg="white", insertbackground="white")
        procedure_body_text.grid(row=5, column=0, columnspan=4, padx=5, pady=5, sticky="we")

        def create_stored_procedure():
            procedure_name = self.procedure_name_var.get()
            if not procedure_name:
                messagebox.showerror("Error", "Debe ingresar el nombre del procedimiento.")
                return

            parameters = [self.columns_tree.item(item, "values") for item in self.columns_tree.get_children()]
            param_definitions = []

            for param in parameters:
                param_mode = param[1]
                param_name = param[0]
                param_type = param[2]
                param_size = f"({param[3]})" if param_type == "VARCHAR" and param[3] else ""
                param_def = f"{param_mode} {param_name} {param_type}{param_size}"
                param_definitions.append(param_def)

            procedure_body = procedure_body_text.get("1.0", tk.END).strip()

            ddl = f"""
            CREATE PROCEDURE {procedure_name} (
                {', '.join(param_definitions)}
            )
            PARAMETER STYLE JAVA
            LANGUAGE JAVA
            EXTERNAL NAME '{procedure_body}'
            """

            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, ddl)

            try:
                cursor = self.conn.cursor()
                cursor.execute(ddl)
                self.conn.commit()

                insert_query = "INSERT INTO SYSPROCEDURES (PROCEDURE_NAME, DEFINITION) VALUES (?, ?)"
                cursor.execute(insert_query, (procedure_name, ddl))
                self.conn.commit()

                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Procedimiento '{procedure_name}' creado exitosamente y almacenado en SYSPROCEDURES.")
                cursor.close()

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al crear el procedimiento: {str(e)}")

        tk.Button(parent, text="Crear Procedimiento", command=create_stored_procedure, bg="#3e3e3e", fg="black").grid(row=6, column=0, padx=5, pady=10)
        tk.Button(parent, text="Cancelar", command=parent.quit, bg="#3e3e3e", fg="black").grid(row=6, column=1, padx=5, pady=10)


    def delete_stored_procedure_form(self, parent):
            tk.Label(parent, text="Borrar Procedimiento Almacenado", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

            tk.Label(parent, text="Nombre del Procedimiento", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)

            procedure_name_var = tk.StringVar()
            procedure_combobox = ttk.Combobox(parent, textvariable=procedure_name_var, state="readonly", width=30)
            procedure_combobox.grid(row=1, column=1, padx=5, pady=5)

            def load_procedures():
                try:
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT ALIAS FROM SYS.SYSALIASES WHERE ALIASTYPE='P'")  # Query para obtener nombres de procedimientos
                    procedures = [row[0] for row in cursor.fetchall()]
                    procedure_combobox['values'] = procedures
                    cursor.close()
                except Exception as e:
                    messagebox.showerror("Error", f"Error al cargar procedimientos: {str(e)}")

            def delete_stored_procedure():
                procedure_name = procedure_name_var.get()
                if not procedure_name:
                    messagebox.showerror("Error", "Debe seleccionar un procedimiento.")
                    return

                try:
                    cursor = self.conn.cursor()
                    ddl = f"DROP PROCEDURE {procedure_name}"
                    self.query_text.delete(1.0, tk.END)
                    self.query_text.insert(tk.END, ddl)

                    cursor.execute(ddl)
                    self.conn.commit()

                    self.resultado_text.delete(1.0, tk.END)
                    self.resultado_text.insert(tk.END, f"Procedimiento '{procedure_name}' borrado exitosamente.")
                    cursor.close()


                except Exception as e:
                    self.resultado_text.delete(1.0, tk.END)
                    self.resultado_text.insert(tk.END, f"Error al borrar el procedimiento: {str(e)}")

            tk.Button(parent, text="Cargar Procedimientos", bg="#3e3e3e", fg="black", command=load_procedures).grid(row=2, column=0, padx=5, pady=5)
            tk.Button(parent, text="Borrar Procedimiento", bg="#3e3e3e", fg="black", command=delete_stored_procedure).grid(row=2, column=1, padx=5, pady=10)

    def create_stored_function_form(self, parent):
        tk.Label(parent, text="Crear Función", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=3, pady=3, sticky="w")

        # Nombre de la función
        tk.Label(parent, text="Nombre de la Función", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=3, pady=3, sticky="w")
        function_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=function_name_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=3, pady=3, sticky="w")

        # Tipo de retorno
        tk.Label(parent, text="Tipo de Retorno", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=3, pady=3, sticky="w")
        return_type_var = tk.StringVar()
        return_type_combobox = ttk.Combobox(parent, textvariable=return_type_var, values=["VARCHAR", "INT", "FLOAT"], state="readonly")
        return_type_combobox.grid(row=2, column=1, padx=3, pady=3, sticky="w")

        # Longitud del retorno
        tk.Label(parent, text="Longitud del Retorno", bg="#2e2e2e", fg="white").grid(row=2, column=2, padx=3, pady=3, sticky="w")
        return_length_var = tk.StringVar()
        tk.Entry(parent, textvariable=return_length_var, width=5, bg="#2e2e2e", fg="white").grid(row=2, column=3, padx=3, pady=3, sticky="w")

        # Tabla de parámetros
        column_frame = tk.Frame(parent, bg="#2e2e2e")
        column_frame.grid(row=3, column=0, columnspan=4, padx=3, pady=3, sticky="w")

        columns_tree = ttk.Treeview(column_frame, columns=("name", "mode", "data_type", "length", "default_value"), show="headings", height=4)
        columns_tree.grid(row=1, column=0, columnspan=5, pady=3)
        columns_tree.heading("name", text="Nombre")
        columns_tree.heading("mode", text="Modo")
        columns_tree.heading("data_type", text="Tipo de Dato")
        columns_tree.heading("length", text="Longitud")
        columns_tree.heading("default_value", text="Valor por Defecto")

        columns_tree.column("name", width=100)
        columns_tree.column("mode", width=60)
        columns_tree.column("data_type", width=100)
        columns_tree.column("length", width=60)
        columns_tree.column("default_value", width=100)

        def add_parameter():
            if not param_name_var.get() or not param_mode_var.get() or not param_data_type_var.get():
                messagebox.showerror("Error", "Debe ingresar todos los campos del parámetro.")
                return
            columns_tree.insert("", "end", values=(param_name_var.get(), param_mode_var.get(), param_data_type_var.get(), param_length_var.get(), param_default_var.get()))

        def delete_parameter():
            selected_item = columns_tree.selection()
            if selected_item:
                columns_tree.delete(selected_item)

        param_name_var = tk.StringVar()
        tk.Entry(column_frame, textvariable=param_name_var, width=15, bg="white", fg="black").grid(row=2, column=0, padx=3, pady=3)

        param_mode_var = tk.StringVar()
        mode_combobox = ttk.Combobox(column_frame, textvariable=param_mode_var, values=["IN", "OUT", "INOUT"], state="readonly")
        mode_combobox.grid(row=2, column=1, padx=3, pady=3)

        param_data_type_var = tk.StringVar()
        data_type_combobox = ttk.Combobox(column_frame, textvariable=param_data_type_var, values=["VARCHAR", "INT", "FLOAT"], state="readonly")
        data_type_combobox.grid(row=2, column=2, padx=3, pady=3)

        param_length_var = tk.StringVar()
        tk.Entry(column_frame, textvariable=param_length_var, width=5, bg="white", fg="black").grid(row=2, column=3, padx=3, pady=3)

        param_default_var = tk.StringVar()
        tk.Entry(column_frame, textvariable=param_default_var, width=10, bg="white", fg="black").grid(row=2, column=4, padx=3, pady=3)

        tk.Button(column_frame, text="Agregar Parámetro", command=add_parameter, bg="#3e3e3e", fg="black").grid(row=3, column=4, padx=3, pady=3)
        tk.Button(column_frame, text="Eliminar Parámetro", command=delete_parameter, bg="#3e3e3e", fg="black").grid(row=4, column=4, padx=3, pady=3)

        # Área para el cuerpo de la función
        tk.Label(parent, text="Cuerpo de la Función", bg="#2e2e2e", fg="white").grid(row=5, column=0, padx=3, pady=3, sticky="w")
        function_body_text = tk.Text(parent, height=10, width=60, bg="#1e1e1e", fg="white", insertbackground="white")
        function_body_text.grid(row=6, column=0, columnspan=4, padx=3, pady=3, sticky="we")

        def create_function():
            if not self.conn:
                messagebox.showerror("Error", "Debe seleccionar una conexión.")
                return

            try:
                cursor = self.conn.cursor()
                function_name = function_name_var.get()
                return_type = f"{return_type_var.get()}({return_length_var.get()})" if return_type_var.get() == "VARCHAR" else return_type_var.get()
                parameters = ", ".join([f"{p[0]} {p[2]}({p[3]})" if p[2] == "VARCHAR" else f"{p[0]} {p[2]}" for p in [columns_tree.item(i, 'values') for i in columns_tree.get_children()]])
                function_body = function_body_text.get("1.0", tk.END).strip()
                ddl = f"CREATE FUNCTION {function_name} ({parameters}) RETURNS {return_type} LANGUAGE JAVA PARAMETER STYLE JAVA NO SQL EXTERNAL NAME '{function_body}'"
                cursor.execute(ddl)
                self.conn.commit()

                self.query_text.delete(1.0, tk.END)
                self.query_text.insert(tk.END, ddl)

                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Función '{function_name}' creada exitosamente.")
                cursor.close()
            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al crear la función: {str(e)}")

        tk.Button(parent, text="Crear Función", command=create_function, bg="#3e3e3e", fg="black").grid(row=7, column=0, padx=3, pady=3, sticky="e")
        tk.Button(parent, text="Cancelar", command=parent.quit, bg="#3e3e3e", fg="black").grid(row=7, column=1, padx=3, pady=3, sticky="w")

    def show_modify_stored_function_form(self, parent):
        tk.Label(parent, text="Seleccione la Función:", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        function_name_var = tk.StringVar()
        function_combobox = ttk.Combobox(parent, textvariable=function_name_var, state="readonly")
        function_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Button(parent, text="Cargar Funciones", command=lambda: self.load_functions(function_combobox), bg="#3e3e3e", fg="black").grid(row=0, column=2, padx=5, pady=5)

        tk.Label(parent, text="DDL de la Función:", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ddl_textbox = tk.Text(parent, height=10, bg="#2e2e2e", fg="white", insertbackground="white")
        ddl_textbox.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="we")

        def generate_ddl():
            function_name = function_name_var.get()
            if not function_name:
                messagebox.showerror("Error", "Debe seleccionar una función para generar el DDL.")
                return

            try:
                cursor = self.conn.cursor()
                cursor.execute(f"SELECT FUNCTION_DEFINITION FROM SYS.SYSFUNCS WHERE ALIAS = '{function_name}'")
                ddl = cursor.fetchone()[0]

                ddl_textbox.delete(1.0, tk.END)
                ddl_textbox.insert(tk.END, ddl)

                cursor.close()

            except Exception as e:
                ddl_textbox.delete(1.0, tk.END)
                ddl_textbox.insert(tk.END, f"Error al obtener el DDL de la función: {str(e)}")

        tk.Button(parent, text="Generar DDL", command=generate_ddl, bg="#3e3e3e", fg="black").grid(row=3, column=0, columnspan=3, padx=5, pady=10, sticky="e")

        def execute_ddl():
            new_ddl = ddl_textbox.get("1.0", tk.END).strip()
            if not new_ddl:
                messagebox.showerror("Error", "Debe generar o modificar el DDL antes de ejecutarlo.")
                return

            self.modify_stored_function(function_name_var.get(), new_ddl)

        tk.Button(parent, text="Ejecutar DDL", command=execute_ddl, bg="#3e3e3e", fg="black").grid(row=4, column=0, columnspan=3, padx=5, pady=10, sticky="e")


    def delete_stored_function_form(self, parent):
        tk.Label(parent, text="Borrar Función", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        # ComboBox para seleccionar la función
        tk.Label(parent, text="Seleccione la Función", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        function_name_var = tk.StringVar()
        function_combobox = ttk.Combobox(parent, textvariable=function_name_var, state="readonly", width=30)
        function_combobox.grid(row=1, column=1, padx=5, pady=5)

        # Botón para cargar todas las funciones en el ComboBox
        def load_functions():
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT ALIAS FROM SYS.SYSALIASES WHERE ALIASTYPE='F'")
                functions = [row[0] for row in cursor.fetchall()]
                function_combobox['values'] = functions
                cursor.close()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar las funciones: {e}")

        tk.Button(parent, text="Cargar Funciones", bg="#3e3e3e", fg="black", command=load_functions).grid(row=2, column=0, columnspan=2, pady=10)

        # Botón para eliminar la función seleccionada
        def delete_function():
            selected_function = function_name_var.get()
            if not selected_function:
                messagebox.showerror("Error", "Debe seleccionar una función para eliminar.")
                return

            try:
                cursor = self.conn.cursor()
                cursor.execute(f"DROP FUNCTION {selected_function}")
                self.conn.commit()
                messagebox.showinfo("Éxito", f"Función '{selected_function}' eliminada exitosamente.")
                cursor.close()
                load_functions()  # Recargar las funciones después de borrar
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la función: {e}")

        tk.Button(parent, text="Borrar Función", bg="#3e3e3e", fg="black", command=delete_function).grid(row=3, column=0, columnspan=2, pady=10)

    def modify_stored_procedure_form(self, parent):
        tk.Label(parent, text="Modificar Procedimiento Almacenado", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Nombre del Procedimiento", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)

        procedure_name_var = tk.StringVar()
        procedure_combobox = ttk.Combobox(parent, textvariable=procedure_name_var, state="readonly")
        procedure_combobox.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(parent, text="Cargar Procedimientos", command=lambda: self.load_procedures(procedure_combobox), bg="#3e3e3e", fg="black").grid(row=1, column=2, padx=5, pady=5)

        tk.Button(parent, text="Cargar DDL", command=lambda: self.get_procedure_ddl(procedure_name_var.get()), bg="#3e3e3e", fg="black").grid(row=2, column=0, columnspan=2, pady=10)

        procedure_code_text = tk.Text(parent, height=10, bg="#2e2e2e", fg="white")
        procedure_code_text.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        tk.Button(parent, text="Modificar Procedimiento", bg="#3e3e3e", fg="black", command=lambda: self.modify_stored_procedure(procedure_name_var.get(), procedure_code_text.get("1.0", tk.END))).grid(row=4, column=0, columnspan=2, pady=10)

    def load_procedures(self, combobox):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT ALIAS FROM SYS.SYSALIASES WHERE ALIASTYPE = 'P'")
            procedures = cursor.fetchall()
            procedure_names = [proc[0] for proc in procedures]
            combobox['values'] = procedure_names
            cursor.close()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar los procedimientos: {str(e)}")

    def get_procedure_ddl(self, procedure_name):
        if not procedure_name:
            messagebox.showerror("Error", "Debe seleccionar un procedimiento.")
            return

        try:
            cursor = self.conn.cursor()

            # Buscar el DDL en la tabla SYSPROCEDURES
            cursor.execute(f"SELECT DEFINITION FROM SYSPROCEDURES WHERE PROCEDURE_NAME = '{procedure_name}'")
            result = cursor.fetchone()

            if result:
                ddl_clob = result[0]
                if isinstance(ddl_clob, str):
                    ddl = ddl_clob  # Si es una cadena, la utilizamos directamente
                else:
                    ddl = ddl_clob.read()  # Si es un CLOB, usamos read() para obtener el contenido

                # Mostrar el DDL recuperado
                self.query_text.delete(1.0, tk.END)
                self.query_text.insert(tk.END, ddl)
            else:
                # Si no se encuentra el DDL, mostrar un mensaje de error
                self.query_text.delete(1.0, tk.END)
                self.query_text.insert(tk.END, "No se encontró el DDL en SYSPROCEDURES.")

            cursor.close()

        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al obtener el DDL: {str(e)}")

    def modify_stored_procedure(self, name, new_code):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        try:
            cursor = self.conn.cursor()

            # Primero, eliminamos el procedimiento almacenado original
            drop_query = f"DROP PROCEDURE {name}"

            # Creamos el nuevo procedimiento
            create_query = f"""
            CREATE PROCEDURE {name} AS
            {new_code.strip().replace("'", "''")}
            """

            # Eliminar el DDL antiguo de SYSPROCEDURES
            delete_sysproc_query = f"DELETE FROM SYSPROCEDURES WHERE PROCEDURE_NAME = '{name}'"

            # Insertar el nuevo DDL en SYSPROCEDURES
            insert_sysproc_query = f"""
            INSERT INTO SYSPROCEDURES (PROCEDURE_NAME, DEFINITION)
            VALUES ('{name}', '{new_code.strip().replace("'", "''")}')
            """

            # Ejecutamos las consultas
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, f"{drop_query};\n{create_query};\n{delete_sysproc_query};\n{insert_sysproc_query}")

            # Ejecutar la eliminación y creación del procedimiento original
            cursor.execute(drop_query)
            cursor.execute(create_query)
            self.conn.commit()

            # Actualizar la tabla SYSPROCEDURES
            cursor.execute(delete_sysproc_query)
            cursor.execute(insert_sysproc_query)
            self.conn.commit()

            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Procedimiento {name} modificado exitosamente y actualizado en SYSPROCEDURES.")
            cursor.close()

        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al modificar el procedimiento: {str(e)}")

    def delete_stored_procedure(self, name):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        try:
            cursor = self.conn.cursor()
            query = f"DROP PROCEDURE {name}"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, query)
            cursor.execute(query)
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Procedimiento {name} borrado exitosamente.")
            cursor.close()
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al borrar el procedimiento: {str(e)}")

    def get_function_ddl(self, function_name):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return
        try:
            cursor = self.conn.cursor()
            query = f"SELECT FUNCTIONTEXT FROM SYS.SYSALIASES WHERE ALIAS = '{function_name}'"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, query)
            cursor.execute(query)
            ddl = cursor.fetchone()
            if ddl:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, ddl[0])
            else:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"No se encontró la función {function_name}.")
            cursor.close()
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al obtener DDL de la función: {str(e)}")

    def create_stored_function(self, name, return_type, parameters):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return
        try:
            cursor = self.conn.cursor()

            query = f"CREATE FUNCTION {name}({parameters}) RETURNS {return_type} LANGUAGE JAVA PARAMETER STYLE JAVA NO SQL EXTERNAL NAME 'Class.method';"

            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, query)

            cursor.execute(query)
            self.conn.commit()

            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Función {name} creada exitosamente.")
            cursor.close()

        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al crear la función: {str(e)}")

    def load_functions(self, combobox):
        try:
            if not self.conn:
                messagebox.showerror("Error", "No hay ninguna conexión establecida.")
                return

            cursor = self.conn.cursor()
            cursor.execute("SELECT ALIAS FROM SYS.SYSALIASES WHERE ALIASTYPE = 'F'")
            functions = cursor.fetchall()

            combobox['values'] = [func[0] for func in functions]
            if functions:
                combobox.current(0)

            cursor.close()

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar las funciones: {str(e)}")

    def modify_stored_function(self, name, new_code):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        try:
            cursor = self.conn.cursor()

            drop_query = f"DROP FUNCTION {name}"
            create_query = new_code

            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, f"{drop_query};\n{create_query}")
            cursor.execute(drop_query)
            cursor.execute(create_query)
            self.conn.commit()

            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Función {name} modificada exitosamente.")
            cursor.close()

        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al modificar la función: {str(e)}")

    def delete_function(self, name):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return
        try:
            cursor = self.conn.cursor()
            query = f"DROP FUNCTION {name}"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, query)
            cursor.execute(query)
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Función {name} borrada exitosamente.")
            cursor.close()
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al borrar la función: {str(e)}")

    def list_items(self, option):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        self.query_text.delete(1.0, tk.END)
        textbox = self.resultado_text
        textbox.delete(1.0, tk.END)

        try:
            cursor = self.conn.cursor()
            query = ""

            if option.lower() == "tablas":
                query = "SELECT TABLENAME FROM SYS.SYSTABLES WHERE TABLETYPE='T'"
            elif option.lower() == "vistas":
                query = "SELECT TABLENAME FROM SYS.SYSTABLES WHERE TABLETYPE='V'"
            elif option.lower() == "indices":
                query = """
                   SELECT CONGLOMERATENAME
                    FROM SYS.SYSCONGLOMERATES
                    WHERE ISINDEX = true
                """
            elif option.lower() == "procedimientos almacenados":
                query = "SELECT ALIAS FROM SYS.SYSALIASES WHERE ALIASTYPE='P'"
            elif option.lower() == "funciones almacenadas":
                query = "SELECT ALIAS, ALIASTYPE FROM SYS.SYSALIASES WHERE ALIASTYPE ='F'"
            elif option.lower() == "triggers":
                query = """
                    SELECT TRIGGERNAME, EVENT, TABLENAME
                    FROM SYS.SYSTRIGGERS
                    JOIN SYS.SYSTABLES ON SYS.SYSTRIGGERS.TABLEID = SYS.SYSTABLES.TABLEID
                """
            elif option.lower() == "checks":
                query = """
                    SELECT C.CONSTRAINTNAME, T.TABLENAME
                    FROM SYS.SYSCONSTRAINTS C
                    JOIN SYS.SYSTABLES T ON C.TABLEID = T.TABLEID
                    WHERE C.TYPE = 'C'
                """
            elif option.lower() == "esquemas":
                query = "SELECT SCHEMANAME FROM SYS.SYSSCHEMAS"

            if query:
                self.query_text.insert(tk.END, query)
                cursor.execute(query)
                items = cursor.fetchall()
                if items:
                    for item in items:
                        textbox.insert(tk.END, f"{item[0]}\n")
                else:
                    textbox.insert(tk.END, f"No se encontraron {option.lower()}.")

            cursor.close()

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al listar los {option.lower()}s: {str(e)}")

    def create_index_form(self, parent):
        tk.Label(parent, text="Crear Índice", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Nombre del Índice", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        index_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=index_name_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Label(parent, text="Tabla", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=5, pady=5)
        table_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=table_name_var, bg="#2e2e2e", fg="white").grid(row=2, column=1, padx=5, pady=5)

        tk.Label(parent, text="Columnas (separadas por comas)", bg="#2e2e2e", fg="white").grid(row=3, column=0, padx=5, pady=5)
        columns_var = tk.StringVar()
        tk.Entry(parent, textvariable=columns_var, bg="#2e2e2e", fg="white").grid(row=3, column=1, padx=5, pady=5)

        tk.Label(parent, text="Tipo de Índice", bg="#2e2e2e", fg="white").grid(row=4, column=0, padx=5, pady=5)
        index_type_var = tk.StringVar(value="No único")
        ttk.Combobox(parent, textvariable=index_type_var, values=["No único", "Único"], state="readonly").grid(row=4, column=1, padx=5, pady=5)

        tk.Button(parent, text="Crear Índice", bg="#3e3e3e", fg="black", command=lambda: self.create_index(index_name_var.get(), table_name_var.get(), columns_var.get(), index_type_var.get())).grid(row=5, column=0, columnspan=2, pady=10)



    def load_indexes(self, combobox):
            if not self.conn:
                messagebox.showerror("Error", "No hay ninguna conexión establecida.")
                return

            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT CONGLOMERATENAME FROM SYS.SYSCONGLOMERATES WHERE ISINDEX = true")
                indexes = cursor.fetchall()
                index_names = [index[0] for index in indexes]
                combobox['values'] = index_names
                cursor.close()
            except Exception as e:
                messagebox.showerror("Error", f"Error al obtener los índices: {str(e)}")


    def modify_index_form(self, parent):
        tk.Label(parent, text="Modificar Índice", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Nombre del Índice", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)

        index_name_var = tk.StringVar()
        index_combobox = ttk.Combobox(parent, textvariable=index_name_var, state="readonly")
        index_combobox.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(parent, text="Cargar Índices", bg="#3e3e3e", fg="black", command=lambda: self.load_indexes(index_combobox)).grid(row=1, column=2, padx=5, pady=5)

        tk.Label(parent, text="Nueva Tabla", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=5, pady=5)
        new_table_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=new_table_name_var, bg="#2e2e2e", fg="white").grid(row=2, column=1, padx=5, pady=5)

        tk.Label(parent, text="Nuevas Columnas (separadas por comas)", bg="#2e2e2e", fg="white").grid(row=3, column=0, padx=5, pady=5)
        new_columns_var = tk.StringVar()
        tk.Entry(parent, textvariable=new_columns_var, bg="#2e2e2e", fg="white").grid(row=3, column=1, padx=5, pady=5)

        tk.Button(parent, text="Modificar Índice", bg="#3e3e3e", fg="black", command=lambda: self.modify_index(index_name_var.get(), new_table_name_var.get(), new_columns_var.get())).grid(row=4, column=0, columnspan=2, pady=10)




    def delete_index_form(self, parent):
        tk.Label(parent, text="Borrar Índice", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)


        tk.Label(parent, text="Nombre del Índice", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        index_name_var = tk.StringVar()
        index_combobox = ttk.Combobox(parent, textvariable=index_name_var, state="readonly", width=30)
        index_combobox.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(parent, text="Cargar Indices", bg="#3e3e3e", fg="black", command=lambda: self.populate_indexes(index_combobox)).grid(row=1, column=2, padx=5, pady=5)
        # Botón para borrar el índice
        tk.Button(parent, text="Borrar Índice", bg="#3e3e3e", fg="black", command=lambda: self.delete_index(index_name_var.get())).grid(row=2, column=0, columnspan=2, pady=10)

        # Llamar al método para llenar el ComboBox con los índices disponibles
        self.populate_indexes(index_combobox)

    def populate_indexes(self, combobox):
        if self.conn:
            try:
                cursor = self.conn.cursor()

                cursor.execute("SELECT CONGLOMERATENAME FROM SYS.SYSCONGLOMERATES WHERE ISINDEX = true")
                indexes = cursor.fetchall()

                index_names = [index[0] for index in indexes]
                combobox['values'] = index_names

                cursor.close()

            except Exception as e:
                messagebox.showerror("Error", f"Error al obtener los índices: {str(e)}")

    def delete_index(self, index_name):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        try:
            cursor = self.conn.cursor()
            query = f"DROP INDEX {index_name}"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, query)
            cursor.execute(query)
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Índice {index_name} borrado exitosamente.")
            cursor.close()

        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al borrar el índice: {str(e)}")

    def create_index(self, index_name, table_name, columns, index_type):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        try:
            cursor = self.conn.cursor()
            unique = "UNIQUE" if index_type == "Único" else ""
            query = f"CREATE {unique} INDEX {index_name} ON {table_name} ({columns})"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, query)
            cursor.execute(query)
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Índice {index_name} creado exitosamente en la tabla {table_name}.")
            cursor.close()
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al crear el índice: {str(e)}")

    def modify_index(self, index_name, new_table_name, new_columns):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        try:
            cursor = self.conn.cursor()
            drop_query = f"DROP INDEX {index_name}"
            create_query = f"CREATE INDEX {index_name} ON {new_table_name} ({new_columns})"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, f"{drop_query};\n{create_query}")
            cursor.execute(drop_query)
            cursor.execute(create_query)
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Índice {index_name} modificado exitosamente.")
            cursor.close()
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al modificar el índice: {str(e)}")

    def delete_index(self, index_name):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        try:
            cursor = self.conn.cursor()
            query = f"DROP INDEX {index_name}"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, query)
            cursor.execute(query)
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Índice {index_name} borrado exitosamente.")
            cursor.close()
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al borrar el índice: {str(e)}")
            print(e)

root = tk.Tk()
app = SQLDeveloperEmulator(root)
root.mainloop()
