"""
Petrol Buddy – Automated Database Setup & Seeder Script
Initializes MySQL schema and hashes all demo account passwords with Werkzeug security.
Usage:
    python setup_db.py
"""

import os
import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "petrol_buddy")

def run_setup():
    print("=" * 60)
    print("  🚀 Petrol Buddy – MySQL Database Initializer")
    print(f"  Target: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    print("=" * 60)

    try:
        # 1. Connect without database first
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = conn.cursor()
        print("✅ Connected to MySQL server successfully.")

        # 2. Read petrol_buddy.sql
        sql_path = os.path.join(os.path.dirname(__file__), "petrol_buddy.sql")
        if not os.path.exists(sql_path):
            raise FileNotFoundError(f"Could not find {sql_path}")

        with open(sql_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # 3. Execute all SQL statements
        # Split on semicolon but handle comments
        statements = []
        delimiter = ";"
        current = []
        for line in sql_content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("--") or stripped.startswith("/*"):
                continue
            current.append(line)
            if stripped.endswith(";"):
                statements.append("\n".join(current))
                current = []

        print(f"📦 Executing schema & initial seeds ({len(statements)} statements)...")
        for stmt in statements:
            try:
                cursor.execute(stmt)
            except mysql.connector.Error as err:
                # Ignore duplicate key on re-run
                if err.errno not in (1061, 1062, 1050):
                    print(f"   Notice: {err.msg}")

        conn.commit()
        print("✅ Database schema and seed data inserted successfully.")

        # 4. Now generate real Werkzeug hashes for the demo accounts
        cursor.execute(f"USE `{DB_NAME}`")
        
        demo_accounts = [
            ("admin@petrolbuddy.com",    "Admin@123"),
            ("customer@petrolbuddy.com", "Customer@123"),
            ("rahul.sharma@example.com", "Customer@123"),
            ("delivery@petrolbuddy.com", "Delivery@123"),
            ("suresh.kumar@example.com", "Delivery@123"),
        ]

        print("🔐 Upgrading demo accounts with Werkzeug pbkdf2 password hashes...")
        for email, plain_pw in demo_accounts:
            hashed = generate_password_hash(plain_pw)
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed, email))

        conn.commit()
        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("  🎉 Setup Complete! You can now start the application:")
        print("     python app.py")
        print("=" * 60)
        print("\n🔑 Demo Login Credentials:")
        print("   🛡️ Admin:    admin@petrolbuddy.com    | Admin@123")
        print("   👤 Customer: customer@petrolbuddy.com | Customer@123")
        print("   🚚 Delivery: delivery@petrolbuddy.com | Delivery@123\n")

    except mysql.connector.Error as err:
        print(f"\n❌ MySQL Error: {err}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Verify MySQL is running (e.g. in XAMPP or Windows Services).")
        print("   2. Check connection settings in your .env file.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    run_setup()
