import pandas as pd

# Sesuaikan path dengan lokasi file kamu
df_penduduk = pd.read_csv("dataset\jml_penduduk_tingkat_sekolah_menengah_sma_usia_16__v1_data.csv")
df_sma = pd.read_csv("dataset\jml_sekolah_menengah_sma_brdsrkn_kategori_sekolah_v1_data.csv")
df_smk = pd.read_csv("dataset\jml_sekolah_menengah_kejuruan_smk_brdsrkn_kategori_v1_data.csv")

print("=" * 50)
print("KOLOM DI FILE PENDUDUK:")
print("=" * 50)
print(df_penduduk.columns.tolist())
print()
print("5 baris pertama:")
print(df_penduduk.head())

print()
print("=" * 50)
print("KOLOM DI FILE SMA:")
print("=" * 50)
print(df_sma.columns.tolist())
print()
print("5 baris pertama:")
print(df_sma.head())

print()
print("=" * 50)
print("KOLOM DI FILE SMK:")
print("=" * 50)
print(df_smk.columns.tolist())
print()
print("5 baris pertama:")
print(df_smk.head())
