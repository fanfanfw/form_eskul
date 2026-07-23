#!/usr/bin/env python3
"""
Script untuk setup database dan import data siswa dari CSV
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import sys
import os

# Database configuration - GANTI SESUAI KONFIGURASI ANDA
DB_CONFIG = {
    "host": "localhost",
    "database": "db_form_eskul",  # Ganti dengan nama database Anda
    "user": "fanfan",             # Ganti dengan username database Anda
    "password": "cenanun"         # Ganti dengan password database Anda
}

def create_database_and_tables():
    """Membuat database dan tabel yang diperlukan"""
    
    # Koneksi ke PostgreSQL untuk membuat database
    try:
        # Koneksi ke database postgres untuk membuat database baru
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            database="postgres",  # Connect to default postgres database
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Cek apakah database sudah ada
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_CONFIG['database']}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print(f"✅ Database '{DB_CONFIG['database']}' berhasil dibuat")
        else:
            print(f"✅ Database '{DB_CONFIG['database']}' sudah ada")
        
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error membuat database: {e}")
        return False
    
    # Koneksi ke database yang baru dibuat untuk membuat tabel
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Buat tabel eskul
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eskul (
                id SERIAL PRIMARY KEY,
                nama_eskul VARCHAR(50) NOT NULL,
                minimal_kelas INTEGER NOT NULL DEFAULT 1 CHECK (minimal_kelas BETWEEN 1 AND 6)
            )
        """)
        
        cursor.execute("SELECT 1 FROM pg_attribute WHERE attrelid='eskul'::regclass AND attname='minimal_kelas' AND NOT attisdropped")
        new_column = not cursor.fetchone()
        cursor.execute("ALTER TABLE eskul ADD COLUMN IF NOT EXISTS minimal_kelas INTEGER NOT NULL DEFAULT 1")
        if new_column:
            cursor.execute("UPDATE eskul SET minimal_kelas=3 WHERE LOWER(nama_eskul) IN ('pencak silat','futsal','angklung')")
        cursor.execute("SELECT 1 FROM pg_constraint WHERE conname='eskul_minimal_kelas_check' AND conrelid='eskul'::regclass")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE eskul ADD CONSTRAINT eskul_minimal_kelas_check CHECK (minimal_kelas BETWEEN 1 AND 6)")

        # Buat tabel siswa
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS siswa (
                id SERIAL PRIMARY KEY,
                nis VARCHAR(20) NOT NULL,
                nisn VARCHAR(20) NOT NULL,
                nama VARCHAR(255) NOT NULL,
                jeniskelamin VARCHAR(1) NOT NULL,
                kelas VARCHAR(15) NOT NULL,
                eskul INTEGER,
                CONSTRAINT fk_eskul
                    FOREIGN KEY(eskul)
                    REFERENCES eskul(id)
                    ON DELETE SET NULL
            )
        """)
        
        conn.commit()
        print("✅ Tabel berhasil dibuat")
        
        return conn
        
    except psycopg2.Error as e:
        print(f"❌ Error membuat tabel: {e}")
        return None

def insert_sample_eskul(conn):
    """Insert data eskul contoh"""
    try:
        cursor = conn.cursor()
        
        # Cek apakah sudah ada data eskul
        cursor.execute("SELECT COUNT(*) FROM eskul")
        count = cursor.fetchone()[0]
        
        if count == 0:
            eskul_data = [
                "Pramuka",
                "PMR (Palang Merah Remaja)",
                "Paskibra",
                "Rohis (Rohani Islam)",
                "Basket",
                "Sepak Bola",
                "Voli",
                "Badminton",
                "Futsal",
                "Taekwondo",
                "Karate",
                "Silat",
                "Tenis Meja",
                "Catur",
                "Band/Musik",
                "Tari",
                "Teater",
                "English Club",
                "Jurnalistik",
                "Fotografi",
                "Komputer/IT",
                "Sains Club",
                "Matematika",
                "Debat",
                "Mading (Majalah Dinding)"
            ]
            
            for eskul in eskul_data:
                cursor.execute("INSERT INTO eskul (nama_eskul) VALUES (%s)", (eskul,))
            
            conn.commit()
            print(f"✅ {len(eskul_data)} data eskul berhasil diinsert")
        else:
            print(f"✅ Data eskul sudah ada ({count} records)")
            
    except psycopg2.Error as e:
        print(f"❌ Error insert eskul: {e}")

def import_students_from_csv(conn, csv_file):
    """Import data siswa dari file CSV"""
    try:
        # Baca CSV file
        if not os.path.exists(csv_file):
            print(f"❌ File {csv_file} tidak ditemukan")
            return False
        
        df = pd.read_csv(csv_file)
        print(f"📁 Membaca {len(df)} records dari {csv_file}")
        
        cursor = conn.cursor()
        
        # Cek apakah sudah ada data siswa
        cursor.execute("SELECT COUNT(*) FROM siswa")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"⚠️  Data siswa sudah ada ({existing_count} records)")
            response = input("Hapus data lama dan import ulang? (y/n): ")
            if response.lower() == 'y':
                cursor.execute("DELETE FROM siswa")
                print("🗑️  Data siswa lama telah dihapus")
            else:
                print("❌ Import dibatalkan")
                return False
        
        # Insert data siswa
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO siswa (nis, nisn, nama, jeniskelamin, kelas)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    str(row['NIS']),
                    str(row['NISN']),
                    row['Nama'],
                    row['JenisKelamin'],
                    row['Kelas']
                ))
                success_count += 1
                
            except psycopg2.Error as e:
                print(f"❌ Error inserting row {index}: {e}")
                error_count += 1
                continue
        
        conn.commit()
        print(f"✅ {success_count} siswa berhasil diimport")
        if error_count > 0:
            print(f"⚠️  {error_count} siswa gagal diimport")
        
        return True
        
    except Exception as e:
        print(f"❌ Error import CSV: {e}")
        return False

def verify_data(conn):
    """Verifikasi data yang telah diimport"""
    try:
        cursor = conn.cursor()
        
        # Count eskul
        cursor.execute("SELECT COUNT(*) FROM eskul")
        eskul_count = cursor.fetchone()[0]
        
        # Count siswa
        cursor.execute("SELECT COUNT(*) FROM siswa")
        siswa_count = cursor.fetchone()[0]
        
        # Count kelas
        cursor.execute("SELECT COUNT(DISTINCT kelas) FROM siswa")
        kelas_count = cursor.fetchone()[0]
        
        # Sample data
        cursor.execute("SELECT nama_eskul FROM eskul LIMIT 5")
        sample_eskul = cursor.fetchall()
        
        cursor.execute("SELECT nama, kelas FROM siswa LIMIT 5")
        sample_siswa = cursor.fetchall()
        
        print("\n" + "="*50)
        print("📊 RINGKASAN DATA")
        print("="*50)
        print(f"Total Ekstrakurikuler: {eskul_count}")
        print(f"Total Siswa: {siswa_count}")
        print(f"Total Kelas: {kelas_count}")
        
        print(f"\nContoh Eskul:")
        for eskul in sample_eskul:
            print(f"  - {eskul[0]}")
        
        print(f"\nContoh Siswa:")
        for siswa in sample_siswa:
            print(f"  - {siswa[0]} ({siswa[1]})")
        
        print("="*50)
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error verifying data: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Setup Database Form Eskul")
    print("="*40)
    
    # Membuat database dan tabel
    print("1. Membuat database dan tabel...")
    conn = create_database_and_tables()
    if not conn:
        print("❌ Gagal setup database")
        sys.exit(1)
    
    # Insert data eskul
    print("\n2. Menambahkan data ekstrakurikuler...")
    insert_sample_eskul(conn)
    
    # Import data siswa dari CSV
    print("\n3. Import data siswa dari CSV...")
    csv_file = "dataset.csv"
    if import_students_from_csv(conn, csv_file):
        print("✅ Import siswa berhasil")
    else:
        print("❌ Import siswa gagal")
    
    # Verifikasi data
    print("\n4. Verifikasi data...")
    verify_data(conn)
    
    conn.close()
    print("\n🎉 Setup database selesai!")
    print("\nSelanjutnya:")
    print("1. Pastikan konfigurasi database di main.py sesuai")
    print("2. Jalankan aplikasi dengan: python main.py")
    print("3. Buka browser ke: http://localhost:8000")

if __name__ == "__main__":
    # Install pandas jika belum ada
    try:
        import pandas as pd
    except ImportError:
        print("📦 Installing pandas...")
        os.system("pip install pandas")
        import pandas as pd
    
    main()
