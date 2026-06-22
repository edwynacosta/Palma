import os
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QDesktopServices
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QFrame,
    QPushButton, QLabel, QScrollArea, QMessageBox, QComboBox, QDoubleSpinBox
)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class TarjetaFacturaHistorial(QFrame):
    def __init__(self, id_fact, cliente, total, fecha, ruta_pdf, parent=None):
        super().__init__(parent)
        self.ruta_pdf = ruta_pdf
        self.setFixedHeight(85)
        self.setStyleSheet("QFrame { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; } QFrame:hover { border: 1px solid #008F39; }")
        
        layout = QHBoxLayout(self)
        info_layout = QVBoxLayout()
        lbl_id = QLabel(f"<b>#{id_fact}</b> • <span style='color:#64748B;'>{fecha}</span>")
        lbl_cli = QLabel(str(cliente).title())
        lbl_cli.setStyleSheet("color: #1B4314; font-weight: bold; border: none;")
        
        info_layout.addWidget(lbl_id); info_layout.addWidget(lbl_cli)
        
        btn_pdf = QPushButton("VER PDF")
        btn_pdf.setFixedSize(80, 36)
        btn_pdf.setStyleSheet("QPushButton { background-color: #E2E8F0; color: #1B4314; border-radius: 8px; font-weight:bold; } QPushButton:hover { background-color: #008F39; color: white; }")
        btn_pdf.clicked.connect(self.abrir_pdf)
        
        layout.addLayout(info_layout); layout.addStretch(); layout.addWidget(btn_pdf)

    def abrir_pdf(self):
        if os.path.exists(self.ruta_pdf): QDesktopServices.openUrl(QUrl.fromLocalFile(self.ruta_pdf))
        else: QMessageBox.warning(self, "Error", "Archivo no encontrado.")

class FacturaElectronicaVista(QWidget):
    def __init__(self, conexion=None, datos_usuario=None, parent=None):
        super().__init__(parent)
        self.conexion = conexion
        self.carpeta_pdfs = os.path.join(os.getcwd(), "facturas_pdf")
        os.makedirs(self.carpeta_pdfs, exist_ok=True)
        self.init_ui()
        self.cargar_clientes()

    def init_ui(self):
        layout_principal = QHBoxLayout(self)
        panel_izq = QFrame(self)
        panel_izq.setStyleSheet("background-color: #FFFFFF; border-radius: 24px; border: 1px solid #E2E8F0;")
        layout_izq = QVBoxLayout(panel_izq)
        
        self.combo_cliente = QComboBox()
        self.txt_concepto = QLineEdit("Compra de productos")
        self.spin_monto = QDoubleSpinBox()
        self.spin_monto.setRange(0, 999999999)
        self.spin_monto.setPrefix("$ ")
        
        self.btn_emitir = QPushButton("EMITIR FACTURA")
        self.btn_emitir.setStyleSheet("background-color: #008F39; color: white; border-radius: 12px; font-weight: bold; padding: 15px;")
        self.btn_emitir.clicked.connect(self.procesar_factura)
        
        layout_izq.addWidget(QLabel("CLIENTE:")); layout_izq.addWidget(self.combo_cliente)
        layout_izq.addWidget(QLabel("CONCEPTO:")); layout_izq.addWidget(self.txt_concepto)
        layout_izq.addWidget(QLabel("VALOR TOTAL:")); layout_izq.addWidget(self.spin_monto)
        layout_izq.addWidget(self.btn_emitir); layout_izq.addStretch()

        panel_der = QScrollArea()
        panel_der.setWidgetResizable(True)
        self.contenedor_lista = QWidget()
        self.layout_lista = QVBoxLayout(self.contenedor_lista)
        self.layout_lista.addStretch()
        panel_der.setWidget(self.contenedor_lista)

        layout_principal.addWidget(panel_izq, 40); layout_principal.addWidget(panel_der, 60)

    def cargar_clientes(self):
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                cursor.execute("SELECT nombre_cliente FROM clientes")
                for (nombre,) in cursor.fetchall():
                    self.combo_cliente.addItem(nombre)
                cursor.close()
            except Exception as e: print(f"Error cargando clientes: {e}")

    def procesar_factura(self):
        id_fac = datetime.now().strftime("%Y%m%d%H%M%S")
        ruta = os.path.join(self.carpeta_pdfs, f"Factura_{id_fac}.pdf")
        
        c = canvas.Canvas(ruta, pagesize=letter)
        c.drawString(100, 750, f"Factura #{id_fac}")
        c.drawString(100, 730, f"Cliente: {self.combo_cliente.currentText()}")
        c.drawString(100, 710, f"Total: {self.spin_monto.text()}")
        c.save()
        
        self.layout_lista.insertWidget(0, TarjetaFacturaHistorial(id_fac, self.combo_cliente.currentText(), self.spin_monto.value(), "Hoy", ruta))
        QMessageBox.information(self, "Éxito", "Factura generada.")