import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Dashboard ZIS | Overview",
    page_icon="📊",
    layout="wide"
)

# --- CUSTOM CSS FOR LIGHT MODE ---
st.markdown("""
<style>
/* General Body Styles */
body {
    background-color: #f0f2f6; /* Light grey background */
}

/* Main container styling */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

/* Card Styling */
.card {
    background-color: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease-in-out;
    height: 100%;
}
.card:hover {
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

/* Metric Card Styling */
.metric-card h3 {
    font-size: 1.1rem;
    color: #6c757d;
    margin-bottom: 8px;
    font-weight: 400;
}
.metric-card p {
    font-size: 2.2rem;
    font-weight: 600;
    color: #1E293B;
    margin-bottom: 8px;
}
.metric-card span {
    font-size: 1rem;
    color: #28a745;
}
.metric-card span.red {
    color: #dc3545;
}


/* Header styling */
h1, h2, h3, h4 { color: #1E293B; }

/* Button styling */
div.stButton > button {
    background-color: #0068c9;
    color: white;
    border-radius: 8px;
    padding: 10px 20px;
    border: none;
    font-weight: 500;
}
div.stButton > button:hover {
    background-color: #0055a8;
}
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'df' not in st.session_state:
    st.session_state.df = None
if 'df_processed' not in st.session_state:
    st.session_state.df_processed = None
if 'scaled_data' not in st.session_state:
    st.session_state.scaled_data = None
if 'result_df' not in st.session_state:
    st.session_state.result_df = None
if 'model' not in st.session_state:
    st.session_state.model = None

# --- SIDEBAR FOR UPLOAD ---
with st.sidebar:
    st.title("Upload Data Anda")
    uploaded_file = st.file_uploader("📤 Upload file Excel Rekapitulasi ZIS", type=["xlsx"])
    
    if uploaded_file:
        if st.session_state.df is None or not st.session_state.df.equals(pd.read_excel(uploaded_file)):
            st.session_state.df = pd.read_excel(uploaded_file)
            st.session_state.df_processed = None
            st.session_state.scaled_data = None
            st.session_state.result_df = None
            st.session_state.model = None
            st.success("File berhasil diunggah!")

# --- HOMEPAGE CONTENT ---
st.title("Dashboard Overview ZIS")
st.markdown("Selamat datang! Halaman ini menampilkan ringkasan data awal dari file yang Anda unggah.")
st.markdown("---")

if st.session_state.df is not None:
    df_display = st.session_state.df.copy()
    
    # Mencari kolom tanggal yang mungkin (misal: 'tanggal', 'waktu', 'date')
    date_col_name = None
    possible_date_cols = ['tanggal', 'tgl', 'date', 'waktu_transaksi', 'waktu']
    for col in df_display.columns:
        if col.lower() in possible_date_cols:
            date_col_name = col
            break

    # Filter Tahun (ditempatkan di atas untuk mengontrol semua elemen di bawahnya)
    if date_col_name:
        df_display['date'] = pd.to_datetime(df_display[date_col_name], errors='coerce')
        df_display.dropna(subset=['date'], inplace=True) # Hapus baris yang tanggalnya tidak valid
        df_display['year'] = df_display['date'].dt.year
        
        years = sorted(df_display['year'].dropna().unique().astype(int), reverse=True)
        # Menambahkan opsi "Semua Data"
        filter_options = ["Semua Data"] + years
        selected_option = st.selectbox("Pilih Periode:", filter_options)
        
        if selected_option == "Semua Data":
            filtered_df = df_display
            display_period = "Semua Data"
        else:
            filtered_df = df_display[df_display['year'] == selected_option]
            display_period = f"Tahun {selected_option}"

    else:
        st.warning("Kolom tanggal tidak ditemukan. Menampilkan data keseluruhan.")
        filtered_df = df_display
        display_period = "Keseluruhan"


    # --- METRICS ROW ---
    st.subheader(f"Ringkasan Periode {display_period}")
    zakat_beras_col = "Jumlah Beras (Kg)"
    
    # Calculate metrics based on filtered data
    total_zakat_beras = 0
    if zakat_beras_col in filtered_df.columns:
        numeric_beras = pd.to_numeric(filtered_df[zakat_beras_col], errors='coerce')
        total_zakat_beras = numeric_beras.sum()

    numeric_cols = filtered_df.select_dtypes(include=np.number)
    
    # Daftar kolom yang bukan donasi uang untuk dikecualikan
    cols_to_exclude = [zakat_beras_col, 'year']
    if 'month' in filtered_df.columns:
        cols_to_exclude.append('month')
        
    money_cols = numeric_cols.drop(columns=[col for col in cols_to_exclude if col in numeric_cols.columns])
    total_donasi_uang = money_cols.sum().sum()
    jumlah_transaksi = len(filtered_df)
    rata_donasi = money_cols.sum(axis=1).mean() if not money_cols.empty else 0


    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="card metric-card">
            <h3>Total Donasi Uang</h3><p>Rp {total_donasi_uang:,.0f}</p><span>Terkumpul</span>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="card metric-card">
            <h3>Jumlah Transaksi</h3><p>{jumlah_transaksi}</p><span>Tercatat</span>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="card metric-card">
            <h3>Total Zakat Beras</h3><p>{total_zakat_beras:,.1f}</p><span>Kg</span>
        </div>""", unsafe_allow_html=True)
    with col4:
         st.markdown(f"""
        <div class="card metric-card">
            <h3>Rata-Rata Donasi Uang</h3><p>Rp {rata_donasi:,.0f}</p><span>per Transaksi</span>
        </div>""", unsafe_allow_html=True)


    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRAFIK ROW ---
    if date_col_name:
        st.subheader(f"Grafik Penerimaan Bulanan - {display_period}")
        
        # Menambahkan kolom nama bulan untuk plotting
        filtered_df['month_name'] = filtered_df['date'].dt.strftime('%b')
        # Urutkan bulan dengan benar
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        filtered_df['month_name'] = pd.Categorical(filtered_df['month_name'], categories=month_order, ordered=True)
        
        graph_col1, graph_col2 = st.columns(2)

        with graph_col1:
            # Grup data uang per bulan
            money_cols_list = money_cols.columns.tolist()
            monthly_money = filtered_df.groupby('month_name', observed=False)[money_cols_list].sum().sum(axis=1).reset_index(name='total_uang')
            
            fig_money = px.bar(monthly_money, x='month_name', y='total_uang', title="Total Donasi Uang per Bulan")
            fig_money.update_layout(xaxis_title="Bulan", yaxis_title="Total Donasi (Rp)")
            st.plotly_chart(fig_money, use_container_width=True)
        
        with graph_col2:
            # Grup data beras per bulan
            if zakat_beras_col in filtered_df.columns:
                monthly_rice = filtered_df.groupby('month_name', observed=False)[zakat_beras_col].sum().reset_index()
                fig_rice = px.bar(monthly_rice, x='month_name', y=zakat_beras_col, title="Total Zakat Beras per Bulan", color_discrete_sequence=['#28a745'])
                fig_rice.update_layout(xaxis_title="Bulan", yaxis_title="Jumlah Beras (Kg)")
                st.plotly_chart(fig_rice, use_container_width=True)
            else:
                st.info(f"Kolom '{zakat_beras_col}' tidak ditemukan untuk membuat grafik beras.")

    st.markdown("---")
    st.subheader("Pratinjau Data (Sesuai Filter)")
    st.dataframe(filtered_df.head())

else:
    st.info("Silakan unggah file Excel di sidebar untuk memulai analisis.")
