import hashlib

SALT = "pos_erp_system_salt_colombia_2026_"

def hash_password(password: str) -> str:
    """Hashea una contraseña usando SHA-256 y una sal fija de aplicación."""
    if not password:
        return ""
    salted_password = SALT + password
    return hashlib.sha256(salted_password.encode('utf-8')).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Compara una contraseña en texto plano contra su hash."""
    if not password or not hashed:
        return False
    return hash_password(password) == hashed
