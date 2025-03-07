import sys
import logging
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QMainWindow, QApplication, QHBoxLayout, QMessageBox
from gui.login import LoginDialog
from gui.user_management_window import UserManagementWindow  
from gui.carrito import Carrito 
from core.database import inicializar_db

# Configuración de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MainWindow(QMainWindow):
    """Ventana principal según el rol del usuario."""
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Panel de Administración - ORDICO")
        self.setGeometry(100, 100, 400, 300)  

        if self.user_data["rol"] == "admin":
            self.show_admin_interface()
        else:
            self.show_cashier_interface()

    def show_admin_interface(self):
        """Interfaz para administrador."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)  

        self.btn_stock = QPushButton("Gestión de Stock")
        self.btn_users = QPushButton("Gestión de Usuarios")

        self.btn_stock.setFixedSize(200, 40)
        self.btn_users.setFixedSize(200, 40)

        btn_layout_stock = QHBoxLayout()
        btn_layout_stock.addStretch()
        btn_layout_stock.addWidget(self.btn_stock)
        btn_layout_stock.addStretch()

        btn_layout_users = QHBoxLayout()
        btn_layout_users.addStretch()
        btn_layout_users.addWidget(self.btn_users)
        btn_layout_users.addStretch()

        layout.addLayout(btn_layout_stock)
        layout.addLayout(btn_layout_users)

        self.btn_stock.clicked.connect(self.abrir_stock_window)
        self.btn_users.clicked.connect(self.abrir_users_window)

        self.central_widget.setLayout(layout)
    def show_cashier_interface(self):
        """Interfaz para cajeros."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)  

        self.btn_sales = QPushButton("Ventas")

        self.btn_sales.setFixedSize(200, 40)

        btn_layout_sales = QHBoxLayout()
        btn_layout_sales.addStretch()
        btn_layout_sales.addWidget(self.btn_sales)
        btn_layout_sales.addStretch()

        layout.addLayout(btn_layout_sales)

        self.btn_sales.clicked.connect(self.abrir_carrito)

        self.central_widget.setLayout(layout)
    def abrir_stock_window(self):
        """Abre la ventana de gestión de stock."""
        from gui.stock_window import StockWindow  # Importación dentro de la función
        self.stock_window = StockWindow(usuario_actual=self.user_data)
        self.stock_window.show()

    def abrir_users_window(self):
        """Abre la ventana de gestión de usuarios."""
        self.user_management_window = UserManagementWindow()
        self.user_management_window.show()

    def abrir_carrito(self):
        """Abre la ventana de ventas."""
        logging.info("🛒 Abriendo la ventana del carrito de compras...")
        self.carrito_window = Carrito()
        self.carrito_window.show()
    


def main():
    try:
        logging.info("✅ Inicializando la base de datos...")
        inicializar_db()  

        logging.info("✅ Creando la aplicación PyQt5...")
        app = QApplication.instance() or QApplication(sys.argv)

        logging.info("✅ Mostrando ventana de inicio de sesión...")
        login_dialog = LoginDialog()

        if login_dialog.exec_():  
            user_data = login_dialog.get_authenticated_user()  

            if not user_data:
                logging.error("❌ No se obtuvo información del usuario autenticado. Saliendo del programa.")
                sys.exit(1)

            logging.info(f"✅ Usuario autenticado: {user_data}")
            main_window = MainWindow(user_data)  
            main_window.show()
            app.exec_() 
        else:
            logging.info("❌ El usuario cerró la ventana de login. Saliendo del programa.")
            sys.exit(0)

    except Exception as e:
        logging.error(f"❌ Ocurrió un error: {e}")
        QMessageBox.critical(None, "Error", "Ocurrió un error inesperado. Reinicia la aplicación.")
        sys.exit(1)

    if not user_data:
        logging.error("❌ No se obtuvo información del usuario autenticado.")
        QMessageBox.critical(None, "Error", "No se pudo autenticar el usuario. Reinicia la aplicación.")
    return


if __name__ == "__main__":
    logging.info("🚀 Iniciando aplicación...")
    main()
