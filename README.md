# Form Eskul Siswa

Website sederhana untuk mengisi form ekstrakurikuler siswa menggunakan FastAPI dengan dropdown yang saling terhubung.

## ✨ Fitur

- 🎯 **Dropdown Terhubung**: Pilih kelas → muncul siswa kelas tersebut → pilih eskul
- 📊 **Data Registrasi**: Lihat data siswa yang sudah mendaftar eskul
- 🎨 **Desain Modern**: Interface yang menarik dan responsif
- 📱 **Mobile Friendly**: Tampilan optimal di desktop dan mobile
- 🔍 **Pencarian Data**: Filter dan cari data registrasi
- 📄 **Export Data**: Export ke CSV dan print

## 🚀 Quick Start

### 1. Persiapan Database

Pastikan PostgreSQL sudah terinstall dan berjalan. Kemudian buat database:

```sql
CREATE DATABASE eskul_db;
```

### 2. Konfigurasi Database

Edit file `config.py` atau `main.py` dan sesuaikan konfigurasi database:

```python
DB_CONFIG = {
    "host": "localhost",
    "database": "eskul_db",
    "user": "your_username",
    "password": "your_password"
}
```

### 3. Install Dependencies & Setup Database

```bash
# Aktifkan virtual environment
source enveskul/bin/activate

# Install pandas untuk import data
pip install pandas

# Setup database dan import data
python setup_database.py
```

### 4. Jalankan Aplikasi

```bash
# Jalankan server FastAPI
python main.py
```

Buka browser ke: **http://localhost:8000**

## 📁 Struktur Project

```
form_eskul/
├── main.py                 # Aplikasi FastAPI utama
├── config.py              # Konfigurasi database
├── setup_database.py      # Script setup database
├── dataset.csv            # Data siswa
├── templates/             # Template HTML
│   ├── index.html         # Halaman form
│   └── registrations.html # Halaman data registrasi
├── static/               # File statis
│   ├── css/
│   │   └── style.css     # Custom CSS
│   └── js/
│       ├── app.js        # JavaScript form
│       └── registrations.js # JavaScript data registrasi
└── enveskul/             # Virtual environment
```

## 🎮 Cara Penggunaan

### Form Pendaftaran Eskul

1. **Pilih Kelas**: Pilih kelas dari dropdown pertama
2. **Pilih Siswa**: Setelah memilih kelas, dropdown siswa akan muncul
3. **Pilih Eskul**: Pilih ekstrakurikuler yang diinginkan
4. **Submit**: Klik tombol "Daftarkan ke Eskul"

### Melihat Data Registrasi

1. Klik menu "Data Registrasi" di navbar
2. Lihat tabel lengkap siswa dan eskul mereka
3. Gunakan fitur pencarian untuk filter data
4. Export data ke CSV atau print jika diperlukan

## 🛠️ Teknologi

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL + psycopg2
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Data Table**: DataTables.js
- **Icons**: Font Awesome

## 📊 Database Schema

### Tabel `eskul`
```sql
CREATE TABLE eskul (
    id SERIAL PRIMARY KEY,
    nama_eskul VARCHAR(50)
);
```

### Tabel `siswa`
```sql
CREATE TABLE siswa (
    id SERIAL PRIMARY KEY,
    nis VARCHAR(20),
    nisn VARCHAR(20),
    nama VARCHAR(255),
    jeniskelamin VARCHAR(1),
    kelas VARCHAR(15),
    eskul INTEGER,
    CONSTRAINT fk_eskul
        FOREIGN KEY(eskul)
        REFERENCES eskul(id)
        ON DELETE SET NULL
);
```

## 🎨 Kustomisasi

### Menambah Eskul Baru

Edit file `setup_database.py` dan tambahkan eskul di array `eskul_data`:

```python
eskul_data = [
    "Pramuka",
    "PMR",
    "Eskul Baru Anda",  # Tambah di sini
    # ... eskul lainnya
]
```

### Mengubah Tampilan

Edit file `static/css/style.css` untuk mengubah tema warna dan styling.

### Menambah Kolom Data

1. Alter table database
2. Update form di `templates/index.html`
3. Update JavaScript di `static/js/app.js`
4. Update API endpoint di `main.py`

## 🔧 Troubleshooting

### Error Database Connection

1. Pastikan PostgreSQL berjalan
2. Cek username/password di config
3. Pastikan database sudah dibuat

### Error Import Data

1. Pastikan file `dataset.csv` ada
2. Cek format CSV (header: NIS,NISN,Nama,JenisKelamin,Kelas)
3. Install pandas: `pip install pandas`

### Error Permission

Pastikan virtual environment aktif dan dependencies terinstall:

```bash
source enveskul/bin/activate
pip install fastapi uvicorn jinja2 python-multipart psycopg2 pandas
```

## 📝 API Endpoints

- `GET /` - Halaman form utama
- `GET /registrations` - Halaman data registrasi
- `GET /api/kelas` - API daftar kelas
- `GET /api/siswa/{kelas}` - API siswa per kelas
- `GET /api/eskul` - API daftar eskul
- `POST /api/submit` - API submit form
- `GET /api/registrations` - API data registrasi

## 👥 Kontribusi

Silahkan buat issue atau pull request untuk perbaikan dan fitur baru.

## 📄 Lisensi

MIT License - Silahkan digunakan untuk keperluan pendidikan dan komersial.

---

**Dibuat dengan ❤️ menggunakan FastAPI & Bootstrap**
