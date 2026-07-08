from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, File, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import io
from typing import List, Dict, Any
import json
import pandas as pd

try:
    from config import *
except ImportError:
    DB_HOST = "localhost"
    DB_DATABASE = "db_form_eskul"
    DB_USER = "postgres"
    DB_PASSWORD = "postgres"
    DB_PORT = 5432
    APP_TITLE = "Form Eskul Siswa"
    APP_DESCRIPTION = "Website untuk mengisi form eskul siswa"

DB_HOST = os.getenv("DB_HOST", DB_HOST)
DB_DATABASE = os.getenv("DB_DATABASE", DB_DATABASE)
DB_USER = os.getenv("DB_USER", DB_USER)
DB_PASSWORD = os.getenv("DB_PASSWORD", DB_PASSWORD)
DB_PORT = int(os.getenv("DB_PORT", DB_PORT))
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(title=APP_TITLE, description=APP_DESCRIPTION)

# Setup templates dan static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database configuration
DB_CONFIG = {
    "host": DB_HOST,
    "database": DB_DATABASE,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "port": DB_PORT
}

def get_db_connection():
    """Membuat koneksi ke database PostgreSQL"""
    try:
        if DATABASE_URL:
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        else:
            conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Halaman utama dengan form"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/kelas")
async def get_kelas():
    """API untuk mendapatkan daftar kelas yang tersedia"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT kelas FROM siswa ORDER BY kelas")
        kelas_list = [row['kelas'] for row in cursor.fetchall()]
        return {"kelas": kelas_list}
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

@app.get("/api/siswa/{kelas}")
async def get_siswa_by_kelas(kelas: str):
    """API untuk mendapatkan daftar siswa berdasarkan kelas"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nis, nisn, nama FROM siswa WHERE kelas = %s ORDER BY nama",
            (kelas,)
        )
        siswa_list = cursor.fetchall()
        return {"siswa": siswa_list}
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

@app.get("/api/eskul")
async def get_eskul():
    """API untuk mendapatkan daftar ekstrakurikuler"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama_eskul FROM eskul ORDER BY nama_eskul")
        eskul_list = cursor.fetchall()
        return {"eskul": eskul_list}
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

def read_students_excel(file_content: bytes):
    df = pd.read_excel(io.BytesIO(file_content), dtype=str).fillna("")
    required_columns = ["NIS", "NISN", "Nama", "JenisKelamin", "Kelas"]
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise HTTPException(status_code=400, detail=f"Kolom wajib tidak ada: {', '.join(missing_columns)}")

    rows = []
    seen = set()
    duplicate_file = []
    for _, row in df.iterrows():
        nis = str(row["NIS"]).strip()
        if not nis:
            continue
        student = {
            "nis": nis,
            "nisn": str(row["NISN"]).strip(),
            "nama": str(row["Nama"]).strip(),
            "jeniskelamin": str(row["JenisKelamin"]).strip().upper(),
            "kelas": str(row["Kelas"]).strip(),
        }
        if nis in seen:
            duplicate_file.append(student)
            continue
        seen.add(nis)
        rows.append(student)
    return rows, duplicate_file

@app.post("/api/students/preview-import")
async def preview_students_import(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Upload file Excel .xlsx")

    rows, duplicate_file = read_students_excel(await file.read())
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = conn.cursor()
        nis_list = [row["nis"] for row in rows]
        existing = set()
        if nis_list:
            cursor.execute("SELECT nis FROM siswa WHERE nis = ANY(%s)", (nis_list,))
            existing = {row["nis"] for row in cursor.fetchall()}
        return {
            "total": len(rows),
            "new_count": len([row for row in rows if row["nis"] not in existing]),
            "duplicate_database_count": len(existing),
            "duplicate_file_count": len(duplicate_file),
            "preview": rows[:20],
            "duplicate_database": sorted(existing)[:20],
            "duplicate_file": duplicate_file[:20],
        }
    finally:
        conn.close()

@app.post("/api/students/import")
async def import_students(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Upload file Excel .xlsx")

    rows, duplicate_file = read_students_excel(await file.read())
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    inserted = 0
    skipped = len(duplicate_file)
    try:
        cursor = conn.cursor()
        for row in rows:
            cursor.execute(
                """
                INSERT INTO siswa (nis, nisn, nama, jeniskelamin, kelas)
                SELECT %s, %s, %s, %s, %s
                WHERE NOT EXISTS (SELECT 1 FROM siswa WHERE nis = %s)
                """,
                (row["nis"], row["nisn"], row["nama"], row["jeniskelamin"], row["kelas"], row["nis"]),
            )
            if cursor.rowcount:
                inserted += 1
            else:
                skipped += 1
        conn.commit()
        return {"inserted": inserted, "skipped": skipped}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

@app.get("/api/eskul/manage")
async def manage_eskul_list():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id, e.nama_eskul, COUNT(s.id) AS siswa_count
            FROM eskul e
            LEFT JOIN siswa s ON s.eskul = e.id
            GROUP BY e.id, e.nama_eskul
            ORDER BY e.nama_eskul
        """)
        return {"eskul": cursor.fetchall()}
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

