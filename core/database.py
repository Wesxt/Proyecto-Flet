import sqlite3
import os
from core.security import hash_password

DB_PATH = "sistema_ventas.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        email TEXT,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        salary REAL DEFAULT 0,
        status INTEGER DEFAULT 1,
        last_access TIMESTAMP,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Intento de agregar la columna 'salary' por si la tabla ya existe
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN salary REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # La columna ya existe
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_access TIMESTAMP")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    except sqlite3.OperationalError:
        pass
    
    # Create Products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price_buy REAL,
        price_sell REAL NOT NULL,
        stock REAL DEFAULT 0,
        stock_min REAL DEFAULT 0,
        category TEXT,
        in_limit INTEGER DEFAULT 10,
        out_limit INTEGER DEFAULT 10,
        adj_limit INTEGER DEFAULT 10,
        status INTEGER DEFAULT 1,
        image TEXT,
        codigo_producto TEXT
    )
    ''')
    
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN codigo_producto TEXT")
    except sqlite3.OperationalError:
        pass
    
    # Create Clients table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT NOT NULL,
        doc_type TEXT,
        doc_num TEXT,
        email TEXT,
        phone TEXT,
        address TEXT,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    try:
        cursor.execute("ALTER TABLE clients ADD COLUMN fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    except sqlite3.OperationalError:
        pass
    
    # Create Sales table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        user_id INTEGER,
        total REAL NOT NULL,
        payment_method TEXT DEFAULT 'Efectivo',
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status INTEGER DEFAULT 1,
        FOREIGN KEY (client_id) REFERENCES clients (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Intento de agregar la columna payment_method por si la tabla ya existe
    try:
        cursor.execute("ALTER TABLE sales ADD COLUMN payment_method TEXT DEFAULT 'Efectivo'")
    except sqlite3.OperationalError:
        pass  # La columna ya existe
        
    try:
        cursor.execute("ALTER TABLE sales ADD COLUMN status INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass
    
    # Create Sale Details table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sale_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER,
        product_id INTEGER,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (sale_id) REFERENCES sales (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')

    # Create Reports table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        start_date TEXT,
        end_date TEXT,
        summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create Cash Registers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cash_registers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        opening_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        closing_time TIMESTAMP,
        initial_amount REAL NOT NULL,
        expected_amount REAL,
        actual_amount REAL,
        cash_sales REAL DEFAULT 0,
        card_sales REAL DEFAULT 0,
        transfer_sales REAL DEFAULT 0,
        difference REAL,
        status INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    try:
        cursor.execute("ALTER TABLE cash_registers ADD COLUMN transfer_sales REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    # Create Audit Logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        details TEXT NOT NULL
    )
    ''')
    
    # Insert default users if not exists (with hashed passwords)
    users_to_create = [
        ('Administrador Principal', 'admin', 'admin@empresa.com', 'admin123', 'Administrador', 1),
        ('Supervisor de Turno', 'supervisor', 'super@empresa.com', 'super123', 'Supervisor', 1),
        ('Cajero Principal', 'cajero', 'cajero@empresa.com', 'cajero123', 'Cajero', 1)
    ]
    
    for fullname, username, email, password, role, status in users_to_create:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            hashed_pwd = hash_password(password)
            cursor.execute('''
            INSERT INTO users (fullname, username, email, password, role, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (fullname, username, email, hashed_pwd, role, status))
            
    # Migración: cifrar contraseñas existentes en texto plano
    cursor.execute("SELECT id, password FROM users")
    for row in cursor.fetchall():
        current_pwd = row["password"]
        # Si la contraseña no tiene longitud 64 (SHA-256 hash), asumimos que es texto plano y la ciframos
        if len(current_pwd) != 64:
            new_hashed = hash_password(current_pwd)
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_hashed, row["id"]))
        
    # Insert some sample products if table is empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('Arroz 1kg', 'Arroz blanco de grano largo', 1.00, 1.50, 100, 10, 'Abarrotes', 10, 10, 10, 1, 'PROD-001'),
            ('Aceite 1L', 'Aceite vegetal refinado', 2.50, 3.20, 50, 5, 'Aceites', 10, 10, 10, 1, 'PROD-002'),
            ('Leche 1L', 'Leche entera pasteurizada', 0.80, 1.10, 80, 10, 'Lácteos', 10, 10, 10, 1, 'PROD-003'),
            ('Pan Molde', 'Pan de molde blanco 500g', 1.40, 2.00, 30, 5, 'Panadería', 10, 10, 10, 1, 'PROD-004')
        ]
        cursor.executemany('INSERT INTO products (name, description, price_buy, price_sell, stock, stock_min, category, in_limit, out_limit, adj_limit, status, codigo_producto) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', sample_products)

    # Migración: asignar códigos de producto secuenciales a productos existentes que no tengan código
    cursor.execute("SELECT id, codigo_producto FROM products")
    prod_rows = cursor.fetchall()
    for idx, row in enumerate(prod_rows):
        if not row["codigo_producto"]:
            generated_code = f"PROD-{idx+1:03d}"
            cursor.execute("UPDATE products SET codigo_producto = ? WHERE id = ?", (generated_code, row["id"]))

    # Seed default client "Consumidor Final" if not exists
    cursor.execute("SELECT * FROM clients WHERE doc_num = '9999999999'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO clients (fullname, doc_type, doc_num, phone, email, address)
            VALUES ('Consumidor Final', 'Cédula de ciudadanía', '9999999999', '', '', '')
        ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
