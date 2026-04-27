import database

def register_user(username, password, role):
    conn = database.get_connection()
    cursor = conn.cursor()
    try:
        # Everyone starts as pending. 
        # Admins will approve/revoke later.
        status = 'pending'
        cursor.execute(
            "INSERT INTO users (username, password, role, status) VALUES (?, ?, ?, ?)",
            (username, password, role, status)
        )
        user_id = cursor.lastrowid 
        conn.commit()
        return user_id 
    except Exception as e:
        # This is where the UNIQUE constraint error is caught during Registration
        print(f"Registration Error: {e}")
        return None
    finally:
        conn.close()

def login_user(username, password):
    # 1. SECRET ADMIN BYPASS
    # Changed to your specific admin password to avoid conflict with test users
    if username == "admin" and password == "LocalFixAdmin2026":
        return {
            "id": 0, 
            "username": "System Admin", 
            "role": "admin", 
            "status": "approved",
            "rejection_reason": None
        }

    # 2. STANDARD USER LOGIN
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # We select all columns including 'rejection_reason'
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?", 
        (username, password)
    )
    user = cursor.fetchone()
    conn.close()
    
    # Note: cursor.fetchone() returns a Row object. 
    # In app.py we convert this to a dict.
    return user