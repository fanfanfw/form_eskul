import csv
import os
from pathlib import Path

import psycopg2


ESKUL = [
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
    "Mading (Majalah Dinding)",
]


def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_DATABASE", "db_form_eskul"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        port=int(os.getenv("DB_PORT", "5432")),
    )


def migrate(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eskul (
            id SERIAL PRIMARY KEY,
            nama_eskul VARCHAR(50) NOT NULL
        )
    """)

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
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS siswa_nis_unique ON siswa (nis)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS eskul_nama_unique ON eskul (nama_eskul)")


def seed_eskul(cursor):
    for nama_eskul in ESKUL:
        cursor.execute(
            """
            INSERT INTO eskul (nama_eskul)
            SELECT %s
            WHERE NOT EXISTS (SELECT 1 FROM eskul WHERE nama_eskul = %s)
            """,
            (nama_eskul, nama_eskul),
        )


def seed_siswa(cursor):
    path = Path(__file__).with_name("dataset.csv")
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute(
                """
                INSERT INTO siswa (nis, nisn, nama, jeniskelamin, kelas)
                SELECT %s, %s, %s, %s, %s
                WHERE NOT EXISTS (SELECT 1 FROM siswa WHERE nis = %s)
                """,
                (
                    row["NIS"],
                    row["NISN"],
                    row["Nama"],
                    row["JenisKelamin"],
                    row["Kelas"],
                    row["NIS"],
                ),
            )


def main():
    conn = get_connection()
    cursor = conn.cursor()
    migrate(cursor)
    seed_eskul(cursor)
    seed_siswa(cursor)
    conn.commit()
    cursor.close()
    conn.close()
    print("Production migration and seed completed")


if __name__ == "__main__":
    main()
