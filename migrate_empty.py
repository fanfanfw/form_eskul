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

    conn.commit()
    cursor.close()
    conn.close()
    print("Empty migration completed")


if __name__ == "__main__":
    main()
