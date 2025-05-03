# Smartphone Detection Monitor

Aplikasi desktop Python yang dapat:
1. Merekam seluruh layar secara real-time dengan interval refresh 1-2 detik
2. Menggunakan model YOLOv8 untuk mendeteksi smartphone di dalam tangkapan layar
3. Menampilkan notifikasi popup ketika smartphone terdeteksi
4. Menyediakan antarmuka sederhana dengan kontrol pemantauan dan area log

## Persyaratan

- Python 3.8 atau lebih baru
- Sistem operasi Windows

## Instalasi

1. Clone atau download repository ini
2. Buat virtual environment (direkomendasikan):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install paket-paket yang diperlukan:
   ```
   pip install -r requirements.txt
   ```

## Penggunaan

1. Pastikan file model YOLOv8 (`best.pt`) berada di direktori `model`
2. Jalankan aplikasi:
   ```
   python app.py
   ```
3. Gunakan tombol "Start Monitoring" untuk memulai deteksi
4. Notifikasi popup akan muncul ketika smartphone terdeteksi
5. Gunakan tombol "Stop Monitoring" untuk menghentikan deteksi

## Fitur Tambahan

1. **Exclusion Zones**: Tentukan area-area di layar yang akan diabaikan oleh detektor.
   - Gunakan tombol "Select Area" untuk memilih area pada preview layar
   - Klik dan drag untuk membuat rectangle yang akan diabaikan
   - Area yang dipilih akan ditandai sebagai zona pengecualian

2. **Load External Screenshot**: Muat screenshot eksternal untuk memilih area pengecualian.
   - Berguna untuk memilih area pada aplikasi yang biasanya tertutup saat aplikasi monitor aktif
   - Gunakan tombol "Load Screenshot" untuk memilih file gambar
   - Pilih area pengecualian pada gambar yang dimuat

3. **Save Zones**: Simpan area pengecualian ke file untuk digunakan kembali di sesi mendatang.
   - Semua area pengecualian disimpan di file `excluded_areas.json`

## Struktur Proyek

```
project/
├── app.py                # File utama untuk menjalankan aplikasi
├── gui.py                # Implementasi GUI dan komponen UI
├── model/
│   └── best.pt           # Model YOLOv8 untuk deteksi smartphone
├── utils/
│   ├── screen_capture.py # Fungsi-fungsi untuk merekam layar
│   └── detection.py      # Implementasi deteksi YOLOv8
├── excluded_areas.json   # Menyimpan area yang dikecualikan dari deteksi
└── README.md             # File ini
```

## Perubahan Pada Versi Terbaru

- Memisahkan GUI dari logika aplikasi untuk kode yang lebih terorganisir
- Memperbaiki masalah warna pada gambar preview (konversi BGR/RGB)
- Menambahkan fitur untuk memuat screenshot eksternal
- Menambahkan fitur untuk menyimpan dan memuat exclusion zones

## Library yang Digunakan

- **Screen Capture**: mss (untuk merekam layar dengan cepat)
- **Object Detection**: Ultralytics YOLOv8 / torch
- **GUI**: Tkinter (untuk antarmuka desktop yang ringan)
- **Image Processing**: OpenCV, Numpy, PIL

## Catatan

- Aplikasi dirancang ringan dan responsif
- Deteksi terjadi di memori tanpa menyimpan screenshot ke disk
- Interval rekam yang dapat disesuaikan di class ScreenCapture (default: 1.5 detik)
- Notifikasi muncul sebagai popup di layar ketika smartphone terdeteksi 