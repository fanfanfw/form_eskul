#!/usr/bin/env python3
"""
Script untuk test koneksi database
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration sesuai dengan Anda
DB_CONFIG = {
    "host": "localhost",
    "database": "db_form_eskul",
    "user": "fanfan",
    "password": "cenanun",
    "port": 5432
}

def test_connection():
    """Test koneksi ke database"""
    print("🔍 Testing database connection...")
    print(f"Host: {DB_CONFIG['host']}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"User: {DB_CONFIG['user']}")
    print(f"Port: {DB_CONFIG['port']}")
    print("-" * 40)
    
    try:
        # Test koneksi
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        print("✅ Koneksi database berhasil!")
        
        cursor = conn.cursor()
        
        # Test query sederhana
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"PostgreSQL Version: {version[0]}")
        
        # Cek tabel yang ada
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n📋 Daftar tabel yang ada:")
        if tables:
            for table in tables:
                print(f"  - {table['table_name']}")
        else:
            print("  Tidak ada tabel")
        
        # Jika ada tabel eskul, tampilkan isinya
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'eskul'
            )
        """)
        
        eskul_exists = cursor.fetchone()[0]
        
        if eskul_exists:
            cursor.execute("SELECT COUNT(*) FROM eskul")
            count = cursor.fetchone()[0]
            print(f"\n🏆 Tabel eskul: {count} records")
            
            if count > 0:
                cursor.execute("SELECT * FROM eskul LIMIT 5")
                eskul_sample = cursor.fetchall()
                print("Sample data eskul:")
                for eskul in eskul_sample:
                    print(f"  {eskul['id']}: {eskul['nama_eskul']}")
        
        # Jika ada tabel siswa, tampilkan info
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'siswa'
            )
        """)
        
        siswa_exists = cursor.fetchone()[0]
        
        if siswa_exists:
            cursor.execute("SELECT COUNT(*) FROM siswa")
            count = cursor.fetchone()[0]
            print(f"\n👥 Tabel siswa: {count} records")
            
            if count > 0:
                cursor.execute("SELECT DISTINCT kelas FROM siswa ORDER BY kelas")
                kelas_list = cursor.fetchall()
                print("Daftar kelas:")
                for kelas in kelas_list:
                    print(f"  - {kelas['kelas']}")
        
        conn.close()
        print("\n🎉 Test koneksi selesai!")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error koneksi database: {e}")
        print("\n💡 Tips troubleshooting:")
        print("1. Pastikan PostgreSQL service berjalan")
        print("2. Cek username dan password")
        print("3. Pastikan database 'db_form_eskul' sudah dibuat")
        print("4. Cek permission user 'fanfan'")
        return False
    except Exception as e:
        print(f"❌ Error umum: {e}")
        return False

if __name__ == "__main__":
    test_connection()
