# Tugas Analisis Minggu 3 - Integrasi Sistem Informasi

## 1. Analisis Pola Arsitektur (Adapter Pattern)

Rancangan pada praktikum ini dikategorikan sebagai penerapan **Adapter Pattern** dalam arsitektur Enterprise Application Integration (EAI) karena komponen `adapter_service.py` bertindak sebagai penerjemah (*wrapper*) antara dua antarmuka yang tidak saling cocok secara langsung. 

Program *legacy* berbasis bahasa C (`legacy_core.c`) hanya mampu mengakses basis data teks lokal (`students_db.txt`) tanpa kemampuan komunikasi jaringan. Sementara itu, klien web modern mengekspektasikan komunikasi berbasis protokol HTTP dan format data terstruktur seperti XML. Server adapter menjembatani perbedaan ini dengan mengonversi permintaan HTTP/XML menjadi operasi pembacaan dan penulisan berkas teks lokal.

### Keuntungan Bagi Klien Web Luar:
* **Abstraksi dan Decoupling**: Klien web cukup berinteraksi melalui *endpoint* standar (`/students`) dan format XML tanpa perlu mengetahui kerumitan internal, struktur penyimpanan file teks, maupun cara kerja program C di sistem *legacy*.
* **Interoperabilitas**: Mampu mengintegrasikan sistem lama yang kaku (*rigid*) ke dalam ekosistem web modern berbasis SOA tanpa merusak atau mengubah kode sumber mesin *legacy*.
* **Evolusi Sistem Tanpa Henti**: Jika di masa mendatang sistem *legacy* diganti dengan RDBMS modern, antarmuka adapter dapat tetap dipertahankan sehingga aplikasi klien tidak memerlukan perubahan sama sekali.

---

## 2. Analisis Overhead Serialisasi Data XML

Berikut adalah perhitungan rasio *overhead* dari format serialisasi XML berdasarkan pengujian `GET /students/2415354001`:

### A. Data Aktual (Payload Murni)
Karakter dari nilai data aktual tanpa pembungkus:
* `NIM`: `2415354001` (10 byte)
* `Nama`: `I Made Sujana` (13 byte)
* `Jurusan`: `Teknologi Informasi` (19 byte)
* `Status`: `ACTIVE` (6 byte)

$$\text{Total Byte Data Aktual} = 10 + 13 + 19 + 6 = 48\text{ byte}$$

### B. Total Respons XML (Termasuk Structure Tag)
Dokumen XML lengkap yang dihasilkan oleh adapter:

```xml
<?xml version='1.0' encoding='utf-8'?>
<StudentResponse><NIM>2415354001</NIM><Nama>I Made Sujana</Nama><Jurusan>Teknologi Informasi</Jurusan><Status>ACTIVE</Status></StudentResponse>
```

Ukuran total dari seluruh string dokumen XML di atas adalah **175 byte**.

### C. Perhitungan Rasio Overhead

$$\text{Byte Overhead} = \text{Total Respons XML} - \text{Total Data Aktual}$$
$$\text{Byte Overhead} = 175\text{ byte} - 48\text{ byte} = 127\text{ byte}$$

$$\text{Rasio Overhead (\%)} = \left( \frac{\text{Byte Overhead}}{\text{Total Data Aktual}} \right) \times 100\%$$
$$\text{Rasio Overhead (\%)} = \left( \frac{127}{48} \right) \times 100\% \approx 264.58\%$$

> **Kesimpulan Analysis:** Serialisasi XML menghasilkan *overhead* transmisi sebesar **264.58%** dari ukuran data asli. Hal ini disebabkan oleh penggunaan deklarasi header XML serta tag pembungkus (*element tags*) yang cukup dominan (*verbose*).

---

## 3. Prediksi Keterbatasan Integrasi & Masalah Konkurensi

Jika 500 permintaan `POST` datang ke server adapter secara simultan pada detik yang sama, akan terjadi masalah **Race Condition** dan **File Locking Conflict** pada berkas basis data `students_db.txt`.

### Dampak Pada Berkas Teks:
1. **Integritas Data Rusak (Data Corruption)**: Karena `students_db.txt` adalah file teks biasa tanpa mekanisme *transaction lock* atau *ACID Compliance*, beberapa proses penulisan (*write*) yang terjadi bersamaan akan saling menimpa baris teks satu sama lain. Hasilnya, struktur CSV menjadi berantakan atau sebagian baris data hilang.
2. **Kegagalan Akses Berkas (I/O Exception)**: Sistem operasi akan mengunci berkas ketika sedang ditulis oleh satu thread/proses. Hal ini menyebabkan permintaan lainnya mengalami *permission error* atau *access collision* saat mencoba membuka file secara bersamaan.

### Mengapa Message Broker Dibutuhkan?
Untuk mengatasi masalah tingkat konkurensi tinggi ini, arsitektur di masa mendatang memerlukan **Message Broker** (seperti RabbitMQ, Apache Kafka, atau Redis Streams):
* **Asynchronous Queueing**: Message Broker menerima 500 permintaan `POST` secara langsung di memori dan menyimpannya ke dalam antrean (*queue*).
* **Rate Limiting & Sequential Processing**: Adapter/Worker akan mengambil pesan dari antrean satu per satu (*sequentially*) untuk dituliskannya secara teratur ke dalam `students_db.txt`, sehingga mencegah terjadinya benturan akses file (*race condition*).