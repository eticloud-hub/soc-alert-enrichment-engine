import sqlite3
from pathlib import Path

DB_PATH = Path("soc_alert_engine/data/alerts.db")

def init_database():
    """Initialize SQLite database with alerts table"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Create alerts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_ip TEXT NOT NULL,
            destination_ip TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            message TEXT,
            risk_score REAL DEFAULT 0,
            priority TEXT DEFAULT 'Medium',
            enrichment_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✓ Database initialized")

def get_connection():
    """Get SQLite database connection"""
    return sqlite3.connect(str(DB_PATH))

def insert_alert(timestamp, source_ip, destination_ip, alert_type, message):
    """Insert a raw alert into database"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO alerts (timestamp, source_ip, destination_ip, alert_type, message)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, source_ip, destination_ip, alert_type, message))

    conn.commit()
    alert_id = cursor.lastrowid
    conn.close()
    return alert_id

def update_alert_enrichment(alert_id, risk_score, priority, enrichment_data):
    """Update alert with enrichment data and risk score"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE alerts 
        SET risk_score = ?, priority = ?, enrichment_data = ?
        WHERE id = ?
    """, (risk_score, priority, enrichment_data, alert_id))

    conn.commit()
    conn.close()

def get_all_alerts():
    """Retrieve all alerts from database"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM alerts ORDER BY timestamp DESC")
    alerts = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return alerts

def get_alerts_by_priority(priority):
    """Get alerts filtered by priority"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM alerts WHERE priority = ? ORDER BY timestamp DESC",
        (priority,)
    )
    alerts = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return alerts

def clear_database():
    """Clear all alerts from database (for testing)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM alerts")
    conn.commit()
    conn.close()