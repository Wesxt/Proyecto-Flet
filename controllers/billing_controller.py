from models.client import Client
from models.user import User
from models.sale import Sale
from models.audit import AuditEvent

class BillingController:
    def __init__(self, view):
        self.view = view

    def get_all_clients(self):
        return Client.get_all()

    def process_billing(self, username, client_fullname, doc_type, doc_num, payment_method_val, register_client_flag, total, cart_items):
        client_id = None
        if client_fullname:
            existing_client = Client.get_by_doc(doc_num, doc_type)
            if existing_client:
                client_id = existing_client.id
            elif register_client_flag:
                client_id = Client.create(client_fullname, doc_type, doc_num)

        user = User.get_by_username(username)
        user_id = user.id if user else None
        
        if payment_method_val.lower().startswith("pago mixto"):
            metodo = payment_method_val
        else:
            metodo = payment_method_val.capitalize()
        
        # Guardamos la venta en base de datos
        sale_id = Sale.create_sale(client_id, user_id, total, metodo, cart_items)
        
        if sale_id:
            # Registrar auditoría de la venta
            # Agrupar productos para contar unidades
            product_quantities = {}
            for item in cart_items:
                name = item['name']
                product_quantities[name] = product_quantities.get(name, 0) + 1
            
            user_role = user.role if user else "Cajero"
            client_name = client_fullname if client_fullname else "Consumidor Final"
            
            for name, qty in product_quantities.items():
                AuditEvent.log_event("Venta", {
                    "producto": name,
                    "unidades": str(qty),
                    "usuario": username,
                    "rol": user_role,
                    "cliente": client_name,
                    "metodo_pago": metodo
                })
                
        return sale_id
