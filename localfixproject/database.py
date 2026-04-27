import sqlite3

def get_connection():
    # This creates/connects to your 'backpack' database file
    conn = sqlite3.connect("localfix.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row 
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. USERS TABLE: Stores everyone (Admin, Tech, User)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT UNIQUE, 
            password TEXT, 
            role TEXT, 
            status TEXT DEFAULT "pending"
        )
    ''')
    
    # 2. TECHNICIANS TABLE: Stores the professional details (Matching your screenshots)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS technicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INTEGER, 
            name TEXT, 
            phone TEXT, 
            service_type TEXT, 
            location TEXT, 
            bio TEXT, 
            rating REAL DEFAULT 0.0,
            years_exp INTEGER DEFAULT 0,
            hourly_rate REAL DEFAULT 0.0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 3. SERVICE REQUESTS TABLE: When a user clicks "Request Service"
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INTEGER, 
            tech_id INTEGER, 
            status TEXT DEFAULT "requested", 
            request_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 4. MESSAGES TABLE: For the chat-style messaging
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            sender_id INTEGER, 
            receiver_id INTEGER, 
            content TEXT, 
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 5. REVIEWS TABLE: For the gold stars and user feedback
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INTEGER, 
            tech_id INTEGER, 
            rating INTEGER, 
            comment TEXT
        )
    ''')

    # Inside your database setup function
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tech_id INTEGER,
        user_id INTEGER,
        rating INTEGER,
        comment TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tech_id) REFERENCES technicians (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')
    
    conn.commit()
    conn.close()

# Start the database tables as soon as this file is touched
create_tables()