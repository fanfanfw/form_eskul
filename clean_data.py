#!/usr/bin/env python3
"""
Script untuk membersihkan data null di database
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "database": "db_form_eskul",
    "user": "fanfan",
    "password": "cenanun",
    "port": 5432
}

def clean_null_data():
    """Membersihkan data null di database"""
    print("🧹 Membersihkan data null di database...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        # Cek data sebelum pembersihan
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN nis IS NULL THEN 1 END) as nis_null,
                COUNT(CASE WHEN nisn IS NULL THEN 1 END) as nisn_null,
                COUNT(CASE WHEN nama IS NULL THEN 1 END) as nama_null,
                COUNT(CASE WHEN jeniskelamin IS NULL THEN 1 END) as jk_null,
                COUNT(CASE WHEN kelas IS NULL THEN 1 END) as kelas_null
            FROM siswa
        """)
        
        stats_before = cursor.fetchone()
        print(f"📊 Statistik sebelum pembersihan:")
        print(f"   Total siswa: {stats_before['total']}")
        print(f"   NIS null: {stats_before['nis_null']}")
        print(f"   NISN null: {stats_before['nisn_null']}")
        print(f"   Nama null: {stats_before['nama_null']}")
        print(f"   Jenis Kelamin null: {stats_before['jk_null']}")
        print(f"   Kelas null: {stats_before['kelas_null']}")
        
        # Opsi 1: Update nilai null menjadi string kosong atau nilai default
        print(f"\n🔧 Pilihan pembersihan:")
        print(f"1. Update nilai null menjadi string kosong")
        print(f"2. Hapus record yang memiliki data penting null (nama, kelas)")
        print(f"3. Lihat data null saja")
        print(f"4. Keluar tanpa perubahan")
        
        choice = input("\nPilih opsi (1-4): ")
        
        if choice == "1":
            # Update null values
            updates = 0
            
            # Update NIS null
            cursor.execute("UPDATE siswa SET nis = '' WHERE nis IS NULL")
            updates += cursor.rowcount
            
            # Update NISN null
            cursor.execute("UPDATE siswa SET nisn = '' WHERE nisn IS NULL")
            updates += cursor.rowcount
            
            # Update nama null (jika ada)
            cursor.execute("UPDATE siswa SET nama = 'Nama tidak tersedia' WHERE nama IS NULL OR nama = ''")
            updates += cursor.rowcount
            
            # Update jenis kelamin null
            cursor.execute("UPDATE siswa SET jeniskelamin = 'L' WHERE jeniskelamin IS NULL OR jeniskelamin = ''")
            updates += cursor.rowcount
            
            # Update kelas null
            cursor.execute("UPDATE siswa SET kelas = 'Tidak diketahui' WHERE kelas IS NULL OR kelas = ''")
            updates += cursor.rowcount
            
            conn.commit()
            print(f"✅ Berhasil update {updates} field yang null")
            
        elif choice == "2":
            # Hapus record dengan data penting null
            cursor.execute("DELETE FROM siswa WHERE nama IS NULL OR nama = '' OR kelas IS NULL OR kelas = ''")
            deleted = cursor.rowcount
            conn.commit()
            print(f"🗑️ Berhasil hapus {deleted} record dengan data penting null")
            
        elif choice == "3":
            # Tampilkan data null
            cursor.execute("""
                SELECT id, nis, nisn, nama, jeniskelamin, kelas 
                FROM siswa 
                WHERE nis IS NULL OR nisn IS NULL OR nama IS NULL OR jeniskelamin IS NULL OR kelas IS NULL
                ORDER BY id
                LIMIT 20
            """)
            
            null_records = cursor.fetchall()
            if null_records:
                print(f"\n📋 Data dengan nilai null (maksimal 20 record):")
                print(f"{'ID':<5} {'NIS':<15} {'NISN':<15} {'Nama':<30} {'JK':<3} {'Kelas':<10}")
                print("-" * 80)
                for record in null_records:
                    print(f"{record['id']:<5} {str(record['nis'] or 'NULL'):<15} {str(record['nisn'] or 'NULL'):<15} {str(record['nama'] or 'NULL'):<30} {str(record['jeniskelamin'] or 'NULL'):<3} {str(record['kelas'] or 'NULL'):<10}")
            else:
                print("✅ Tidak ada data dengan nilai null")
                
        else:
            print("❌ Keluar tanpa perubahan")
            
        # Statistik setelah perubahan
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN nis IS NULL OR nis = '' THEN 1 END) as nis_empty,
                COUNT(CASE WHEN nisn IS NULL OR nisn = '' THEN 1 END) as nisn_empty,
                COUNT(CASE WHEN nama IS NULL OR nama = '' THEN 1 END) as nama_empty,
                COUNT(CASE WHEN jeniskelamin IS NULL OR jeniskelamin = '' THEN 1 END) as jk_empty,
                COUNT(CASE WHEN kelas IS NULL OR kelas = '' THEN 1 END) as kelas_empty
            FROM siswa
        """)
        
        stats_after = cursor.fetchone()
        print(f"\n📊 Statistik setelah pembersihan:")
        print(f"   Total siswa: {stats_after['total']}")
        print(f"   NIS kosong: {stats_after['nis_empty']}")
        print(f"   NISN kosong: {stats_after['nisn_empty']}")
        print(f"   Nama kosong: {stats_after['nama_empty']}")
        print(f"   Jenis Kelamin kosong: {stats_after['jk_empty']}")
        print(f"   Kelas kosong: {stats_after['kelas_empty']}")
        
        conn.close()
        print(f"\n🎉 Pembersihan selesai!")
        
    except psycopg2.Error as e:
        print(f"❌ Error database: {e}")
    except Exception as e:
        print(f"❌ Error umum: {e}")

if __name__ == "__main__":
    clean_null_data()
