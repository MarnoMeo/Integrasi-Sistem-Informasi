# LAPORAN PRAKTIKUM PERTEMUAN 4
**Mata Kuliah:** Integrasi Sistem Informasi  
**Topik:** Integrasi Modern Web Services & API Gateway (RESTful HTTP/JSON)  

---

## 1. Pendahuluan & Tujuan Praktikum

Pada praktikum minggu ke-4 ini, dilakukan implementasi pola **API Gateway** yang bertindak sebagai titik masuk tunggal (*single entry point*) untuk mengintegrasikan layanan modern berbasis RESTful HTTP/JSON dengan sistem *legacy* berbasis berkas teks (`data.txt`) yang dibuat pada praktikum sebelumnya.

### Tujuan Utama:
1. Memahami arsitektur integrasi modern berbasis **API Gateway Pattern**.
2. Membangun antarmuka REST API menggunakan format serialisasi **JSON** untuk operasi `GET` dan `POST`.
3. Mengintegrasikan API Gateway dengan basis data teks *legacy*.
4. Melakukan *benchmarking* kuantitatif untuk membandingkan efisiensi ukuran transmisi data (*payload size*) antara XML dan JSON.
5. Menganalisis keterbatasan komunikasi sinkron (*synchronous blocking*) pada protokol HTTP/1.1.

---

## 2. Arsitektur & Topologi Integrasi

Sistem yang dibangun terdiri dari tiga lapisan utama:
* **Klien Eksternal**: Berkomunikasi menggunakan protokol HTTP/1.1 dengan *payload* berformat JSON (`application/json`).
* **API Gateway (Flask / Python)**: Menangani perutean (*routing*), validasi input, pencegahan ID ganda, serta transformasi data antara format JSON dan format baris teks *legacy*.
* **Sistem Legacy (`data.txt`)**: Menyimpan data transaksi/mahasiswa dalam format delimitasi karakter pipa (`|`).

---

## 3. Pengujian Fungsionalitas REST API

### A. Pengujian Operasi `GET /api/v1/students`
* **Permintaan**: `curl -i -X GET http://localhost:5000/api/v1/students`
* **Status HTTP**: `200 OK`
* **Content-Type**: `application/json`
* **Hasil**: API Gateway membaca seluruh baris dari `data.txt`, mengonversinya ke dalam struktur JSON terformat lengkap dengan *metadata* (service, format, total_records, timestamp).

### B. Pengujian Operasi `POST /api/v1/students`
* **Permintaan**:
  ```bash
  curl -i -X POST http://localhost:5000/api/v1/students \
       -H "Content-Type: application/json" \
       -d '{"id": "104", "nama": "Dewi Sartika", "jurusan": "Sistem Informasi", "status": "Aktif"}'
  ```
* **Status HTTP**: `201 Created`
* **Hasil**: Data baru berhasil divalidasi, diformat ulang, dan ditambahkan ke baris paling akhir pada berkas `data.txt` (`104|Dewi Sartika|Sistem Informasi|Aktif`).

### C. Penanganan Kesalahan (Error Handling)
* **ID Ganda (Conflict)**: Mengembalikan status `409 Conflict` jika ID yang dimasukkan sudah ada di `data.txt`.
* **Field Kosong (Unprocessable Entity)**: Mengembalikan status `422 Unprocessable Entity` jika ada atribut wajib yang hilang.
* **Payload Kosong (Bad Request)**: Mengembalikan status `400 Bad Request` jika tidak ada body JSON yang dikirimkan.

---

## 4. Hasil Uji Komparasi Serialisasi (Benchmark: XML vs JSON)

Pengujian skrip `benchmark_serialization.py` dilakukan untuk mengukur efisiensi ukuran *payload* biner (dalam byte) antara format XML (Minggu 3) dan JSON (Minggu 4) pada berbagai skala jumlah data:

| Jumlah Rekaman | Ukuran XML (Bytes) | Ukuran JSON (Bytes) | Persentase Efisiensi Ukuran (%) |
| :--- | :--- | :--- | :--- |
| **10 Data** | 1,733 bytes | 1,079 bytes | **37.74%** |
| **50 Data** | 8,213 bytes | 5,119 bytes | **37.67%** |
| **100 Data** | 16,313 bytes | 10,169 bytes | **37.66%** |
| **500 Data** | 81,113 bytes | 50,569 bytes | **37.66%** |

