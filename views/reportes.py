import flet as ft
from core.colors import *
from core.database import get_connection
import datetime

def ReportesView(page: ft.Page):
    """
    Módulo de Reportes con CRUD real y DatePickers.
    """
    
    # --- Referencias a Controles ---
    tf_start = ft.TextField(label="Fecha de inicio", hint_text="YYYY-MM-DD", expand=True, read_only=True)
    tf_end = ft.TextField(label="Fecha de corte", hint_text="YYYY-MM-DD", expand=True, read_only=True)
    
    # --- DatePickers Logic ---
    def handle_start_change(e):
        if date_picker_start.value:
            tf_start.value = date_picker_start.value.strftime("%Y-%m-%d")
        date_picker_start.open = False
        page.update()

    def handle_end_change(e):
        if date_picker_end.value:
            tf_end.value = date_picker_end.value.strftime("%Y-%m-%d")
        date_picker_end.open = False
        page.update()

    def handle_dismiss(e):
        e.control.open = False
        page.update()

    date_picker_start = ft.DatePicker(
        on_change=handle_start_change,
        on_dismiss=handle_dismiss,
        first_date=datetime.datetime(2020, 1, 1),
        last_date=datetime.datetime(2030, 12, 31),
    )
    
    date_picker_end = ft.DatePicker(
        on_change=handle_end_change,
        on_dismiss=handle_dismiss,
        first_date=datetime.datetime(2020, 1, 1),
        last_date=datetime.datetime(2030, 12, 31),
    )

    page.overlay.append(date_picker_start)
    page.overlay.append(date_picker_end)

    def open_start_picker(e):
        date_picker_start.open = True
        page.update()

    def open_end_picker(e):
        date_picker_end.open = True
        page.update()

    tf_start.suffix_icon = ft.Icons.CALENDAR_MONTH
    tf_start.on_click = open_start_picker
    tf_end.suffix_icon = ft.Icons.CALENDAR_MONTH
    tf_end.on_click = open_end_picker

    table_reports = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Tipo de reporte")), 
            ft.DataColumn(label=ft.Text("Fecha de creación")), 
            ft.DataColumn(label=ft.Text("Periodo")),
            ft.DataColumn(label=ft.Text("Acciones"))
        ],
        rows=[],
        expand=True
    )

    search_bar = ft.TextField(
        hint_text="Buscar reporte...", 
        prefix_icon=ft.Icons.SEARCH, 
        bgcolor=SURFACE_COLOR,
        on_change=lambda _: load_reports()
    )

    # --- Lógica de Negocio ---

    def load_reports():
        search_term = search_bar.value.lower() if search_bar.value else ""
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM reports ORDER BY created_at DESC"
        cursor.execute(query)
        reports = cursor.fetchall()
        
        table_reports.rows.clear()
        for r in reports:
            if search_term and search_term not in r["type"].lower():
                continue
                
            table_reports.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(r["type"])),
                    ft.DataCell(ft.Text(r["created_at"][:10])),
                    ft.DataCell(ft.Text(f"{r['start_date']} / {r['end_date']}")),
                    ft.DataCell(ft.Row([
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE, 
                            icon_color=DANGER_COLOR,
                            on_click=lambda _, rid=r["id"]: delete_report(rid)
                        ),
                        ft.IconButton(
                            ft.Icons.PICTURE_AS_PDF, 
                            icon_color=SECONDARY_COLOR,
                            on_click=lambda _, rid=r["id"]: export_report(rid)
                        )
                    ]))
                ])
            )
        conn.close()
        page.update()

    # Dropdown de Tipos de Reportes
    dd_report_type = ft.Dropdown(
        label="Tipo de Reporte",
        options=[
            ft.dropdown.Option("Ventas Generales"),
            ft.dropdown.Option("Ventas por Cajero"),
            ft.dropdown.Option("Ventas por Cliente"),
            ft.dropdown.Option("Inventario Actual"),
            ft.dropdown.Option("Inventario Bajo Stock"),
            ft.dropdown.Option("Productos Más Vendidos"),
            ft.dropdown.Option("Ganancias por Producto")
        ],
        value="Ventas Generales"
    )

    def generate_report(e):
        start = tf_start.value
        end = tf_end.value
        tipo = dd_report_type.value
        
        if not start or not end:
            show_toast("Por favor, seleccione ambas fechas", DANGER_COLOR)
            return

        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            if tipo == "Ventas Generales":
                cursor.execute("SELECT SUM(total) as total_ventas, COUNT(*) as cant_ventas FROM sales WHERE datetime(date, 'localtime') BETWEEN ? AND ?", (start + " 00:00:00", end + " 23:59:59"))
                res = cursor.fetchone()
                total = res["total_ventas"] if res["total_ventas"] else 0
                cant = res["cant_ventas"] if res else 0
                if cant == 0:
                    conn.close()
                    show_toast("No hay ventas registradas en las fechas seleccionadas", WARNING_COLOR)
                    return
                summary = f"Ventas Totales: ${total:,.2f} | Cantidad: {cant}"
            
            elif tipo == "Ventas por Cajero":
                cursor.execute('''
                    SELECT u.fullname, SUM(s.total) as total
                    FROM sales s JOIN users u ON s.user_id = u.id
                    WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? GROUP BY u.id ORDER BY total DESC LIMIT 1
                ''', (start + " 00:00:00", end + " 23:59:59"))
                res = cursor.fetchone()
                if not res:
                    conn.close()
                    show_toast("No hay ventas en estas fechas", WARNING_COLOR)
                    return
                summary = f"Mejor Cajero: {res['fullname']} (${res['total']:,.2f})"

            elif tipo == "Ventas por Cliente":
                cursor.execute('''
                    SELECT c.fullname, SUM(s.total) as total
                    FROM sales s JOIN clients c ON s.client_id = c.id
                    WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? GROUP BY c.id ORDER BY total DESC LIMIT 1
                ''', (start + " 00:00:00", end + " 23:59:59"))
                res = cursor.fetchone()
                if not res:
                    conn.close()
                    show_toast("No hay ventas a clientes registrados en estas fechas", WARNING_COLOR)
                    return
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
                    conn.close()
                    show_toast("No hay productos vendidos en este periodo", WARNING_COLOR)
                    return
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
            
            # Guardar el reporte
            cursor.execute('''
                INSERT INTO reports (type, start_date, end_date, summary)
                VALUES (?, ?, ?, ?)
            ''', (tipo, start, end, summary))
            
            conn.commit()
            show_toast(f"Reporte de {tipo} generado con éxito", SUCCESS_COLOR)
        except Exception as ex:
            show_toast(f"Error al generar reporte: {ex}", DANGER_COLOR)
        finally:
            conn.close()
            
        load_reports()

    def delete_report(report_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        conn.commit()
        conn.close()
        load_reports()
        show_toast("Reporte eliminado", WARNING_COLOR)

    def export_report(report_id):
        import os
        from fpdf import FPDF
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
        report = cursor.fetchone()
        
        if not report:
            show_toast("Reporte no encontrado", DANGER_COLOR)
            conn.close()
            return
            
        tipo = report["type"]
        st = report["start_date"] + " 00:00:00"
        ed = report["end_date"] + " 23:59:59"
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 16)
        pdf.cell(0, 10, text=f"Reporte: {tipo}", new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.set_font("helvetica", size=12)
        pdf.cell(0, 10, text=f"Periodo: {report['start_date']} al {report['end_date']}", new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.cell(0, 10, text=f"Resumen: {report['summary']}", new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.ln(10)
        
        if tipo == "Ventas Generales":
            cursor.execute('''
                SELECT s.id, datetime(s.date, 'localtime') as local_date, s.total, s.payment_method, u.fullname as cajero, c.fullname as cliente
                FROM sales s 
                LEFT JOIN users u ON s.user_id = u.id 
                LEFT JOIN clients c ON s.client_id = c.id
                WHERE datetime(s.date, 'localtime') BETWEEN ? AND ?
            ''', (st, ed))
            sales = cursor.fetchall()
            
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
            cursor.execute('''
                SELECT u.fullname, COUNT(s.id) as cant, SUM(s.total) as total
                FROM sales s JOIN users u ON s.user_id = u.id
                WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? GROUP BY u.id ORDER BY total DESC
            ''', (st, ed))
            rows = cursor.fetchall()
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
            cursor.execute('''
                SELECT c.fullname, c.doc_num, COUNT(s.id) as cant, SUM(s.total) as total
                FROM sales s JOIN clients c ON s.client_id = c.id
                WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? GROUP BY c.id ORDER BY total DESC
            ''', (st, ed))
            rows = cursor.fetchall()
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
            cursor.execute("SELECT name, stock, stock_min, price_buy, price_sell FROM products WHERE status = 1")
            rows = cursor.fetchall()
            if rows:
                pdf.set_font("helvetica", 'B', 10)
                pdf.cell(80, 10, 'Producto', border=1)
                pdf.cell(20, 10, 'Stock', border=1)
                pdf.cell(20, 10, 'Min', border=1)
                pdf.cell(30, 10, 'P. Compra', border=1)
                pdf.cell(30, 10, 'P. Venta', border=1, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", size=9)
                for r in rows:
                    pdf.cell(80, 8, str(r['name'])[:35], border=1)
                    pdf.cell(20, 8, str(r['stock']), border=1)
                    pdf.cell(20, 8, str(r['stock_min']), border=1)
                    pdf.cell(30, 8, f"${r['price_buy']:.2f}", border=1)
                    pdf.cell(30, 8, f"${r['price_sell']:.2f}", border=1, new_x="LMARGIN", new_y="NEXT")

        elif tipo == "Inventario Bajo Stock":
            cursor.execute("SELECT name, stock, stock_min FROM products WHERE stock <= stock_min AND status = 1")
            rows = cursor.fetchall()
            if rows:
                pdf.set_font("helvetica", 'B', 12)
                pdf.cell(100, 10, 'Producto', border=1)
                pdf.cell(40, 10, 'Stock Actual', border=1)
                pdf.cell(40, 10, 'Stock Mínimo', border=1, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", size=10)
                for r in rows:
                    pdf.cell(100, 8, str(r['name'])[:40], border=1)
                    pdf.cell(40, 8, str(r['stock']), border=1)
                    pdf.cell(40, 8, str(r['stock_min']), border=1, new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.cell(0, 10, text="No hay productos con bajo stock.", new_x="LMARGIN", new_y="NEXT", align='C')

        elif tipo == "Productos Más Vendidos":
            cursor.execute('''
                SELECT p.name, SUM(sd.quantity) as qty, SUM(sd.quantity * sd.price) as total
                FROM sale_details sd JOIN products p ON sd.product_id = p.id
                JOIN sales s ON sd.sale_id = s.id
                WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? GROUP BY p.id ORDER BY qty DESC
            ''', (st, ed))
            rows = cursor.fetchall()
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
            cursor.execute('''
                SELECT p.name, SUM(sd.quantity) as qty, 
                       SUM(sd.quantity * p.price_buy) as costo,
                       SUM(sd.quantity * sd.price) as ingreso,
                       SUM(sd.quantity * (sd.price - p.price_buy)) as ganancia
                FROM sale_details sd JOIN products p ON sd.product_id = p.id
                JOIN sales s ON sd.sale_id = s.id
                WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? GROUP BY p.id ORDER BY ganancia DESC
            ''', (st, ed))
            rows = cursor.fetchall()
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

        conn.close()
        
        if not os.path.exists("exportaciones"):
            os.makedirs("exportaciones")
            
        filename = f"exportaciones/Reporte_{report['start_date']}_{report['end_date']}_{report_id}.pdf"
        try:
            pdf.output(filename)
            show_toast(f"Reporte PDF guardado en la carpeta 'exportaciones'", SUCCESS_COLOR)
        except Exception as e:
            show_toast(f"Error al exportar: {str(e)}", DANGER_COLOR)

    def show_toast(text, color):
        snack = ft.SnackBar(ft.Text(text), bgcolor=color)
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def reset_fields(e):
        tf_start.value = ""
        tf_end.value = ""
        dd_report_type.value = "Ventas Generales"
        page.update()

    # --- UI Panels ---

    manual_panel = ft.Container(
        bgcolor=SURFACE_COLOR, padding=20, border_radius=10,
        content=ft.Column(
            controls=[
                ft.Text("Generar manualmente reportes", weight=ft.FontWeight.BOLD, size=16),
                dd_report_type,
                ft.Row([tf_start, tf_end], spacing=10),
                ft.Row([
                    ft.OutlinedButton("Restablecer", on_click=reset_fields),
                    ft.Button("Generar Reporte", bgcolor=PRIMARY_COLOR, color="white", on_click=generate_report)
                ], alignment=ft.MainAxisAlignment.END, spacing=10)
            ],
            spacing=20,
            alignment=ft.Alignment.TOP_CENTER
        )
    )

    # Panel de Configuración (Placeholder para la UI premium)
    # !! Esto ya no es necesario, por ahora, lo dejaré comentado. !!
    # config_panel = ft.Container(
    #     bgcolor=SURFACE_COLOR, padding=20, border_radius=10,
    #     content=ft.Column(
    #         controls=[
    #             ft.Text("Configuración de Reportes Automáticos", weight=ft.FontWeight.BOLD, size=16),
    #             ft.Switch(label="Envío diario por correo", value=False, active_color=PRIMARY_COLOR),
    #             ft.Switch(label="Respaldo en la nube mensual", value=True, active_color=PRIMARY_COLOR),
    #             ft.Text("Esta configuración se aplicará a todos los reportes futuros.", size=12, color=TEXT_SECONDARY, italic=True)
    #         ],
    #         spacing=15
    #     )
    # )

    # Inicializar datos
    load_reports()

    # --- Main Layout ---
    return ft.Container(
        expand=True, padding=20, bgcolor=BACKGROUND_COLOR,
        content=ft.Row([
            ft.Column([manual_panel], expand=4, spacing=20),
            ft.VerticalDivider(width=1, color=DIVIDER_COLOR),
            ft.Column([
                ft.Text("Historial de Reportes", size=24, weight=ft.FontWeight.BOLD),
                search_bar,
                ft.Container(
                    content=ft.Column([table_reports], scroll=ft.ScrollMode.AUTO),
                    bgcolor=SURFACE_COLOR, 
                    border_radius=10, 
                    padding=10, 
                    expand=True, 
                    alignment=ft.Alignment.TOP_CENTER
                )
            ], expand=6)
        ], spacing=20)
    )

