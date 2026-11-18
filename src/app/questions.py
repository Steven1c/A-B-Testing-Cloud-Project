"""
questions.py
Instrumen 20 butir pertanyaan survei kepuasan pembelajaran: Luring (Varian A) vs Daring (Varian B).
Teks verbatim mematuhi docs/survey-instrument.md.
"""

from typing import List, Tuple

# Format per item: (no_str, column_name, text_variant_a, text_variant_b)
# Format DIMENSIONS: [(dimension_title, [items...]), ...]

DIMENSIONS: List[Tuple[str, List[Tuple[str, str, str, str]]]] = [
    (
        "Kepuasan & Efektivitas Keseluruhan",
        [
            (
                "Q1",
                "sat_overall",
                "Secara keseluruhan, seberapa puas Anda dengan pengalaman mengikuti metode pembelajaran Luring (tatap muka di kelas)?",
                "Secara keseluruhan, seberapa puas Anda dengan pengalaman mengikuti metode pembelajaran Daring (online via Zoom/LMS)?",
            ),
            (
                "Q2",
                "sat_expectation",
                "Seberapa puas Anda dengan kesesuaian proses pembelajaran Luring terhadap ekspektasi belajar Anda?",
                "Seberapa puas Anda dengan kesesuaian proses pembelajaran Daring terhadap ekspektasi belajar Anda?",
            ),
            (
                "Q3",
                "sat_effectiveness",
                "Seberapa puas Anda terhadap efektivitas pencapaian tujuan perkuliahan melalui metode Luring?",
                "Seberapa puas Anda terhadap efektivitas pencapaian tujuan perkuliahan melalui metode Daring?",
            ),
            (
                "Q4",
                "sat_preference",
                "Seberapa puas Anda apabila metode pembelajaran Luring ini terus diterapkan pada mata kuliah serupa?",
                "Seberapa puas Anda apabila metode pembelajaran Daring ini terus diterapkan pada mata kuliah serupa?",
            ),
        ],
    ),
    (
        "Pedagogis & Pemahaman Materi",
        [
            (
                "Q5",
                "mat_comprehension",
                "Seberapa puas Anda terhadap kemudahan memahami konsep perkuliahan melalui metode Luring (tatap muka langsung)?",
                "Seberapa puas Anda terhadap kemudahan memahami konsep perkuliahan melalui metode Daring (konferensi video & modul digital)?",
            ),
            (
                "Q6",
                "mat_clarity",
                "Seberapa puas Anda dengan kejelasan penyampaian penjelasan dosen melalui papan tulis/proyektor pada perkuliahan Luring?",
                "Seberapa puas Anda dengan kejelasan penyampaian penjelasan dosen melalui berbagi layar (screen sharing) pada perkuliahan Daring?",
            ),
            (
                "Q7",
                "mat_retention",
                "Seberapa puas Anda terhadap daya ingat dan pemahaman jangka panjang materi setelah mengikuti kelas Luring?",
                "Seberapa puas Anda terhadap daya ingat dan pemahaman jangka panjang materi setelah mengikuti kelas Daring?",
            ),
            (
                "Q8",
                "mat_readiness",
                "Seberapa puas Anda dengan tingkat kesiapan Anda mengerjakan tugas atau ujian setelah mengikuti pembelajaran Luring?",
                "Seberapa puas Anda dengan tingkat kesiapan Anda mengerjakan tugas atau ujian setelah mengikuti pembelajaran Daring?",
            ),
        ],
    ),
    (
        "Interaksi & Keterlibatan Belajar",
        [
            (
                "Q9",
                "int_lecturer",
                "Seberapa puas Anda terhadap kemudahan mengajukan pertanyaan langsung kepada dosen pada perkuliahan Luring?",
                "Seberapa puas Anda terhadap kemudahan mengajukan pertanyaan (via mic/kolom chat) kepada dosen pada perkuliahan Daring?",
            ),
            (
                "Q10",
                "int_feedback",
                "Seberapa puas Anda dengan kecepatan dan kejelasan umpan balik (feedback) dosen saat diskusi Luring di kelas?",
                "Seberapa puas Anda dengan kecepatan dan kejelasan umpan balik (feedback) dosen saat diskusi Daring di ruang virtual?",
            ),
            (
                "Q11",
                "int_peers",
                "Seberapa puas Anda dengan kualitas komunikasi dan diskusi kelompok bersama rekan kelas dalam pembelajaran Luring?",
                "Seberapa puas Anda dengan kualitas komunikasi dan diskusi kelompok bersama rekan kelas dalam pembelajaran Daring?",
            ),
            (
                "Q12",
                "int_focus",
                "Seberapa puas Anda dengan kemampuan menjaga fokus dan konsentrasi penuh selama mengikuti sesi pembelajaran Luring di ruang kelas?",
                "Seberapa puas Anda dengan kemampuan menjaga fokus dan konsentrasi penuh selama mengikuti sesi pembelajaran Daring dari jarak jauh?",
            ),
        ],
    ),
    (
        "Fleksibilitas & Kenyamanan Lingkungan",
        [
            (
                "Q13",
                "flx_time",
                "Seberapa puas Anda dengan keteraturan dan efisiensi pengaturan waktu pada metode pembelajaran Luring?",
                "Seberapa puas Anda dengan efisiensi waktu belajar dan penghematan waktu perjalanan pada metode pembelajaran Daring?",
            ),
            (
                "Q14",
                "flx_location",
                "Seberapa puas Anda dengan pelaksanaan perkuliahan Luring yang terpusat di ruang kelas kampus?",
                "Seberapa puas Anda dengan fleksibilitas lokasi belajar yang dapat diakses dari mana saja pada perkuliahan Daring?",
            ),
            (
                "Q15",
                "flx_comfort",
                "Seberapa puas Anda terhadap kenyamanan fisik ruang kelas dalam mendukung proses pembelajaran Luring?",
                "Seberapa puas Anda terhadap kenyamanan suasana ruang belajar mandiri dalam mendukung proses pembelajaran Daring?",
            ),
            (
                "Q16",
                "flx_pace",
                "Seberapa puas Anda dengan ritme dan kecepatan penyampaian materi secara langsung pada kelas Luring?",
                "Seberapa puas Anda dengan keleluasaan mengatur ritme belajar ulang (melalui rekaman/materi LMS) pada kelas Daring?",
            ),
        ],
    ),
    (
        "Dukungan Teknis & Kelancaran Operasional",
        [
            (
                "Q17",
                "tec_access",
                "Seberapa puas Anda dengan kemudahan mengakses bahan ajar cetak/papan tulis saat perkuliahan Luring berlangsung?",
                "Seberapa puas Anda dengan kemudahan mengunduh dan mengakses file materi digital pada platform LMS Daring?",
            ),
            (
                "Q18",
                "tec_stability",
                "Seberapa puas Anda dengan kelancaran jalannya perkuliahan Luring tanpa gangguan fasilitas ruang kelas (audio/proyektor)?",
                "Seberapa puas Anda dengan kelancaran jalannya perkuliahan Daring tanpa gangguan koneksi internet maupun kendala teknis aplikasi?",
            ),
            (
                "Q19",
                "tec_submission",
                "Seberapa puas Anda dengan mekanisme pengumpulan tugas dan pelaksanaan evaluasi secara langsung pada perkuliahan Luring?",
                "Seberapa puas Anda dengan mekanisme pengumpulan tugas dan pelaksanaan evaluasi berbasis sistem online pada perkuliahan Daring?",
            ),
            (
                "Q20",
                "tec_attendance",
                "Seberapa puas Anda dengan kejelasan prosedur presensi dan administrasi kehadiran pada perkuliahan Luring?",
                "Seberapa puas Anda dengan kejelasan prosedur presensi dan pencatatan kehadiran otomatis pada perkuliahan Daring?",
            ),
        ],
    ),
]
