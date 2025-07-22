from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
from typing import List, Dict, Any

app = FastAPI(title="Form Eskul Siswa (Demo)", description="Demo website form eskul dengan data dummy")

# Setup templates dan static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Data dummy untuk demo
DUMMY_KELAS = ["Kelas 2A", "Kelas 2B", "Kelas 2C", "Kelas 2D", "Kelas 2E"]

DUMMY_SISWA = {
    "Kelas 2A": [
        {"id": 1, "nis": "2425021011858", "nisn": "0156718794", "nama": "ABIZAR GUFTHA PRATAMA"},
        {"id": 2, "nis": "2425021011859", "nisn": "3178436522", "nama": "ADIBA SHAKILA PUTRI FIRMANSYAH"},
        {"id": 3, "nis": "2425021011860", "nisn": "3187206234", "nama": "AISYAH KIRANA ZAHRA"},
        {"id": 4, "nis": "2425021011861", "nisn": "3172274436", "nama": "ANDINI PUTRI VITALOKA"},
        {"id": 5, "nis": "2425021011862", "nisn": "3176742485", "nama": "ANNISA NUR RAFANI"}
    ],
    "Kelas 2B": [
        {"id": 6, "nis": "2425021011900", "nisn": "0156718800", "nama": "BUDI SANTOSO"},
        {"id": 7, "nis": "2425021011901", "nisn": "3178436600", "nama": "CITRA DEWI"},
        {"id": 8, "nis": "2425021011902", "nisn": "3187206300", "nama": "DANI RAMADHAN"},
        {"id": 9, "nis": "2425021011903", "nisn": "3172274500", "nama": "EVA SARI"},
        {"id": 10, "nis": "2425021011904", "nisn": "3176742600", "nama": "FAJAR NUGROHO"}
    ],
    "Kelas 2C": [
        {"id": 11, "nis": "2425021012000", "nisn": "0156718900", "nama": "GITA AMANDA"},
        {"id": 12, "nis": "2425021012001", "nisn": "3178436700", "nama": "HENDRA WIJAYA"},
        {"id": 13, "nis": "2425021012002", "nisn": "3187206400", "nama": "INDAH PERMATA"},
        {"id": 14, "nis": "2425021012003", "nisn": "3172274600", "nama": "JOKO SUSILO"},
        {"id": 15, "nis": "2425021012004", "nisn": "3176742700", "nama": "KARTIKA SARI"}
    ]
}

DUMMY_ESKUL = [
    {"id": 1, "nama_eskul": "Pramuka"},
    {"id": 2, "nama_eskul": "PMR (Palang Merah Remaja)"},
    {"id": 3, "nama_eskul": "Paskibra"},
    {"id": 4, "nama_eskul": "Basket"},
    {"id": 5, "nama_eskul": "Sepak Bola"},
    {"id": 6, "nama_eskul": "Voli"},
    {"id": 7, "nama_eskul": "Badminton"},
    {"id": 8, "nama_eskul": "Band/Musik"},
    {"id": 9, "nama_eskul": "Tari"},
    {"id": 10, "nama_eskul": "English Club"}
]

# Storage untuk registrasi (dalam memory untuk demo)
registrations = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Halaman utama dengan form"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/kelas")
async def get_kelas():
    """API untuk mendapatkan daftar kelas yang tersedia"""
    return {"kelas": DUMMY_KELAS}

@app.get("/api/siswa/{kelas}")
async def get_siswa_by_kelas(kelas: str):
    """API untuk mendapatkan daftar siswa berdasarkan kelas"""
    siswa_list = DUMMY_SISWA.get(kelas, [])
    return {"siswa": siswa_list}

@app.get("/api/eskul")
async def get_eskul():
    """API untuk mendapatkan daftar ekstrakurikuler"""
    return {"eskul": DUMMY_ESKUL}

@app.post("/api/submit")
async def submit_form(
    siswa_id: int = Form(...),
    eskul_id: int = Form(...)
):
    """API untuk submit form eskul siswa"""
    
    # Cari siswa
    siswa_found = None
    for kelas, siswa_list in DUMMY_SISWA.items():
        for siswa in siswa_list:
            if siswa['id'] == siswa_id:
                siswa_found = siswa
                siswa_found['kelas'] = kelas
                break
        if siswa_found:
            break
    
    if not siswa_found:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
    
    # Cari eskul
    eskul_found = None
    for eskul in DUMMY_ESKUL:
        if eskul['id'] == eskul_id:
            eskul_found = eskul
            break
    
    if not eskul_found:
        raise HTTPException(status_code=404, detail="Eskul tidak ditemukan")
    
    # Simpan registrasi
    registrations[siswa_id] = {
        "siswa": siswa_found,
        "eskul": eskul_found
    }
    
    return {
        "success": True,
        "message": f"Berhasil mendaftarkan {siswa_found['nama']} ke eskul {eskul_found['nama_eskul']}",
        "data": {
            "nama": siswa_found['nama'],
            "nama_eskul": eskul_found['nama_eskul'],
            "kelas": siswa_found['kelas']
        }
    }

@app.get("/api/registrations")
async def get_registrations():
    """API untuk melihat data registrasi eskul"""
    
    # Buat data lengkap untuk semua siswa
    all_students = []
    
    for kelas, siswa_list in DUMMY_SISWA.items():
        for siswa in siswa_list:
            student_data = {
                "nis": siswa["nis"],
                "nisn": siswa["nisn"],
                "nama": siswa["nama"],
                "jeniskelamin": "L" if siswa["nama"].split()[0] in ["ABIZAR", "BUDI", "DANI", "FAJAR", "HENDRA", "JOKO"] else "P",
                "kelas": kelas,
                "nama_eskul": None
            }
            
            # Cek apakah siswa sudah registrasi
            if siswa["id"] in registrations:
                student_data["nama_eskul"] = registrations[siswa["id"]]["eskul"]["nama_eskul"]
            
            all_students.append(student_data)
    
    return {"registrations": all_students}

@app.get("/registrations", response_class=HTMLResponse)
async def view_registrations(request: Request):
    """Halaman untuk melihat data registrasi"""
    return templates.TemplateResponse("registrations.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Form Eskul Demo (No Database Required)")
    print("📍 Access URL: http://localhost:8000")
    print("📊 Data Registrasi: http://localhost:8000/registrations")
    print("🛑 Press Ctrl+C to stop")
    print("💡 This is demo version with dummy data")
    print("-" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
