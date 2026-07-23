import os

import psycopg2


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


def main():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eskul (
            id SERIAL PRIMARY KEY,
            nama_eskul VARCHAR(50) NOT NULL,
            minimal_kelas INTEGER NOT NULL DEFAULT 1 CHECK (minimal_kelas BETWEEN 1 AND 6)
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
    cursor.execute("SELECT 1 FROM pg_attribute WHERE attrelid='eskul'::regclass AND attname='minimal_kelas' AND NOT attisdropped")
    new_column = not cursor.fetchone()
    cursor.execute("ALTER TABLE eskul ADD COLUMN IF NOT EXISTS minimal_kelas INTEGER NOT NULL DEFAULT 1")
    if new_column:
        cursor.execute("UPDATE eskul SET minimal_kelas=3 WHERE LOWER(nama_eskul) IN ('pencak silat','futsal','angklung')")
    cursor.execute("SELECT 1 FROM pg_constraint WHERE conname='eskul_minimal_kelas_check' AND conrelid='eskul'::regclass")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE eskul ADD CONSTRAINT eskul_minimal_kelas_check CHECK (minimal_kelas BETWEEN 1 AND 6)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS siswa_nis_unique ON siswa (nis)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS eskul_nama_unique ON eskul (nama_eskul)")

    conn.commit()
    cursor.close()
    conn.close()
    print("Empty migration completed")


if __name__ == "__main__":
    main()
