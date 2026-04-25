import sqlite3
import os

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
        status INTEGER DEFAULT 1
    )
    ''')
    
    # Intento de agregar la columna 'salary' por si la tabla ya existe
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN salary REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # La columna ya existe
    
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
        status INTEGER DEFAULT 1
    )
    ''')
    
    # Create Clients table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        address TEXT
    )
    ''')
    
    # Create Sales table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        user_id INTEGER,
        total REAL NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (client_id) REFERENCES clients (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
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
    
    # Insert default users if not exists
    users_to_create = [
        ('Administrador Principal', 'admin', 'admin@empresa.com', 'admin123', 'Administrador', 1),
        ('Supervisor de Turno', 'supervisor', 'super@empresa.com', 'super123', 'Supervisor', 1),
        ('Cajero Principal', 'cajero', 'cajero@empresa.com', 'cajero123', 'Cajero', 1)
    ]
    
    for fullname, username, email, password, role, status in users_to_create:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            cursor.execute('''
            INSERT INTO users (fullname, username, email, password, role, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (fullname, username, email, password, role, status))
        
    # Insert some sample products if table is empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('Arroz 1kg', 'Arroz blanco de grano largo', 1.00, 1.50, 100, 10, 'Abarrotes', 1),
            ('Aceite 1L', 'Aceite vegetal refinado', 2.50, 3.20, 50, 5, 'Aceites', 1),
            ('Leche 1L', 'Leche entera pasteurizada', 0.80, 1.10, 80, 10, 'Lácteos', 1),
            ('Pan Molde', 'Pan de molde blanco 500g', 1.40, 2.00, 30, 5, 'Panadería', 1)
        ]
        cursor.executemany('INSERT INTO products (name, description, price_buy, price_sell, stock, stock_min, category, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', sample_products)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
