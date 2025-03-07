from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QLineEdit, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QLabel
from core.database import obtener_productos, agregar_producto, actualizar_producto, inicializar_db, importar_desde_excel
from core.database import eliminar_producto as eliminar_producto_db  # Renombramos solo eliminar_producto
from .agregar_producto_dialog import AgregarProductoDialog
import logging
import pandas as pd

class StockWindow(QWidget):
    """Ventana para la gestión del stock de productos."""

    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.usuario_es_admin = self.usuario_actual.get("rol") == "admin"
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de gestión de stock."""
        self.setWindowTitle("Gestión de Stock")
        self.setGeometry(200, 200, 900, 500)

        layout = QVBoxLayout()
        self.label = QLabel("Gestión de Stock")
        layout.addWidget(self.label)

        self.campo_busqueda = QLineEdit()
        self.campo_busqueda.setPlaceholderText("Buscar producto...")
        layout.addWidget(self.campo_busqueda)
        self.campo_busqueda.textChanged.connect(self.filtrar_productos)

        self.tabla_stock = QTableWidget()
        self.tabla_stock.setColumnCount(6)
        self.tabla_stock.setHorizontalHeaderLabels(["ID", "Nombre", "Marca", "Cantidad", "Precio", "Categoría"])
        self.tabla_stock.setSortingEnabled(True)
        self.tabla_stock.horizontalHeader().setStretchLastSection(True)
        self.tabla_stock.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_stock.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.tabla_stock)

        botones_layout = QHBoxLayout()
        self.btn_actualizar = QPushButton("Actualizar Stock")
        self.btn_agregar = QPushButton("Agregar Producto")
        self.btn_editar = QPushButton("Editar Producto")
        self.btn_eliminar = QPushButton("Eliminar Producto")
        self.btn_importar = QPushButton("Importar desde Excel")

        for btn in [self.btn_actualizar, self.btn_agregar, self.btn_editar, self.btn_eliminar, self.btn_importar]:
            btn.setFixedSize(200, 40)
            botones_layout.addWidget(btn)

        layout.addLayout(botones_layout)

        self.btn_actualizar.clicked.connect(self.cargar_stock)
        self.btn_agregar.clicked.connect(self.agregar_producto)
        self.btn_editar.clicked.connect(self.editar_producto)
        self.btn_eliminar.clicked.connect(self.eliminar_producto)
        self.btn_importar.clicked.connect(self.importar_desde_excel)

        self.setLayout(layout)
        self.cargar_stock()

    def cargar_stock(self):
        """Carga los productos en la tabla desde la base de datos."""
        try:
            productos = obtener_productos() or []
            self.tabla_stock.setRowCount(len(productos))

            for i, producto in enumerate(productos):
                id_producto, nombre, marca, cantidad, precio, categoria = producto  
                self.tabla_stock.setItem(i, 0, QTableWidgetItem(str(id_producto)))
                self.tabla_stock.setItem(i, 1, QTableWidgetItem(nombre))
                self.tabla_stock.setItem(i, 2, QTableWidgetItem(marca))  
                self.tabla_stock.setItem(i, 3, QTableWidgetItem(str(cantidad)))
                self.tabla_stock.setItem(i, 4, QTableWidgetItem(str(precio)))
                self.tabla_stock.setItem(i, 5, QTableWidgetItem(categoria))

        except Exception as e:
            logging.error(f"❌ Error al cargar stock: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo cargar el stock: {e}")

    def filtrar_productos(self):
        """Filtra los productos en la tabla según el texto ingresado."""
        texto = self.campo_busqueda.text().lower()
        for fila in range(self.tabla_stock.rowCount()):
            visible = any(
                texto in self.tabla_stock.item(fila, col).text().lower() if self.tabla_stock.item(fila, col) else False
                for col in range(self.tabla_stock.columnCount())
            )
            self.tabla_stock.setRowHidden(fila, not visible)

    def agregar_producto(self):
        """Abre el diálogo para agregar un nuevo producto."""
        if not self.usuario_es_admin:
            QMessageBox.warning(self, "Acceso Denegado", "Solo los administradores pueden agregar productos.")
            return

        dialogo = AgregarProductoDialog()
        if dialogo.exec_():
            self.cargar_stock()

    def editar_producto(self):
        """Edita un producto existente en la base de datos."""
        if not self.usuario_es_admin:
            QMessageBox.warning(self, "Acceso Denegado", "Solo los administradores pueden editar productos.")
            return

        fila_seleccionada = self.tabla_stock.currentRow()
        if fila_seleccionada < 0:
            QMessageBox.warning(self, "Error", "Por favor, seleccione un producto para editar.")
            return

        id_producto = self.tabla_stock.item(fila_seleccionada, 0)
        if id_producto is None:
            QMessageBox.warning(self, "Error", "Producto no válido.")
            return

        id_producto = id_producto.text()
        nombre = self.tabla_stock.item(fila_seleccionada, 1).text()
        marca = self.tabla_stock.item(fila_seleccionada, 2).text()
        cantidad = self.tabla_stock.item(fila_seleccionada, 3).text()
        precio = self.tabla_stock.item(fila_seleccionada, 4).text()
        categoria = self.tabla_stock.item(fila_seleccionada, 5).text()

        dialogo = AgregarProductoDialog()
        dialogo.input_nombre.setText(nombre)
        dialogo.input_marca.setText(marca)
        dialogo.input_cantidad.setText(cantidad)
        dialogo.input_precio.setText(precio)
        dialogo.input_categoria.setCurrentText(categoria)

        if dialogo.exec_():
            actualizar_producto(id_producto, nombre, marca, cantidad, precio, categoria)  # ✅ ACTUALIZA el producto
            self.cargar_stock()

    def eliminar_producto(self):
        """Elimina un producto del stock."""
        if not self.usuario_es_admin:
            QMessageBox.warning(self, "Acceso Denegado", "Solo los administradores pueden eliminar productos.")
            return

        fila_seleccionada = self.tabla_stock.currentRow()
        if fila_seleccionada < 0:
            QMessageBox.warning(self, "Error", "Por favor, seleccione un producto para eliminar.")
            return

        item_id = self.tabla_stock.item(fila_seleccionada, 0)
        if item_id is None:
            QMessageBox.warning(self, "Error", "Producto no válido.")
            return

        id_producto = item_id.text()
        confirmacion = QMessageBox.question(
            self, "Eliminar Producto", f"¿Seguro que quieres eliminar el producto ID {id_producto}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if confirmacion == QMessageBox.Yes:
            if eliminar_producto_db(id_producto):
                QMessageBox.information(self, "Éxito", "Producto eliminado correctamente.")
                self.cargar_stock()
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el producto.")

    def importar_desde_excel(self):
        """Importa productos desde un archivo Excel."""
        if not self.usuario_es_admin:
            QMessageBox.warning(self, "Acceso Denegado", "Solo los administradores pueden importar productos.")
            return

        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo", "", "Archivos Excel (*.xlsx)")
        if archivo:
            if importar_desde_excel(archivo):
                QMessageBox.information(self, "Éxito", "Productos importados correctamente.")
                self.cargar_stock()
            else:
                QMessageBox.warning(self, "Error", "No se pudo importar los productos.")

        else:
            QMessageBox.warning(self, "Error", "No se selecciono ningun archivo.")