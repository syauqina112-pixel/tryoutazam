import pdfplumber
import pandas as pd
from tabulate import tabulate
import re


# ==========================================
# KONFIGURASI
# ==========================================
FILE_PDF = [
    "BISMILLAH UTBK 2027 TO 2.pdf",   # tambah file lain di sini
    # "BISMILLAH UTBK 2027 TO 1.pdf",
]
# ==========================================


def parse_baris(teks):
    """Parsing 1 baris data siswa."""
    teks = teks.strip()
    pola = r"^(\d+)([A-Za-z\.\'\s\-]+?)(12[A-C])((?:\s*\d+)*)$"
    cocok = re.match(pola, teks)
    if not cocok:
        return None
    no, nama, kelas, sisa = cocok.groups()
    nilai = [int(x) for x in sisa.split()] if sisa.strip() else []
    return int(no), nama.strip(), kelas, nilai


def baca_semua_pdf(file_list):
    """Baca semua PDF, return dict: {nama: {kelas, nilai[]}}."""
    data_siswa = {}
    for path in file_list:
        print(f"📄 Membaca: {path}")
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                teks = page.extract_text() or ""
                for baris in teks.split("\n"):
                    hasil = parse_baris(baris)
                    if not hasil:
                        continue
                    no, nama, kelas, nilai = hasil
                    if nama not in data_siswa:
                        data_siswa[nama] = {"kelas": kelas, "nilai": []}
                    data_siswa[nama]["nilai"].extend(nilai)
    return data_siswa


def buat_dataframe(data_siswa):
    """Ubah dict jadi DataFrame + hitung total."""
    baris = []
    for nama, info in data_siswa.items():
        nilai = info["nilai"]
        total = sum(nilai) if nilai else 0
        baris.append({
            "Nama": nama,
            "Kelas": info["kelas"],
            "Nilai": ", ".join(map(str, nilai)) if nilai else "-",
            "Total": total,
        })
    df = pd.DataFrame(baris)
    df = df.sort_values(by="Total", ascending=False).reset_index(drop=True)
    df.insert(0, "Peringkat", df.index + 1)
    return df


def tampilkan(df):
    print("\n" + "=" * 80)
    print("             🏆  HASIL PERANGKINGAN UTBK 2027  🏆")
    print("=" * 80)
    print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
    print(f"\n✅ Total siswa: {len(df)}\n")


if __name__ == "__main__":
    try:
        data = baca_semua_pdf(FILE_PDF)
        if not data:
            print("❌ Tidak ada data siswa yang terbaca.")
        else:
            df = buat_dataframe(data)
            tampilkan(df)
            df.to_excel("hasil_ranking.xlsx", index=False)
            print("💾 Hasil disimpan ke: hasil_ranking.xlsx")
    except FileNotFoundError as e:
        print(f"❌ File tidak ditemukan: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
