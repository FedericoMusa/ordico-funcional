import logging
import sys
from PyQt5.QtWidgets import QDialog,QVBoxLayout, QFormLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox, QFileDialog, QWidget, QTableWidget, QHeaderView, QHBoxLayout, QTableWidgetItem
from core.database import agregar_producto, obtener_productos

categorias_en_memoria = [
    "Comestibles", "Lácteos", "Panadería", "Dulces", "Jardinería",
    "Cuidado personal", "Carnes rojas", "Carnes blancas", "Productos Varios"
]

class AgregarProductoDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de agregar producto con sugerencias de categoría."""
        self.setWindowTitle("Agregar Producto")
        self.setGeometry(200, 200, 400, 300)

        form_layout = QFormLayout()

        self.input_nombre = QLineEdit()
        self.input_marca = QLineEdit()
        self.input_cantidad = QLineEdit()
        self.input_precio = QLineEdit()

        # 🔹 QComboBox para sugerir categorías
        self.input_categoria = QComboBox()
        self.input_categoria.setEditable(True)  # Permite que el usuario escriba nuevas categorías
        self.input_categoria.addItems(categorias_en_memoria)  # Carga las categorías existentes en memoria

        form_layout.addRow(QLabel("Nombre:"), self.input_nombre)
        form_layout.addRow(QLabel("Marca:"), self.input_marca)
        form_layout.addRow(QLabel("Cantidad:"), self.input_cantidad)
        form_layout.addRow(QLabel("Precio:"), self.input_precio)
        form_layout.addRow(QLabel("Categoría:"), self.input_categoria)  # ✅ Categoría con sugerencias

        self.btn_guardar = QPushButton("Guardar")
        self.btn_cancelar = QPushButton("Cancelar")

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.btn_guardar)
        layout.addWidget(self.btn_cancelar)
        self.setLayout(layout)

        self.btn_guardar.clicked.connect(self.guardar_producto)
        self.btn_cancelar.clicked.connect(self.close)

    def guardar_producto(self):
        """Guarda el producto y actualiza la lista de categorías en memoria."""
        nombre = self.input_nombre.text().strip()
        marca = self.input_marca.text().strip()
        cantidad_texto = self.input_cantidad.text().strip()
        precio_texto = self.input_precio.text().strip()
        categoria = self.input_categoria.currentText().strip()  # ✅ Obtiene la categoría del QComboBox

        if not nombre or not marca or not cantidad_texto or not precio_texto:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return

        try:
            cantidad = int(cantidad_texto)
            precio = float(precio_texto)
        except ValueError:
            QMessageBox.warning(self, "Error", "Cantidad y precio deben ser valores numéricos válidos.")
            return

        # ✅ Agregar categoría a la memoria si no existe
        if categoria and categoria not in categorias_en_memoria:
            categorias_en_memoria.append(categoria)  # Se guarda en memoria para futuras sugerencias

        # ✅ Llamar a la función que guarda en la base de datos (sin ID)
        if agregar_producto(nombre, marca, cantidad, precio, categoria):
            QMessageBox.information(self, "Éxito", "Producto agregado correctamente.")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "No se pudo agregar el producto.")

class StockWindow(QWidget):
    """Ventana para la gestión del stock de productos."""

    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual  # Guarda los datos completos del usuario
        self.usuario_es_admin = self.usuario_actual.get("rol") == "admin"  # Evalúa si es admin
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de gestión de stock."""
        self.setWindowTitle("Gestión de Stock")
        self.setGeometry(200, 200, 800, 500)

        layout = QVBoxLayout()

        # Título
        self.label = QLabel("Gestión de Stock")
        layout.addWidget(self.label)

        # Campo de búsqueda
        self.campo_busqueda = QLineEdit()
        self.campo_busqueda.setPlaceholderText("Buscar producto...")
        layout.addWidget(self.campo_busqueda)
        self.campo_busqueda.textChanged.connect(self.filtrar_productos)

        # Tabla de productos
        self.tabla_stock = QTableWidget()
        self.tabla_stock.setColumnCount(4)
        self.tabla_stock.setHorizontalHeaderLabels(["ID", "Nombre", "Cantidad", "Precio"])
        self.tabla_stock.setSortingEnabled(True)
        self.tabla_stock.horizontalHeader().setStretchLastSection(True)
        self.tabla_stock.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_stock.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.tabla_stock)

        # Botones de acción
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

        # Conectar botones a funciones
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
                for j, dato in enumerate(producto):
                    self.tabla_stock.setItem(i, j, QTableWidgetItem(str(dato)))

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
        """Abre el diálogo para agregar un nuevo producto. Solo el admin puede hacerlo."""
        if not self.usuario_es_admin:
            QMessageBox.warning(self, "Acceso Denegado", "Solo los administradores pueden agregar productos.")
            return

        dialogo = AgregarProductoDialog()
        if dialogo.exec_():
            self.cargar_stock()  # Refresca la tabla después de agregar
