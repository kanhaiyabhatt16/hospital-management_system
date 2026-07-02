import os
import pymysql
import hashlib
from dotenv import load_dotenv

load_dotenv()

db_config = {
    "host": os.getenv('DB_HOST'),
    "port": int(os.getenv('DB_PORT')),
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD'),
    "database": os.getenv('DB_NAME'),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def run_migrations():
    print("Starting database migration...")
    conn = pymysql.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            # 1. Drop old users table if it exists (to recreate with correct columns/constraints)
            cursor.execute("DROP TABLE IF EXISTS users;")
            
            # Re-create users table with correct schema
            cursor.execute("""
            CREATE TABLE users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                hospital VARCHAR(100) NOT NULL,
                username VARCHAR(100) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('Admin', 'Staff') NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user (hospital, username)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            print("Users table recreated.")

            # Seed default users for hospital 'abc'
            default_users = [
                ('COER Hospital', 'kanhaiyabhatt9528@gmail.com', hash_password('Ka6vkf1@'), 'Admin'),
                ('COER Hospital', 'staff', hash_password('staff'), 'Staff')
            ]
            for hospital, username, p_hash, role in default_users:
                cursor.execute("""
                INSERT IGNORE INTO users (hospital, username, password_hash, role)
                VALUES (%s, %s, %s, %s)
                """, (hospital, username, p_hash, role))
            print("Default users seeded.")

            # 2. Add 'hospital' column to existing tables if not present
            tables = [
                'patient', 'doctor', 'appointment', 'billing', 'medical_record',
                'department', 'staff', 'insurance_provider', 'test_type',
                'patient_test', 'inventory'
            ]
            
            for table in tables:
                # Check if hospital column exists
                cursor.execute(f"SHOW COLUMNS FROM `{table}` LIKE 'hospital'")
                column_exists = cursor.fetchone()
                
                if not column_exists:
                    print(f"Adding 'hospital' column to table '{table}'...")
                    cursor.execute(f"ALTER TABLE `{table}` ADD COLUMN hospital VARCHAR(100) NOT NULL DEFAULT 'abc'")
                else:
                    print(f"Table '{table}' already has 'hospital' column.")

        conn.commit()
        print("Database migration completed successfully!")
    except Exception as e:
        conn.rollback()
        print(f"Database migration failed: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    run_migrations()
