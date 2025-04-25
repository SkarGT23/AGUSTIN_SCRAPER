import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2  # Cambia a mysql.connector si usas MySQL

# CONFIGURA ESTOS DATOS SEGÚN TU BASE DE DATOS
DB_CONFIG = {
    'host': 'localhost',
    'database': 'nombre_basedatos',
    'user': 'usuario',
    'password': 'contraseña',
    'port': 5432  # Cambia a 3306 si es MySQL
}

class OfertaCRUDApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Ofertas de Empleo - Escritorio")
        self.geometry('800x400')
        self.conn = None
        self.create_widgets()
        self.connect_db()
        self.load_ofertas()

    def connect_db(self):
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
        except Exception as e:
            messagebox.showerror("Error conexión", str(e))
            self.destroy()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Tabla
        self.tree = ttk.Treeview(frame, columns=("ID", "Título", "Empresa", "Portal", "Fecha"), show="headings")
        for col in ("ID", "Título", "Empresa", "Portal", "Fecha"):
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)
        # Botones CRUD
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=8)
        ttk.Button(btn_frame, text="Añadir Oferta", command=self.add_oferta).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Editar Oferta", command=self.edit_oferta).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar Oferta", command=self.delete_oferta).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refrescar", command=self.load_ofertas).pack(side=tk.RIGHT, padx=5)

    def load_ofertas(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT id, titulo, empresa, portal, fecha_publicacion FROM busqueda_ofertalaboral ORDER BY id DESC LIMIT 100")
            for row in cur.fetchall():
                self.tree.insert('', tk.END, values=row)
            cur.close()
        except Exception as e:
            messagebox.showerror("Error cargando ofertas", str(e))

    def add_oferta(self):
        self.oferta_form()

    def edit_oferta(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selecciona", "Selecciona una oferta para editar")
            return
        datos = self.tree.item(sel[0], 'values')
        self.oferta_form(datos)

    def delete_oferta(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selecciona", "Selecciona una oferta para eliminar")
            return
        id_oferta = self.tree.item(sel[0], 'values')[0]
        if messagebox.askyesno("Eliminar", "¿Seguro que quieres eliminar la oferta?"):
            try:
                cur = self.conn.cursor()
                cur.execute("DELETE FROM busqueda_ofertalaboral WHERE id=%s", (id_oferta,))
                self.conn.commit()
                cur.close()
                self.load_ofertas()
            except Exception as e:
                messagebox.showerror("Error eliminando", str(e))

    def oferta_form(self, datos=None):
        win = tk.Toplevel(self)
        win.title("Editar Oferta" if datos else "Añadir Oferta")
        labels = ["Título", "Empresa", "Portal", "Fecha (YYYY-MM-DD)"]
        entries = []
        for i, lab in enumerate(labels):
            ttk.Label(win, text=lab).grid(row=i, column=0, sticky=tk.W, padx=6, pady=4)
            ent = ttk.Entry(win, width=40)
            ent.grid(row=i, column=1, padx=6, pady=4)
            if datos:
                ent.insert(0, datos[i+1])
            entries.append(ent)
        def guardar():
            vals = [e.get().strip() for e in entries]
            if not all(vals):
                messagebox.showwarning("Campos requeridos", "Todos los campos son obligatorios")
                return
            try:
                cur = self.conn.cursor()
                if datos:
                    cur.execute("UPDATE busqueda_ofertalaboral SET titulo=%s, empresa=%s, portal=%s, fecha_publicacion=%s WHERE id=%s", (*vals, datos[0]))
                else:
                    cur.execute("INSERT INTO busqueda_ofertalaboral (titulo, empresa, portal, fecha_publicacion) VALUES (%s, %s, %s, %s)", tuple(vals))
                self.conn.commit()
                cur.close()
                win.destroy()
                self.load_ofertas()
            except Exception as e:
                messagebox.showerror("Error guardando", str(e))
        ttk.Button(win, text="Guardar", command=guardar).grid(row=len(labels), column=0, columnspan=2, pady=10)
        win.grab_set()

if __name__ == '__main__':
    app = OfertaCRUDApp()
    app.mainloop()
