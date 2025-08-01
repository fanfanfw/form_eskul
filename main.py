from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import List, Dict, Any
import json

try:
    from config import *
except ImportError:
    # Fallback configuration jika config.py tidak ada
    DB_HOST = "localhost"
    DB_DATABASE = "db_form_eskul"
    DB_USER = "fanfan"
    DB_PASSWORD = "cenanun"
    DB_PORT = 5432
    APP_TITLE = "Form Eskul Siswa"
    APP_DESCRIPTION = "Website untuk mengisi form eskul siswa"

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