@app.post("/api/eskul/create")
async def create_eskul(nama_eskul: str = Form(...)):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO eskul (nama_eskul)
            SELECT %s
            WHERE NOT EXISTS (SELECT 1 FROM eskul WHERE nama_eskul = %s)
            RETURNING id, nama_eskul
        """, (nama_eskul.strip(), nama_eskul.strip()))
        created = cursor.fetchone()
        if not created:
            raise HTTPException(status_code=400, detail="Nama eskul sudah ada")
        conn.commit()
        return {"eskul": created}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

@app.post("/api/eskul/{eskul_id}/update")
async def update_eskul(eskul_id: int, nama_eskul: str = Form(...)):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM eskul WHERE nama_eskul = %s AND id <> %s", (nama_eskul.strip(), eskul_id))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Nama eskul sudah ada")
        cursor.execute("UPDATE eskul SET nama_eskul = %s WHERE id = %s RETURNING id, nama_eskul", (nama_eskul.strip(), eskul_id))
        updated = cursor.fetchone()
        if not updated:
            raise HTTPException(status_code=404, detail="Eskul tidak ditemukan")
        conn.commit()
        return {"eskul": updated}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

@app.delete("/api/eskul/{eskul_id}")
async def delete_eskul(eskul_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS count FROM siswa WHERE eskul = %s", (eskul_id,))
        if cursor.fetchone()["count"] > 0:
            raise HTTPException(status_code=400, detail="Eskul tidak bisa dihapus karena sudah dipilih siswa")
        cursor.execute("DELETE FROM eskul WHERE id = %s", (eskul_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Eskul tidak ditemukan")
        conn.commit()
        return {"success": True}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

@app.get("/api/students/manage")
async def manage_students(kelas: str = ""):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = conn.cursor()
        if kelas:
            cursor.execute("""
                SELECT id, nis, nisn, nama, jeniskelamin, kelas, eskul
                FROM siswa
                WHERE kelas = %s
                ORDER BY kelas, nama
            """, (kelas,))
        else:
            cursor.execute("""
                SELECT id, nis, nisn, nama, jeniskelamin, kelas, eskul
                FROM siswa
                ORDER BY kelas, nama
            """)
        return {"students": cursor.fetchall()}
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

@app.post("/api/students/create")
async def create_student(
    nis: str = Form(...),
    nisn: str = Form(...),
    nama: str = Form(...),
    jeniskelamin: str = Form(...),
    kelas: str = Form(...),
):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM siswa WHERE nis = %s", (nis.strip(),))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="NIS sudah ada")
        cursor.execute("""
            INSERT INTO siswa (nis, nisn, nama, jeniskelamin, kelas)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (nis.strip(), nisn.strip(), nama.strip(), jeniskelamin.strip().upper(), kelas.strip()))
        created = cursor.fetchone()
        conn.commit()
        return {"id": created["id"]}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

