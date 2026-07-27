# save this as migrate.py
import sqlite3

DB_PATH = "clinic.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    
    # Add columns to prescriptions
    try:
        conn.execute("ALTER TABLE prescriptions ADD COLUMN medical_history_id INTEGER")
        print("✅ Added medical_history_id to prescriptions")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("→ Column already exists in prescriptions")
        else:
            print(f"⚠ Error: {e}")
    
    # Add columns to lab_tests
    try:
        conn.execute("ALTER TABLE lab_tests ADD COLUMN medical_history_id INTEGER")
        print("✅ Added medical_history_id to lab_tests")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("→ Column already exists in lab_tests")
        else:
            print(f"⚠ Error: {e}")
    
    conn.commit()
    conn.close()
    print("✅ Migration complete!")

if __name__ == "__main__":
    migrate()