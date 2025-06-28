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
.metric-card .icon {
    font-size: 1.5rem;
    float: right;
    color: #6c757d;
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
    st.image("https://www.annabawi.org/wp-content/uploads/2022/12/cropped-Logo-web-Lazis-An-Nabawi-300x125.png", width=200)
    st.title("⚙️ Upload Data Anda")
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
st.markdown("Ringkasan data penerimaan Zakat, Infaq, dan Shadaqah.")
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

    if date_col_name:
        df_display['date'] = pd.to_datetime(df_display[date_col_name], errors='coerce')
        df_display['year'] = df_display['date'].dt.year
        df_display['month'] = df_display['date'].dt.month
        
        # --- Filter Tahun ---
        years = sorted(df_display['year'].dropna().unique().astype(int), reverse=True)
        selected_year = st.selectbox("Pilih Tahun:", years)
        
        # Filter dataframe berdasarkan tahun yang dipilih
        filtered_df = df_display[df_display['year'] == selected_year]
        
    else:
        # Jika tidak ada kolom tanggal, gunakan seluruh data
        st.warning("Kolom tanggal tidak ditemukan. Menampilkan data keseluruhan.")
        filtered_df = df_display
        selected_year = "Keseluruhan"


    # --- METRICS ROW ---
    st.subheader(f"Ringkasan Tahun {selected_year}")
    zakat_beras_col = "Jumlah Beras (Kg)"
    
    # Calculate metrics based on filtered data
    total_zakat_beras = 0
    if zakat_beras_col in filtered_df.columns:
        numeric_beras = pd.to_numeric(filtered_df[zakat_beras_col], errors='coerce')
        total_zakat_beras = numeric_beras.sum()

    numeric_cols = filtered_df.select_dtypes(include=np.number)
    if zakat_beras_col in numeric_cols.columns:
        numeric_cols_money = numeric_cols.drop(columns=[zakat_beras_col])
    else:
        numeric_cols_money = numeric_cols
        
    # Hapus kolom 'year' dan 'month' dari perhitungan donasi
    if 'year' in numeric_cols_money.columns:
        numeric_cols_money = numeric_cols_money.drop(columns=['year'])
    if 'month' in numeric_cols_money.columns:
        numeric_cols_money = numeric_cols_money.drop(columns=['month'])

    total_donasi_uang = numeric_cols_money.sum().sum()
    jumlah_transaksi = len(filtered_df)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="card metric-card">
            <span class="icon">💰</span><h3>Total Donasi Uang</h3><p>Rp {total_donasi_uang:,.0f}</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="card metric-card">
            <span class="icon">🌾</span><h3>Total Zakat Beras</h3><p>{total_zakat_beras:,.1f} Kg</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="card metric-card">
            <span class="icon">🔄</span><h3>Jumlah Transaksi</h3><p>{jumlah_transaksi}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRAFIK ROW ---
    if date_col_name:
        st.subheader("Grafik Penerimaan Bulanan")
        graph_col1, graph_col2 = st.columns(2)

        with graph_col1:
            # Grafik Donasi Uang
            money_by_month = numeric_cols_money.groupby(filtered_df['month']).sum().sum(axis=1).reset_index(name='total_uang')
            fig_money = px.line(money_by_month, x='month', y='total_uang', markers=True,
                                title=f"Tren Donasi Uang Tahun {selected_year}")
            fig_money.update_layout(xaxis_title="Bulan", yaxis_title="Total Donasi (Rp)")
            st.plotly_chart(fig_money, use_container_width=True)
        
        with graph_col2:
            # Grafik Donasi Beras
            rice_by_month = filtered_df.groupby('month')[zakat_beras_col].sum().reset_index()
            fig_rice = px.line(rice_by_month, x='month', y=zakat_beras_col, markers=True,
                               title=f"Tren Zakat Beras Tahun {selected_year}", color_discrete_sequence=['green'])
            fig_rice.update_layout(xaxis_title="Bulan", yaxis_title="Jumlah Beras (Kg)")
            st.plotly_chart(fig_rice, use_container_width=True)

    st.markdown("---")
    st.subheader("Pratinjau Data")
    st.dataframe(filtered_df.head())

else:
    st.info("Silakan unggah file Excel di sidebar untuk memulai analisis.")
