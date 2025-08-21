# Smartphone Cheating Detection  

Aplikasi *Smartphone Cheating Detection* merupakan aplikasi desktop berbasis Python yang dirancang untuk melakukan *screen monitoring* secara real-time dengan memanfaatkan model YOLOv8. Aplikasi ini berfungsi untuk mendeteksi keberadaan smartphone pada tangkapan layar yang diambil secara berkala, serta memberikan notifikasi *popup* otomatis apabila objek terdeteksi.  

## Persyaratan  

- Python 3.8 atau versi lebih baru  
- Sistem operasi Windows  

## Instalasi  

1. Clone atau unduh repositori ini.  
2. Buat *virtual environment* (optional):  
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```  
3. Install seluruh pustaka yang diperlukan:  
   ```bash
   pip install -r requirements.txt
   ```  

## Penggunaan  

1. Pastikan file model YOLOv8 (`best.pt`) tersedia di folder `model`.  
2. Jalankan aplikasi melalui perintah:  
   ```bash
   python app.py
   ```  
3. Gunakan tombol **Start Monitoring** untuk memulai proses pemantauan.  
4. Apabila smartphone terdeteksi, sistem akan menampilkan notifikasi *popup* secara otomatis.  
5. Tekan tombol **Stop Monitoring** untuk menghentikan proses pemantauan.  

## Fitur Utama  

1. **Screen Monitoring**  
   - Melakukan pemantauan layar secara real-time dengan interval ±1–2 detik.  
   - Hasil deteksi ditampilkan dalam bentuk *bounding box* dan label prediksi.  

2. **Exclusion Zones**  
   - Memungkinkan pengguna menentukan area pada layar yang dikecualikan dari proses deteksi.  
   - Area yang dipilih dapat disimpan ke dalam file `excluded_areas.json` dan digunakan kembali pada sesi berikutnya.  

3. **Load External Screenshot**  
   - Mendukung pemuatan *screenshot* eksternal untuk menentukan zona pengecualian secara manual sebelum monitoring dimulai.  

4. **Application Log**  
   - Mencatat seluruh aktivitas aplikasi secara otomatis, termasuk status monitoring, hasil deteksi, dan perubahan parameter.  

## Struktur Proyek  

```
project/
├── app.py                # File utama aplikasi
├── gui.py                # Implementasi antarmuka aplikasi
├── model/
│   └── best.pt           # Model YOLOv8 untuk deteksi smartphone
├── utils/
│   ├── screen_capture.py # Modul untuk menangkap layar
│   └── detection.py      # Modul deteksi YOLOv8
├── excluded_areas.json   # File konfigurasi area pengecualian
└── README.md             # Dokumentasi proyek
```  

## Pustaka yang Digunakan  

- **Screen Capture**: `mss`  
- **Object Detection**: `Ultralytics YOLOv8`, `torch`  
- **GUI**: `Tkinter`  
- **Image Processing**: `OpenCV`, `NumPy`, `PIL`  
