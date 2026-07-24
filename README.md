# Form Eskul Siswa

Website sederhana untuk mengisi form ekstrakurikuler siswa menggunakan FastAPI dengan dropdown yang saling terhubung.

## ✨ Fitur

- 🎯 **Dropdown Terhubung**: Pilih kelas → muncul siswa kelas tersebut → pilih eskul
- 📊 **Data Registrasi**: Lihat data siswa yang sudah mendaftar eskul
- 🎨 **Desain Modern**: Interface yang menarik dan responsif
- 📱 **Mobile Friendly**: Tampilan optimal di desktop dan mobile
- 🔍 **Pencarian Data**: Filter dan cari data registrasi
- 📄 **Export Data**: Export ke CSV dan print

## 🚀 Quick Start dengan Docker Compose

### Prasyarat

Install Docker dan Docker Compose. PostgreSQL tidak perlu diinstall manual karena sudah tersedia di `compose.yaml`.

### Menjalankan aplikasi

```bash
git clone <url-repository>
cd form_eskul
docker compose up --build -d
```

Compose akan otomatis:

1. Menjalankan PostgreSQL 16.
2. Menunggu database siap.
3. Membuat tabel dan indeks melalui `migrate_empty.py`.
4. Menjalankan aplikasi FastAPI.
5. Menyimpan database dalam volume `postgres_data`.

Buka aplikasi:

- Halaman guru: **http://localhost:8000**
- Halaman admin: **http://localhost:8000/registrations**
- PIN admin lokal bawaan: `112231`

### Konfigurasi lokal

Aplikasi dapat langsung berjalan tanpa `.env`. Untuk mengganti konfigurasi bawaan, buat file `.env` di root project:

```env
APP_PORT=8000
POSTGRES_DB=form_eskul
POSTGRES_USER=form_eskul
POSTGRES_PASSWORD=ganti-password-database
ADMIN_PIN=112231
SESSION_SECRET=ganti-dengan-string-acak-panjang
```

Buat session secret dengan:

```bash
openssl rand -hex 32
```

File `.env` sudah diabaikan Git. Jangan commit password, PIN, atau session secret.

Setelah mengubah `.env`, terapkan ulang container:

```bash
docker compose up --build -d
```

### Mengisi data awal

Database lokal dimulai dalam keadaan kosong. Masuk ke halaman admin, buka tab **Import**, lalu upload file `.xlsx`.

Importer mendukung banyak sheet dan posisi header dinamis. Kolom wajib:

- Nama
- Jenis kelamin (`L` atau `P`)
- Kelas

NIS dan NISN bersifat opsional. Jika NIS kosong, aplikasi membuat ID stabil secara otomatis. Gunakan **Preview** sebelum menjalankan import.

### Operasional Compose

Lihat status container:

```bash
docker compose ps
```

Lihat log aplikasi:

```bash
docker compose logs -f app
```

Hentikan aplikasi tanpa menghapus database:

```bash
docker compose down
```

Hapus aplikasi beserta seluruh data database lokal:

```bash
docker compose down -v
```

Perintah terakhir bersifat destruktif dan tidak dapat membatalkan penghapusan data.

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
