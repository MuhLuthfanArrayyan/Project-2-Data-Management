# Database Stress Test & Performance Benchmark

![Google Colab](https://img.shields.io/badge/Google%20Colab-Supported-orange?logo=googlecolab)
![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Database](https://img.shields.io/badge/Database-PostgreSQL%20%2F%20MySQL-blue)

Repository ini berisi skrip dan repositori penunjang untuk melakukan **stress testing** dan pengujian performa database (Database Management) yang dirancang agar dapat dijalankan secara langsung melalui **Google Colab**.

---

## Quick Link

- **Google Colab Notebook:**  
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/16A4Pm2EaoSSAVk8zrsAOUW0G8zmqoixo?usp=sharing)

---

## Deskripsi Project

Project ini dibuat untuk menganalisis dan mengukur sejauh mana database dapat menangani beban kerja tinggi (high concurrency/load). Pengujian dilakukan di lingkungan cloud menggunakan Google Colab untuk mensimulasikan berbagai skenario pengujian seperti:
- Pengujian kecepatan query (Insert, Select, Update, Delete).
- Pengujian *concurrency* (akses bersamaan oleh banyak user/koneksi).
- Analisis penggunaan sumber daya (CPU, RAM, dan I/O) saat beban puncak.

---

## Fitur Utama

- **Automated Setup:** Skrip otomatisasi instalasi dan konfigurasi database di lingkungan ephemeral Colab.
- **Stress Testing Tools:** Pengujian performa query secara berulang dan bersamaan.
- **Visualisasi Performa:** Grafis/laporan ringkas mengenai statistik respons time dan throughput.
- **Reproducible:** Bebas dijalankan ulang kapan saja dengan mengklik tombol "Run All" di Colab.

---

## Prasyarat & Teknologi

- **Bahasa:** Python 3.x
- **Lingkungan Eksekusi:** Google Colab / Jupyter Notebook
- **Database Engine:** [Sebutkan database yang digunakan, misal: PostgreSQL / MySQL / SQLite / MongoDB]
- **Library Python Utama:**
  - `psycopg2` / `mysql-connector-python` (Database Driver)
  - `pandas`, `matplotlib` / `seaborn` (Analisis & Visualisasi Data)

---

## Cara Penggunaan

1. Buka notebook melalui tautan berikut:  
   [Google Colab Notebook](https://colab.research.google.com/drive/16A4Pm2EaoSSAVk8zrsAOUW0G8zmqoixo?usp=sharing)
2. Buat salinan notebook ke Google Drive Anda:  
   `File` > `Save a copy in Drive`
3. Jalankan sel kode secara berurutan (*Cell by Cell*) atau pilih **Runtime > Run all**.
4. (Opsional) Sesuaikan variabel batas beban/stress test pada bagian *Configuration* di notebook.

---

## Struktur Repository

```text
├── README.md               # Dokumentasi utama repository
├── data/                   # Dataset opsional / mockup data
├── scripts/                # Skrip pendukung pengujian database
└── config/                 # Konfigurasi koneksi atau skema database
