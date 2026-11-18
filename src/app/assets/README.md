# Aset Foto Stimulus Skenario Survei

Direktori ini memuat 4 foto representatif untuk masing-masing varian perlakuan A/B testing (Step 1 Halaman Skenario).

---

## Struktur File yang Diharapkan

```text
src/app/assets/
├── variant_a/                  # Pembelajaran Luring (Tatap Muka di Kelas)
│   ├── 1_lecture.jpg           # Foto dosen menerangkan di kelas / papan tulis
│   ├── 2_discussion.jpg        # Foto mahasiswa berdiskusi kelompok di meja kelas
│   ├── 3_qa.jpg                # Foto tanya jawab langsung / acung tangan
│   └── 4_assignment.jpg        # Foto pengerjaan tugas / ujian di lembar kertas
└── variant_b/                  # Pembelajaran Daring (Online via Zoom / LMS)
    ├── 1_lecture.jpg           # Foto screen sharing slide di Zoom / Google Meet
    ├── 2_discussion.jpg        # Foto breakout room / diskusi dokumen online
    ├── 3_qa.jpg                # Foto interaksi mic / raise hand / chat box
    └── 4_assignment.jpg        # Foto submit tugas via LMS / Google Classroom
```

---

## Rekomendasi Format & Ukuran Gambar
* **Format:** JPG atau WebP (terkompresi).
* **Dimensi / Rasio:** ~`600 x 400 px` (aspek rasio 3:2 atau 4:3).
* **Ukuran per File:** ≤ 100 KB per foto (agar total seluruh foto ≤ 800 KB, menjaga waktu muat web ≤ 2 detik).
* **Fallback Otomatis:** Jika salah satu foto belum dimasukkan, aplikasi web Streamlit (`main.py`) akan otomatis menampilkan kartu placeholder tanpa memicu error crash.
