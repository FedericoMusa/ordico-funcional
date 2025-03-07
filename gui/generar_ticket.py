from fpdf import FPDF
import os
from tkinter import Tk, filedialog
import webbrowser

def generar_ticket_pdf(empresa, productos, subtotal, total, impuestos):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, empresa['nombre'], ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"CUIT: {empresa['cuit']}", ln=True, align='C')
    pdf.cell(200, 10, f"Dirección: {empresa.get('direccion', empresa.get('Direccion', 'No disponible'))}", ln=True, align='C')
    pdf.cell(200, 10, "------------------------------------------", ln=True, align='C')
    pdf.set_font("Arial", "B", 12)
    pdf.cell(40, 10, "Cantidad", border=1)
    pdf.cell(80, 10, "Producto", border=1)
    pdf.cell(30, 10, "Precio U.", border=1)
    pdf.cell(40, 10, "Total", border=1, ln=True)
    
    pdf.set_font("Arial", "", 12)
    for producto in productos:
        pdf.cell(40, 10, str(producto['cantidad']), border=1)
        pdf.cell(80, 10, producto['nombre'], border=1)
        pdf.cell(30, 10, f"${producto['precio_unitario']:.2f}", border=1)
        pdf.cell(40, 10, f"${producto['total']:.2f}", border=1, ln=True)
    
    pdf.cell(200, 10, "------------------------------------------", ln=True, align='C')
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, f"Subtotal: ${subtotal:.2f}", ln=True, align='R')
    pdf.cell(200, 10, f"Impuestos: ${impuestos:.2f}", ln=True, align='R')
    pdf.cell(200, 10, f"Total: ${total:.2f}", ln=True, align='R')
    
    # Guardar el archivo
    Tk().withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if file_path:
        pdf.output(file_path)
        webbrowser.open(file_path)

# Ejemplo de uso
datos_empresa = {"nombre": "ORDICO", "cuit": "30-12345678-9", "Direccion": "Ruta 60, km 6"}
productos = [{"nombre": "Arroz", "cantidad": 2, "precio_unitario": 150.0, "total": 300.0},
    {"nombre": "Fideos", "cantidad": 1, "precio_unitario": 120.0, "total": 120.0}]
subtotal = 420.0
total = 508.2
impuestos = 88.2

generar_ticket_pdf(datos_empresa, productos, subtotal, total, impuestos)
