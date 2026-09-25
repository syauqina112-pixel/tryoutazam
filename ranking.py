import pdfplumber
import pandas as pd
from tabulate import tabulate


# ==========================================
# KONFIGURASI
# ==========================================
FILE_PDF    = "nilai.pdf"
KOLOM_NILAI = "Nilai"
# ==========================================


def baca_pdf(path):
    """Membaca tabel dari PDF."""
    data = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            tabel = page.extract_table()
            if tabel:
                data.extend(tabel)
    if not data:
        raise ValueError("❌ Tabel tidak ditemukan di PDF.")
    df = pd.DataFrame(data[1:], columns=data[0])
    return df


def ranking(df, kolom_nilai):
    """Urutkan berdasarkan nilai tertinggi."""
    df[kolom_nilai] = pd.to_numeric(df[kolom_nilai], errors="coerce")
    df = df.dropna(subset=[kolom_nilai])
    df = df.sort_values(by=kolom_nilai, ascending=False).reset_index(drop=True)
    df.insert(0, "Peringkat", df.index + 1)
    return df


def tampilkan(df):
    print("\n" + "=" * 45)
    print("        🏆  HASIL PERANGKINGAN  🏆")
    print("=" * 45)
    print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
    print("\n✅ Selesai!\n")


if __name__ == "__main__":
    try:
        df = baca_pdf(FILE_PDF)
        df = ranking(df, KOLOM_NILAI)
        tampilkan(df)
    except FileNotFoundError:
        print(f"❌ File '{FILE_PDF}' tidak ditemukan.")
    except Exception as e:
        print(f"❌ Error: {e}")
