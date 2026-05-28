from models.client import Client

class ClientesController:
    def __init__(self, view):
        self.view = view

    def get_clients(self, search_term=None):
        return Client.get_all(search_term)

    def register_client(self, fullname, doc_type, doc_num, phone, email, address):
        if not fullname or not doc_num:
            return False, "Nombre y número de documento son obligatorios"
        
        client_id = Client.create(fullname, doc_type, doc_num, phone, email, address)
        if client_id:
            return True, "Cliente registrado con éxito"
        return False, "Error al registrar cliente"

    def update_client(self, client_id, fullname, doc_type, doc_num, phone, email, address):
        if not fullname or not doc_num:
            return False, "Nombre y número de documento son obligatorios"
            
        success = Client.update(client_id, fullname, doc_type, doc_num, phone, email, address)
        if success:
            return True, "Datos del cliente actualizados"
        return False, "Error al actualizar cliente"

    def delete_client(self, client_id):
        success = Client.delete(client_id)
        if success:
            return True, "Cliente eliminado"
        return False, "Error al eliminar cliente"
