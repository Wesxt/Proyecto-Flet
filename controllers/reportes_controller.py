import os
from fpdf import FPDF
from models.report import Report
from models.sale import Sale
from models.product import Product

class ReportesController:
    def __init__(self, view):
        self.view = view

    def get_reports(self):
        return Report.get_all()

    def delete_report(self, report_id):
        return Report.delete(report_id)

    def generate_report(self, start, end, tipo):
        if not start or not end:
            return False, "Por favor, seleccione ambas fechas"

        import sqlite3
        from core.database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            summary = ""
            if tipo == "Ventas Generales":
                cursor.execute("SELECT SUM(total) as total_ventas, COUNT(*) as cant_ventas FROM sales WHERE datetime(date, 'localtime') BETWEEN ? AND ?", (start + " 00:00:00", end + " 23:59:59"))
                res = cursor.fetchone()
                total = res["total_ventas"] if res["total_ventas"] else 0
                cant = res["cant_ventas"] if res else 0
                if cant == 0:
                    return False, "No hay ventas registradas en las fechas seleccionadas"
                summary = f"Ventas Totales: ${total:,.2f} | Cantidad: {cant}"
            
            elif tipo == "Ventas por Cajero":
                cursor.execute('''
                    SELECT u.fullname, SUM(s.total) as total
                    FROM sales s JOIN users u ON s.user_id = u.id
                    WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? GROUP BY u.id ORDER BY total DESC LIMIT 1
                ''', (start + " 00:00:00", end + " 23:59:59"))
                res = cursor.fetchone()
                if not res:
                    return False, "No hay ventas en estas fechas"
                summary = f"Mejor Cajero: {res['fullname']} (${res['total']:,.2f})"

            elif tipo == "Ventas por Cliente":
                cursor.execute('''
                    SELECT c.fullname, SUM(s.total) as total
                    FROM sales s JOIN clients c ON s.client_id = c.id
                    WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? GROUP BY c.id ORDER BY total DESC LIMIT 1
                ''', (start + " 00:00:00", end + " 23:59:59"))
                res = cursor.fetchone()
                if not res:
                    return False, "No hay ventas a clientes registrados en estas fechas"
                summary = f"Mejor Cliente: {res['fullname']} (${res['total']:,.2f})"

            elif tipo == "Inventario Actual":
                cursor.execute("SELECT SUM(stock * price_buy) as valor_inv FROM products WHERE status = 1")
                res = cursor.fetchone()
                valor = res["valor_inv"] if res["valor_inv"] else 0
                summary = f"Valor total del Inventario: ${valor:,.2f}"

            elif tipo == "Inventario Bajo Stock":
                cursor.execute("SELECT COUNT(id) as cant FROM products WHERE stock <= stock_min AND status = 1")
                res = cursor.fetchone()
                summary = f"Productos en alerta crítica: {res['cant']}"

            elif tipo == "Productos Más Vendidos":
                cursor.execute('''
                    SELECT p.name, SUM(sd.quantity) as qty
                    FROM sale_details sd JOIN products p ON sd.product_id = p.id
                    JOIN sales s ON sd.sale_id = s.id
                    WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? GROUP BY p.id ORDER BY qty DESC LIMIT 1
                ''', (start + " 00:00:00", end + " 23:59:59"))
                res = cursor.fetchone()
                if not res:
                    return False, "No hay productos vendidos en este periodo"
                summary = f"Top Producto: {res['name']} ({res['qty']} uds)"
                
            elif tipo == "Ganancias por Producto":
                cursor.execute('''
                    SELECT SUM((p.price_sell - p.price_buy) * sd.quantity) as ganancia
                    FROM sale_details sd JOIN products p ON sd.product_id = p.id
                    JOIN sales s ON sd.sale_id = s.id
                    WHERE datetime(s.date, 'localtime') BETWEEN ? AND ?
                ''', (start + " 00:00:00", end + " 23:59:59"))
                res = cursor.fetchone()
                ganancia = res["ganancia"] if res and res["ganancia"] else 0
                summary = f"Ganancia Total Est.: ${ganancia:,.2f}"

            # Create Report
            Report.create(tipo, start, end, summary)
            return True, f"Reporte de {tipo} generado con éxito"
        except Exception as ex:
            return False, f"Error al generar reporte: {ex}"
        finally:
            conn.close()

    def export_report(self, report_id):
        report = Report.get_by_id(report_id)
        if not report:
            return False, "Reporte no encontrado"

        tipo = report.type
        st = report.start_date
        ed = report.end_date

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 16)
        pdf.cell(0, 10, text=f"Reporte: {tipo}", new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.set_font("helvetica", size=12)
        pdf.cell(0, 10, text=f"Periodo: {report.start_date} al {report.end_date}", new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.cell(0, 10, text=f"Resumen: {report.summary}", new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.ln(10)

        # Query using models
        if tipo == "Ventas Generales":
            sales = Sale.get_sales_for_period(st, ed)
            if sales:
                pdf.set_font("helvetica", 'B', 10)
                pdf.cell(15, 10, 'ID', border=1)
                pdf.cell(40, 10, 'Fecha', border=1)
                pdf.cell(40, 10, 'Cajero', border=1)
                pdf.cell(40, 10, 'Cliente', border=1)
                pdf.cell(25, 10, 'Método', border=1)
                pdf.cell(30, 10, 'Total', border=1, new_x="LMARGIN", new_y="NEXT")
                
                pdf.set_font("helvetica", size=9)
                for s in sales:
                    pdf.cell(15, 8, str(s['id']), border=1)
                    pdf.cell(40, 8, s['local_date'][:16], border=1)
                    pdf.cell(40, 8, str(s['cajero'])[:15] if s['cajero'] else "N/A", border=1)
                    pdf.cell(40, 8, str(s['cliente'])[:15] if s['cliente'] else "N/A", border=1)
                    pdf.cell(25, 8, str(s['payment_method'])[:10], border=1)
                    pdf.cell(30, 8, f"${s['total']:.2f}", border=1, new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.cell(0, 10, text="No hay ventas.", new_x="LMARGIN", new_y="NEXT", align='C')

        elif tipo == "Ventas por Cajero":
            rows = Sale.get_sales_by_cashier(st, ed)
            if rows:
                pdf.set_font("helvetica", 'B', 12)
                pdf.cell(80, 10, 'Cajero', border=1)
                pdf.cell(40, 10, 'Cant. Ventas', border=1)
                pdf.cell(50, 10, 'Total Generado', border=1, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", size=10)
                for r in rows:
                    pdf.cell(80, 8, str(r['fullname']), border=1)
                    pdf.cell(40, 8, str(r['cant']), border=1)
                    pdf.cell(50, 8, f"${r['total']:.2f}", border=1, new_x="LMARGIN", new_y="NEXT")

        elif tipo == "Ventas por Cliente":
            rows = Sale.get_sales_by_client(st, ed)
            if rows:
                pdf.set_font("helvetica", 'B', 12)
                pdf.cell(70, 10, 'Cliente', border=1)
                pdf.cell(40, 10, 'Documento', border=1)
                pdf.cell(30, 10, 'Ventas', border=1)
                pdf.cell(50, 10, 'Total Comprado', border=1, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", size=10)
                for r in rows:
                    pdf.cell(70, 8, str(r['fullname'])[:25], border=1)
                    pdf.cell(40, 8, str(r['doc_num']), border=1)
                    pdf.cell(30, 8, str(r['cant']), border=1)
                    pdf.cell(50, 8, f"${r['total']:.2f}", border=1, new_x="LMARGIN", new_y="NEXT")

        elif tipo == "Inventario Actual":
            rows = Product.get_active()
            if rows:
                pdf.set_font("helvetica", 'B', 10)
                pdf.cell(80, 10, 'Producto', border=1)
                pdf.cell(20, 10, 'Stock', border=1)
                pdf.cell(20, 10, 'Min', border=1)
                pdf.cell(30, 10, 'P. Compra', border=1)
                pdf.cell(30, 10, 'P. Venta', border=1, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", size=9)
                for r in rows:
                    pdf.cell(80, 8, str(r.name)[:35], border=1)
                    pdf.cell(20, 8, str(r.stock), border=1)
                    pdf.cell(20, 8, str(r.stock_min), border=1)
                    pdf.cell(30, 8, f"${r.price_buy:.2f}", border=1)
                    pdf.cell(30, 8, f"${r.price_sell:.2f}", border=1, new_x="LMARGIN", new_y="NEXT")

        elif tipo == "Inventario Bajo Stock":
            rows = Product.get_alerts()
            if rows:
                pdf.set_font("helvetica", 'B', 12)
                pdf.cell(100, 10, 'Producto', border=1)
                pdf.cell(40, 10, 'Stock Actual', border=1)
                pdf.cell(40, 10, 'Stock Mínimo', border=1, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", size=10)
                for r in rows:
                    pdf.cell(100, 8, str(r.name)[:40], border=1)
                    pdf.cell(40, 8, str(r.stock), border=1)
                    pdf.cell(40, 8, str(r.stock_min), border=1, new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.cell(0, 10, text="No hay productos con bajo stock.", new_x="LMARGIN", new_y="NEXT", align='C')

        elif tipo == "Productos Más Vendidos":
            rows = Sale.get_top_selling_products(st, ed)
            if rows:
                pdf.set_font("helvetica", 'B', 12)
                pdf.cell(100, 10, 'Producto', border=1)
                pdf.cell(40, 10, 'Cant. Vendida', border=1)
                pdf.cell(50, 10, 'Ingresos Brutos', border=1, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", size=10)
                for r in rows:
                    pdf.cell(100, 8, str(r['name'])[:40], border=1)
                    pdf.cell(40, 8, str(r['qty']), border=1)
                    pdf.cell(50, 8, f"${r['total']:.2f}", border=1, new_x="LMARGIN", new_y="NEXT")

        elif tipo == "Ganancias por Producto":
            rows = Sale.get_profits_by_product(st, ed)
            if rows:
                pdf.set_font("helvetica", 'B', 10)
                pdf.cell(70, 10, 'Producto', border=1)
                pdf.cell(20, 10, 'Cant.', border=1)
                pdf.cell(30, 10, 'Costo Total', border=1)
                pdf.cell(35, 10, 'Ingreso Bruto', border=1)
                pdf.cell(35, 10, 'Ganancia Neta', border=1, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", size=9)
                for r in rows:
                    pdf.cell(70, 8, str(r['name'])[:30], border=1)
                    pdf.cell(20, 8, str(r['qty']), border=1)
                    pdf.cell(30, 8, f"${r['costo']:.2f}", border=1)
                    pdf.cell(35, 8, f"${r['ingreso']:.2f}", border=1)
                    pdf.cell(35, 8, f"${r['ganancia']:.2f}", border=1, new_x="LMARGIN", new_y="NEXT")

        if not os.path.exists("exportaciones"):
            os.makedirs("exportaciones")
            
        filename = f"exportaciones/Reporte_{report.start_date}_{report.end_date}_{report_id}.pdf"
        try:
            pdf.output(filename)
            return True, "Reporte PDF guardado en la carpeta 'exportaciones'"
        except Exception as e:
            return False, f"Error al exportar: {str(e)}"
