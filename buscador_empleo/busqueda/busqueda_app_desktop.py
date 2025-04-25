import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox
)
from PyQt5.QtCore import Qt
import psycopg2  # Cambia a mysql.connector si usas MySQL

# CONFIGURA ESTOS DATOS SEGÚN TU BASE DE DATOS
DB_CONFIG = {
    'host': 'localhost',
    'database': 'nombre_basedatos',
    'user': 'usuario',
    'password': 'contraseña',
    'port': 5432  # Cambia a 3306 si es MySQL
}

class BusquedaEmpleoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Buscar Ofertas de Empleo")
        self.setGeometry(100, 100, 900, 500)
        self.conn = None
        self.setup_ui()
        self.connect_db()

    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()
        # Columna de campos
        campos_layout = QVBoxLayout()
        # Palabra clave
        self.palabra = QLineEdit()
        campos_layout.addWidget(QLabel("Palabra clave:"))
        campos_layout.addWidget(self.palabra)
        # Ubicación
        self.ubicacion = QLineEdit()
        campos_layout.addWidget(QLabel("Ubicación:"))
        campos_layout.addWidget(self.ubicacion)
        # Puesto de trabajo
        self.puesto = QLineEdit()
        campos_layout.addWidget(QLabel("Puesto de trabajo:"))
        campos_layout.addWidget(self.puesto)
        # Salario mínimo
        self.salario = QLineEdit()
        self.salario.setPlaceholderText("Ej: 30000")
        campos_layout.addWidget(QLabel("Salario mínimo (€/año):"))
        campos_layout.addWidget(self.salario)
        # Tecnología utilizada
        self.tecnologia = QLineEdit()
        campos_layout.addWidget(QLabel("Tecnología utilizada:"))
        campos_layout.addWidget(self.tecnologia)
        # Número de ofertas
        self.num_ofertas = QSpinBox()
        self.num_ofertas.setMinimum(1)
        self.num_ofertas.setValue(5)
        campos_layout.addWidget(QLabel("Número de ofertas a mostrar:"))
        campos_layout.addWidget(self.num_ofertas)
        # Botón buscar
        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.clicked.connect(self.buscar_ofertas)
        campos_layout.addWidget(self.btn_buscar)
        form_layout.addLayout(campos_layout)
        # Tabla de resultados
        self.tabla = QTableWidget(0, 5)
        self.tabla.setHorizontalHeaderLabels(["Título", "Ubicación", "Puesto", "Salario", "Tecnología"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        form_layout.addWidget(self.tabla)
        layout.addLayout(form_layout)
        self.setLayout(layout)

    def connect_db(self):
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
        except Exception as e:
            self.tabla.setRowCount(1)
            self.tabla.setItem(0, 0, QTableWidgetItem(f"Error conexión: {str(e)}"))

    def buscar_ofertas(self):
        palabra = self.palabra.text().strip()
        ubicacion = self.ubicacion.text().strip()
        puesto = self.puesto.text().strip()
        salario = self.salario.text().strip()
        tecnologia = self.tecnologia.text().strip()
        num_ofertas = self.num_ofertas.value()
        # Construir consulta dinámica (básica)
        query = "SELECT titulo, ubicacion, puesto, salario, tecnologia FROM busqueda_ofertalaboral WHERE 1=1"
        params = []
        if palabra:
            query += " AND (titulo ILIKE %s OR puesto ILIKE %s OR tecnologia ILIKE %s)"
            params.extend([f"%{palabra}%", f"%{palabra}%", f"%{palabra}%"])
        if ubicacion:
            query += " AND ubicacion ILIKE %s"
            params.append(f"%{ubicacion}%")
        if puesto:
            query += " AND puesto ILIKE %s"
            params.append(f"%{puesto}%")
        if salario:
            try:
                salario_num = int(salario)
                query += " AND salario >= %s"
                params.append(salario_num)
            except ValueError:
                pass
        if tecnologia:
            query += " AND tecnologia ILIKE %s"
            params.append(f"%{tecnologia}%")
        query += " ORDER BY id DESC LIMIT %s"
        params.append(num_ofertas)
        try:
            cur = self.conn.cursor()
            cur.execute(query, tuple(params))
            resultados = cur.fetchall()
            self.tabla.setRowCount(0)
            for row in resultados:
                row_position = self.tabla.rowCount()
                self.tabla.insertRow(row_position)
                for col, value in enumerate(row):
                    self.tabla.setItem(row_position, col, QTableWidgetItem(str(value)))
            cur.close()
            if not resultados:
                self.tabla.setRowCount(1)
                self.tabla.setItem(0, 0, QTableWidgetItem("No se encontraron resultados."))
        except Exception as e:
            self.tabla.setRowCount(1)
            self.tabla.setItem(0, 0, QTableWidgetItem(f"Error: {str(e)}"))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = BusquedaEmpleoApp()
    ventana.show()
    sys.exit(app.exec_())
