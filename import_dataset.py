import psycopg2
import csv

# Koneksi ke database PostgreSQL
conn = psycopg2.connect(
    dbname="db_form_eskul",   # ganti dengan nama database Anda
    user="fanfan",         # ganti dengan user PostgreSQL Anda
    password="cenanun",      # ganti dengan password PostgreSQL Anda
    host="localhost",         # ganti jika database ada di host lain
    port="5432"               # port default PostgreSQL
)
cur = conn.cursor()

# Buka file CSV
with open('dataset.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Masukkan data ke tabel siswa
        cur.execute("""
            INSERT INTO siswa (nis, nisn, nama, JenisKelamin, kelas, eskul)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            row['NIS'],           # nis
            row['NISN'],          # nisn
            row['Nama'],          # nama
            row['JenisKelamin'],  # JenisKelamin
            row['Kelas'],         # kelas
            None                  # eskul, karena tidak ada di dataset
        ))

# Commit perubahan dan tutup koneksi
conn.commit()
cur.close()
conn.close()