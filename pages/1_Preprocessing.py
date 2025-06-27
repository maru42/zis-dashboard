# ==============================================================================
# File: pages/1_Preprocessing.py
# Simpan kode ini sebagai 1_Preprocessing.py di dalam folder 'pages'.
# ==============================================================================
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="Preprocessing Data", layout="wide")

st.title("🧹 Preprocessing & Cleaning Data")
st.markdown("Lakukan pembersihan, penanganan outlier, dan normalisasi data Anda di sini.")

if st.session_state.df is None:
    st.warning("Data belum diunggah. Silakan kembali ke halaman utama untuk mengunggah file Anda.")
    st.stop()

# --- STEP 1: PREPROCESSING & CLEANING ---
with st.expander("Langkah 1: Pembersihan Data Dasar", expanded=True):
    if st.button("🧼 Jalankan Cleaning"):
        with st.spinner("Membersihkan data..."):
            df_temp = st.session_state.df.copy()
            
            df_temp.columns = df_temp.columns.str.lower().str.replace(" ", "_")
            st.write("✅ Nama kolom diubah.")
            
            missing_before = df_temp.isnull().sum().sum()
            df_temp.fillna(0, inplace=True)
            st.write(f"✅ {missing_before} nilai hilang diganti dengan 0.")

            dup_count = df_temp.duplicated().sum()
            if dup_count > 0:
                df_temp = df_temp.drop_duplicates()
                st.warning(f"⚠️ {dup_count} data duplikat dihapus.")
            else:
                st.info("ℹ️ Tidak ada data duplikat.")
            
            st.session_state.df_processed = df_temp
            st.success("Pembersihan data dasar selesai!")
            st.dataframe(st.session_state.df_processed.head())

# --- STEP 2: OUTLIERS & FEATURE SELECTION ---
if st.session_state.df_processed is not None:
    with st.expander("Langkah 2: Penanganan Outlier & Seleksi Kolom (Opsional)"):
        df_current = st.session_state.df_processed.copy()

        # Outlier Handling
        st.subheader("Hapus Outlier")
        numeric_df = df_current.select_dtypes(include=np.number)
        if st.checkbox("Aktifkan penanganan outlier"):
            outlier_removed = numeric_df.copy()
            for col in numeric_df.columns:
                Q1 = numeric_df[col].quantile(0.25)
                Q3 = numeric_df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                outliers_count = ((numeric_df[col] < lower) | (numeric_df[col] > upper)).sum()
                if outliers_count > 0:
                    st.write(f"Kolom **{col}**: terdeteksi {outliers_count} outlier.")
                    outlier_removed = outlier_removed[(outlier_removed[col] >= lower) & (outlier_removed[col] <= upper)]
            
            if st.button("🗑️ Terapkan Penghapusan Outlier"):
                st.session_state.df_processed = df_current.loc[outlier_removed.index]
                st.success(f"Outlier berhasil dihapus!")
                st.dataframe(st.session_state.df_processed.head())
        
        # Drop Columns
        st.subheader("Hapus Kolom Tidak Relevan")
        all_cols = st.session_state.df_processed.columns.tolist()
        cols_to_drop = st.multiselect("Pilih kolom yang ingin dihapus:", all_cols)
        if st.button("❌ Hapus Kolom Terpilih"):
            st.session_state.df_processed.drop(columns=cols_to_drop, inplace=True)
            st.success("Kolom berhasil dihapus.")
            st.dataframe(st.session_state.df_processed.head())

    # --- STEP 3: NORMALIZATION ---
    with st.expander("Langkah 3: Normalisasi Data"):
        st.write("Menyamakan skala data numerik menggunakan StandardScaler.")
        if st.button("⚖️ Lakukan Normalisasi"):
            numeric_df_final = st.session_state.df_processed.select_dtypes(include=np.number)
            if not numeric_df_final.empty:
                scaler = StandardScaler()
                st.session_state.scaled_data = scaler.fit_transform(numeric_df_final)
                st.session_state.feature_names = numeric_df_final.columns.tolist()
                st.success("Data berhasil dinormalisasi!")
                st.write("Data setelah Normalisasi (5 baris pertama):")
                st.dataframe(pd.DataFrame(st.session_state.scaled_data, columns=st.session_state.feature_names).head())
            else:
                st.error("Tidak ada data numerik untuk dinormalisasi.")
else:
    st.info("Selesaikan langkah 'Pembersihan Data Dasar' terlebih dahulu.")