> **Catatan Perhitungan:** Persentase efisiensi dihitung dengan rumus:
> $$\text{Reduksi (\%)} = \left( \frac{\text{Ukuran XML} - \text{Ukuran JSON}}{\text{Ukuran XML}} \right) \times 100\%$$

---

## 5. Lembar Analisis Kritis

### 1. Analisis Struktur Payload (Sintaksis XML vs JSON)
Faktor sintaksis utama yang membuat XML menghasilkan ukuran biner jauh lebih besar dibandingkan JSON untuk data yang identik meliputi:
* **Redundansi Tag Penutup**: Pada XML, setiap elemen memerlukan tag pembuka dan tag penutup berulang (contoh: `<student>...</student>`, `<jurusan>...</jurusan>`). Sebaliknya, JSON hanya menggunakan tanda kurung kurawal `{}` dan petik kunci `"key": "value"` yang jauh lebih ringkas.
* **Deklarasi Header**: XML membutuhkan deklarasi header wajib di awal dokumen (`<?xml version='1.0' encoding='utf-8'?>`), sedangkan JSON tidak memerlukan header sintaksis tambahan di dalam *payload*-nya.
* **Penggunaan Array**: JSON mendukung struktur larik (*array*) bawaan secara langsung menggunakan tanda kurung siku `[]`, sedangkan XML harus membungkus daftar elemen menggunakan tag konteks induk tambahan.

### 2. Analisis Deserialisasi / Parsing di Sisi Klien
* **Proses Parsing XML**: Peramban web harus memanggil *DOMParser* untuk mengonversi string XML menjadi dokumen DOM, kemudian melakukan penelusuran hierarki node menggunakan method seperti `getElementsByTagName()` atau `querySelector()`. Proses ini membutuhkan penggunaan memori dan siklus CPU yang lebih tinggi.
* **Proses Parsing JSON**: Ekosistem JavaScript di peramban web memiliki dukungan bawaan secara *native* melalaui fungsi `JSON.parse()`. String JSON langsung dikonversi menjadi objek JavaScript siap pakai secara cepat.
* **Alasan Migrasi**: Industri web modern beralih ke JSON karena kecepatannya dalam pemrosesan *client-side*, ukuran *payload* yang lebih hemat *bandwidth*, serta kesesuaian alami (*native integration*) dengan bahasa JavaScript dan kerangka kerja *front-end* modern (React, Vue, Angular).

### 3. Bottleneck Arsitektur RESTful Synchronous (HTTP/1.1 Blocking)
* **Skenario Failover**: Jika sistem *legacy* C membutuhkan waktu 1.5 detik untuk melakukan *file locking* saat menulis ke `data.txt`, maka 100 permintaan `POST` yang masuk secara bersamaan akan menyebabkan penumpukan thread server. Klien ke-100 harus menunggu antrean pemblokiran I/O secara kumulatif hingga berpotensi mengalami *Request Timeout* (504).
* **Penyebab Bottleneck**: HTTP/1.1 bersifat *synchronous blocking* dan mengalami masalah *Head-of-Line (HoL) Blocking*, di mana koneksi/thread dipaksa menggantung (*waiting*) sampai I/O ke penyimpanan *legacy* selesai sepenuhnya.
* **Solusi Arsitektur Masa Depan**:
  * **gRPC / HTTP/2 (Minggu 5)**: Memanfaatkan fitur *multiplexing* dalam satu koneksi TCP tunggal serta serialisasi biner (Protocol Buffers) yang mengurangi latensi dan penumpukan *thread*.
  * **Asynchronous Message Broker (Minggu 6)**: Menerapkan mekanisme antrean pesan (seperti RabbitMQ/Kafka) untuk memisahkan proses penerimaan HTTP request dengan penulisan file *legacy* (*decoupling*), sehingga API Gateway dapat langsung merespons `202 Accepted` tanpa harus menunggu operasi I/O disk selesai.