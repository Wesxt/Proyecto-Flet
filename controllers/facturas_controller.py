from models.sale import Sale

class FacturasController:
    def __init__(self, view):
        self.view = view

    def get_sales(self):
        """Obtiene la lista de todas las facturas/ventas en el sistema."""
        return Sale.get_all_sales_list()

    def get_details(self, sale_id):
        """Obtiene los detalles (ítems, precios y cantidades) de una factura."""
        return Sale.get_sale_details(sale_id)

    def void_invoice(self, sale_id, username):
        """Anula una factura en el sistema, restaurando stock y registrando auditoría."""
        return Sale.void_sale(sale_id, username)
