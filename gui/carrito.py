from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QSpinBox
from gui.generar_ticket import generar_ticket_pdf
import sqlite3

class Carrito(QDialog):
    """Ventana de ventas (para cajeros)"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.carrito = []
    
    def init_ui(self):
        self.setWindowTitle("Carrito de Compras")
        self.setGeometry(150, 150, 600, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Buscar Producto:")
        self.layout.addWidget(self.label)

        self.entrada_busqueda = QLineEdit()
        self.layout.addWidget(self.entrada_busqueda)

        self.boton_buscar = QPushButton("Buscar")
        self.boton_buscar.clicked.connect(self.buscar_productos)
        self.layout.addWidget(self.boton_buscar)

        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(4)
        self.tabla_productos.setHorizontalHeaderLabels(["ID", "Nombre", "Precio", "Cantidad Disponible"])
        self.layout.addWidget(self.tabla_productos)

        self.label_cantidad = QLabel("Cantidad a Comprar:")
        self.layout.addWidget(self.label_cantidad)
        
        self.cantidad_spinbox = QSpinBox()
        self.cantidad_spinbox.setMinimum(1)
        self.layout.addWidget(self.cantidad_spinbox)

        self.boton_agregar = QPushButton("Agregar al Carrito")
        self.boton_agregar.clicked.connect(self.agregar_al_carrito)
        self.layout.addWidget(self.boton_agregar)

        self.tabla_carrito = QTableWidget()
        self.tabla_carrito.setColumnCount(4)
        self.tabla_carrito.setHorizontalHeaderLabels(["ID", "Nombre", "Precio", "Cantidad"])
        self.layout.addWidget(self.tabla_carrito)

        self.boton_eliminar = QPushButton("Eliminar del Carrito")
        self.boton_eliminar.clicked.connect(self.eliminar_del_carrito)
        self.layout.addWidget(self.boton_eliminar)

        self.boton_finalizar = QPushButton("Finalizar Compra")
        self.boton_finalizar.clicked.connect(self.finalizar_compra)
        self.layout.addWidget(self.boton_finalizar)

    def buscar_productos(self):
        query = self.entrada_busqueda.text()
        conn = sqlite3.connect("ordico.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, precio, cantidad FROM productos WHERE nombre LIKE ?", ('%' + query + '%',))
        productos = cursor.fetchall()
        conn.close()

        self.tabla_productos.setRowCount(len(productos))
        for row_idx, producto in enumerate(productos):
            for col_idx, dato in enumerate(producto):
                self.tabla_productos.setItem(row_idx, col_idx, QTableWidgetItem(str(dato)))

    def agregar_al_carrito(self):
        selected_row = self.tabla_productos.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un producto.")
            return

        id_producto = self.tabla_productos.item(selected_row, 0).text()
        nombre = self.tabla_productos.item(selected_row, 1).text()
        precio = float(self.tabla_productos.item(selected_row, 2).text())
        cantidad_disponible = int(self.tabla_productos.item(selected_row, 3).text())
        cantidad_a_comprar = self.cantidad_spinbox.value()

        if cantidad_a_comprar > cantidad_disponible:
            QMessageBox.warning(self, "Error", "Stock insuficiente para la cantidad solicitada.")
            return

        if cantidad_disponible <= 5:
            QMessageBox.warning(self, "Advertencia", f"Quedan pocos productos en stock: {cantidad_disponible} unidades.")

        self.carrito.append([id_producto, nombre, precio, cantidad_a_comprar])
        self.actualizar_carrito()

    def eliminar_del_carrito(self):
        selected_row = self.tabla_carrito.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un producto para eliminar.")
            return
        
        del self.carrito[selected_row]
        self.actualizar_carrito()

    def actualizar_carrito(self):
        self.tabla_carrito.setRowCount(len(self.carrito))
        for row_idx, producto in enumerate(self.carrito):
            for col_idx, dato in enumerate(producto):
                self.tabla_carrito.setItem(row_idx, col_idx, QTableWidgetItem(str(dato)))

    def finalizar_compra(self):
        """Finaliza la compra y genera el ticket en PDF"""
        if not self.carrito:
            QMessageBox.warning(self, "Carrito vacío", "No hay productos en el carrito.")
            return

        datos_empresa = {
            "nombre": "ORDICO",
            "cuit": "30-12345678-9",
            "direccion": "Calle Falsa 123"
        }

        print("📄 Datos de la empresa ANTES de generar el ticket:", datos_empresa)
        
        productos = [{
            "nombre": item[1],
            "cantidad": item[3],
            "precio_unitario": item[2],
            "total": item[3] * item[2]
        } for item in self.carrito]

        subtotal = sum(p["total"] for p in productos)
        impuestos = subtotal * 0.21
        total = subtotal + impuestos

        try:
            generar_ticket_pdf(datos_empresa, productos, subtotal, total, impuestos)
            QMessageBox.information(self, "Compra finalizada", "El ticket ha sido generado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error al generar el ticket", f"Ocurrió un error: {str(e)}")

        self.carrito = []