@app.post("/api/students/{student_id}/update")
async def update_student(
    student_id: int,
    nis: str = Form(...),
    nisn: str = Form(...),
    nama: str = Form(...),
    jeniskelamin: str = Form(...),
    kelas: str = Form(...),
):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM siswa WHERE nis = %s AND id <> %s", (nis.strip(), student_id))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="NIS sudah ada")
        cursor.execute("""
            UPDATE siswa
            SET nis = %s, nisn = %s, nama = %s, jeniskelamin = %s, kelas = %s
            WHERE id = %s
        """, (nis.strip(), nisn.strip(), nama.strip(), jeniskelamin.strip().upper(), kelas.strip(), student_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
        conn.commit()
        return {"success": True}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

@app.delete("/api/students/{student_id}")
async def delete_student(student_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM siswa WHERE id = %s", (student_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
        conn.commit()
        return {"success": True}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

@app.post("/api/students/bulk-delete")
async def bulk_delete_students(ids: List[int] = Body(...)):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM siswa WHERE id = ANY(%s)", (ids,))
        deleted = cursor.rowcount
        conn.commit()
        return {"deleted": deleted}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

@app.post("/api/submit")
async def submit_form(
    siswa_id: int = Form(...),
    eskul_id: int = Form(...)
):
    """API untuk submit form eskul siswa"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor()
        
        # Ambil data siswa dan eskul untuk validasi
        cursor.execute("""
            SELECT s.kelas, s.nama, e.nama_eskul 
            FROM siswa s, eskul e 
            WHERE s.id = %s AND e.id = %s
        """, (siswa_id, eskul_id))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Siswa atau eskul tidak ditemukan")
        
        kelas = result['kelas'] or ''
        nama_siswa = result['nama']
        nama_eskul = result['nama_eskul']
        
        # Validasi eskul berdasarkan kelas
        restricted_eskul = ['Pencak Silat', 'Futsal', 'Angklung']
        is_kelas_1 = 'kelas 1' in kelas.lower()
        is_kelas_2 = 'kelas 2' in kelas.lower()
        
        if (is_kelas_1 or is_kelas_2) and nama_eskul in restricted_eskul:
            raise HTTPException(
                status_code=400, 
                detail=f"Siswa kelas 1 dan kelas 2 tidak dapat memilih {nama_eskul}. Eskul ini hanya untuk kelas 3 ke atas."
            )
        
        # Update eskul siswa
        cursor.execute(
            "UPDATE siswa SET eskul = %s WHERE id = %s",
            (eskul_id, siswa_id)
        )
        
        # Cek apakah ada record yang terupdate
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
        
        conn.commit()
        
        return {
            "success": True,
            "message": f"Berhasil mendaftarkan {nama_siswa} ke eskul {nama_eskul}",
            "data": {
                "nama": nama_siswa,
                "nama_eskul": nama_eskul,
                "kelas": kelas
            }
        }
        
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

@app.get("/api/registrations")
async def get_registrations():
    """API untuk melihat data registrasi eskul"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                s.id,
                COALESCE(s.nis, '') as nis, 
                COALESCE(s.nisn, '') as nisn, 
                COALESCE(s.nama, 'Nama tidak tersedia') as nama, 
                COALESCE(s.jeniskelamin, '') as jeniskelamin, 
                COALESCE(s.kelas, 'Tidak diketahui') as kelas, 
                e.nama_eskul
            FROM siswa s
            LEFT JOIN eskul e ON s.eskul = e.id
            ORDER BY s.kelas, s.nama
        """)
        
        registrations = cursor.fetchall()
        
        # Clean up the data to handle any remaining nulls
        cleaned_registrations = []
        for reg in registrations:
            cleaned_reg = dict(reg)
            # Ensure no None values are sent to frontend
            for key, value in cleaned_reg.items():
                if value is None:
                    cleaned_reg[key] = ''
            cleaned_registrations.append(cleaned_reg)
        
        return {"registrations": cleaned_registrations}
        
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

@app.get("/registrations", response_class=HTMLResponse)
async def view_registrations(request: Request):
    """Halaman untuk melihat data registrasi"""
    return templates.TemplateResponse("registrations.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
