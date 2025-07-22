#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

# Test database connection and query
DB_CONFIG = {
    "host": "localhost",
    "database": "db_form_eskul",
    "user": "fanfan",
    "password": "cenanun",
    "port": 5432
}

def test_database():
    print("🔍 Testing database connection and data...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        # Simple test - count students with eskul
        cursor.execute("""
            SELECT 
                COUNT(*) as total_siswa,
                COUNT(eskul) as sudah_daftar_eskul,
                COUNT(*) - COUNT(eskul) as belum_daftar
            FROM siswa
        """)
        
        counts = cursor.fetchone()
        print(f"📊 Database Stats:")
        print(f"   Total siswa: {counts['total_siswa']}")
        print(f"   Sudah daftar eskul: {counts['sudah_daftar_eskul']}")
        print(f"   Belum daftar: {counts['belum_daftar']}")
        
        # Show some sample data
        cursor.execute("""
            SELECT s.nama, e.nama_eskul
            FROM siswa s
            LEFT JOIN eskul e ON s.eskul = e.id
            WHERE s.eskul IS NOT NULL
            LIMIT 5
        """)
        
        registered = cursor.fetchall()
        print(f"\n👥 Students with eskul:")
        for student in registered:
            print(f"   - {student['nama']}: {student['nama_eskul']}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_database()
