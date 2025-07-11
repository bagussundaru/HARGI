# HAR GI Dashboard

Dashboard aplikasi untuk visualisasi data HAR GI (Hasil Akhir Rencana Gardu Induk) dengan teknologi Flask dan Chart.js.

## Fitur Utama

- **Dashboard Interaktif**: Visualisasi data real-time dengan KPI cards dan charts
- **Integrasi Excel**: Membaca data langsung dari file `D:\DASHBOARDHARGI.xlsx`
- **Filter Dinamis**: Filter berdasarkan tahun, bulan, lokasi, status, dan sifat pekerjaan
- **Responsive Design**: Tampilan yang optimal di berbagai ukuran layar
- **Real-time Updates**: Data dashboard terupdate otomatis saat file Excel diubah

## Struktur Proyek

```
Har_GI/
├── src/
│   ├── main.py              # Entry point aplikasi Flask
│   ├── routes/
│   │   └── dashboard.py     # Route dan logic dashboard
│   └── static/
│       ├── index.html       # Template HTML utama
│       ├── style.css        # Styling CSS
│       └── dashboard.js     # JavaScript untuk interaktivitas
├── DASHBOARDHARGI.xlsx      # File data Excel
├── requirements.txt         # Dependencies Python
├── start_dashboard.bat      # Script untuk menjalankan di Windows
├── start_dashboard.sh       # Script untuk menjalankan di Linux/Mac
└── README.md               # Dokumentasi proyek
```

## Instalasi dan Menjalankan

### Prerequisites
- Python 3.7+
- File Excel `DASHBOARDHARGI.xlsx` di lokasi `D:\`

### Langkah Instalasi

1. Clone repository:
```bash
git clone https://github.com/bagussundaru/HARGI.git
cd HARGI
```

2. Buat virtual environment:
```bash
python -m venv venv
```

3. Aktivasi virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Pastikan file `DASHBOARDHARGI.xlsx` ada di `D:\DASHBOARDHARGI.xlsx`

6. Jalankan aplikasi:
- Windows: `start_dashboard.bat`
- Linux/Mac: `./start_dashboard.sh`

7. Buka browser dan akses: `http://127.0.0.1:5000`

## Konfigurasi Data

Aplikasi membaca data dari sheet "REALISASI HAR GI" dalam file Excel `D:\DASHBOARDHARGI.xlsx`. Struktur data yang diharapkan:

- Header dimulai dari baris ke-5
- Kolom yang diperlukan: RENCANA, LOKASI, STATUS, SIFAT_PEKERJAAN, KATEGORI
- Format tanggal pada kolom RENCANA untuk ekstraksi bulan dan tahun

## Teknologi yang Digunakan

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Visualisasi**: Chart.js
- **Data Processing**: openpyxl, pandas
- **Styling**: CSS Grid, Flexbox

## Kontribusi

Untuk berkontribusi pada proyek ini:

1. Fork repository
2. Buat branch fitur baru (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## Lisensi

Proyek ini menggunakan lisensi MIT. Lihat file `LICENSE` untuk detail lebih lanjut.

## Kontak

Bagus Sundaru - [@bagussundaru](https://github.com/bagussundaru)

Project Link: [https://github.com/bagussundaru/HARGI](https://github.com/bagussundaru/HARGI)