import pandas as pd
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QAction, QMessageBox
from PyQt5.QtCore import Qt
import logging
from gui.admin import AdminUsersDialog  # Asegurar que esta ruta es correcta

class MainWindow(QMainWindow):
    """Ventana principal mejorada con diseño tipo Excel e importación de archivos."""

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()

    def init_ui(self):
        """Configura la interfaz gráfica principal."""
        self.setWindowTitle("Sistema POS - Panel Principal")
        self.setGeometry(100, 100, 900, 600)

        # ✅ MENÚ SUPERIOR
        self.menu_bar = self.menuBar()
        self.configurar_menu()

        # ✅ WIDGET CENTRAL (Contenedor principal)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout_principal = QVBoxLayout()

        # ✅ MENSAJE DE BIENVENIDA
        username = self.user.get('username', 'Usuario')
        rol = self.user.get('rol', 'Invitado')
        self.label_bienvenida = QLabel(f"Bienvenido {username} ({rol})")
        self.label_bienvenida.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(self.label_bienvenida)

        # ✅ TABLA CENTRAL CON 5 COLUMNAS
        self.tabla = QTableWidget(10, 5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Precio", "Cantidad", "Presentación"])
        layout_principal.addWidget(self.tabla)

        # ✅ BOTONES DE ACCIÓN
        layout_botones = QHBoxLayout()
        self.btn_importar = QPushButton("Importar desde Excel")
        self.btn_agregar = QPushButton("Agregar Producto")
        self.btn_eliminar = QPushButton("Eliminar Producto")
        self.btn_editar = QPushButton("Editar Producto")

        layout_botones.addWidget(self.btn_importar)
        layout_botones.addWidget(self.btn_agregar)
        layout_botones.addWidget(self.btn_eliminar)
        layout_botones.addWidget(self.btn_editar)
        layout_principal.addLayout(layout_botones)

        central_widget.setLayout(layout_principal)

        # ✅ CONECTAR BOTONES
        self.btn_importar.clicked.connect(self.importar_excel)
        self.btn_agregar.clicked.connect(self.agregar_producto)
        self.btn_eliminar.clicked.connect(self.eliminar_producto)
        self.btn_editar.clicked.connect(self.editar_producto)

        # ✅ Cargar interfaz según rol
        if self.user["rol"] == "cajero":
            self.show_cashier_interface()
        elif self.user["rol"] == "admin":
            self.show_admin_interface()

    def configurar_menu(self):
        """Configura el menú de la ventana principal y restringe accesos según el rol."""
        menu_archivo = self.menu_bar.addMenu("Archivo")
        menu_gestion = self.menu_bar.addMenu("Gestión")

        salir_action = QAction("Salir", self)
        salir_action.triggered.connect(self.close)
        menu_archivo.addAction(salir_action)

        if self.user["rol"] == "admin":
            gestionar_stock_action = QAction("Gestionar Stock", self)
            gestionar_stock_action.triggered.connect(self.gestionar_stock)
            menu_gestion.addAction(gestionar_stock_action)

            admin_usuarios_action = QAction("Administrar Usuarios", self)
            admin_usuarios_action.triggered.connect(self.abrir_admin_usuarios)
            menu_gestion.addAction(admin_usuarios_action)

        if self.user["rol"] in ["cajero", "vendedor"]:
            generar_ticket_action = QAction("Generar Ticket", self)
            generar_ticket_action.triggered.connect(self.generar_ticket)
            menu_gestion.addAction(generar_ticket_action)

    def show_cashier_interface(self):
        """Interfaz para cajeros."""
        QMessageBox.information(self, "Modo Cajero", "Interfaz de cajero activada.")

    def show_admin_interface(self):
        """Interfaz para administradores."""
        QMessageBox.information(self, "Modo Administrador", "Interfaz de administrador activada.")

    def abrir_admin_usuarios(self):
        """Abre la ventana de administración de usuarios (solo para administradores)."""
        self.admin_users_dialog = AdminUsersDialog()
        self.admin_users_dialog.exec_()

    def importar_excel(self):
        """Permite seleccionar un archivo de Excel y cargar los datos en la tabla."""
        opciones = QFileDialog.Options()
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo Excel", "", "Archivos Excel (*.xlsx)", options=opciones)

        if archivo:
            try:
                logging.info(f"🔹 Importando archivo: {archivo}")
                df = pd.read_excel(archivo)  # Leer archivo Excel

                if df.empty:
                    logging.warning("⚠️ El archivo Excel está vacío.")
                    QMessageBox.warning(self, "Advertencia", "El archivo Excel está vacío.")
                    return

                if not all(isinstance(col, str) for col in df.columns):
                    logging.warning("⚠️ El archivo Excel no tiene el formato correcto.")
                    QMessageBox.warning(self, "Advertencia", "El archivo Excel no tiene el formato correcto.")
                    return

                self.tabla.setRowCount(0)
                self.tabla.setRowCount(len(df))
                self.tabla.setColumnCount(len(df.columns))
                self.tabla.setHorizontalHeaderLabels(df.columns)

                for fila in range(len(df)):
                    for columna in range(len(df.columns)):
                        item = QTableWidgetItem(str(df.iloc[fila, columna]))
                        self.tabla.setItem(fila, columna, item)

                logging.info("✅ Archivo importado exitosamente.")
                QMessageBox.information(self, "Éxito", "Archivo importado exitosamente.")

            except Exception as e:
                logging.error(f"❌ Error al importar el archivo: {e}")
                QMessageBox.critical(self, "Error", f"No se pudo importar el archivo.\n{e}")

    # ✅ FUNCIONES DE BOTONES (Se implementarán en pasos siguientes)
    def agregar_producto(self):
        logging.info("🔹 Agregar Producto (Función en desarrollo)")

    def eliminar_producto(self):
        logging.info("🔹 Eliminar Producto (Función en desarrollo)")

    def editar_producto(self):
        logging.info("🔹 Editar Producto (Función en desarrollo)")

    def gestionar_stock(self):
        """Función temporal para gestionar stock."""
        QMessageBox.information(self, "Gestionar Stock", "Funcionalidad para gestionar stock (En desarrollo)")

    def generar_ticket(self):
        """Función temporal para generar un ticket."""
        QMessageBox.information(self, "Generar Ticket", "Funcionalidad para generar ticket (En desarrollo)")
