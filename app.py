import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

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

/* To-Do List Styling */
.todo-item {
    display: flex;
    align-items: center;
    padding: 12px;
    background-color: #f8f9fa;
    border-radius: 10px;
    margin-bottom: 10px;
    border: 1px solid #dee2e6;
}
.todo-item .icon {
    font-size: 1.5rem;
    margin-right: 15px;
    color: #0068c9;
}
.todo-item .text {
    color: #495057;
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
st.title("Selamat Datang di Dashboard Analisis ZIS")
st.markdown("Berikut ringkasan data awal dari file yang Anda unggah.")
st.markdown("---")

if st.session_state.df is not None:
    main_col1, main_col2 = st.columns([2.5, 1])

    with main_col1:
        # --- METRICS ROW ---
        df_display = st.session_state.df.copy()
        zakat_beras_col = "Jumlah Beras (Kg)"
        
        # Calculate metrics
        total_zakat_beras = 0
        if zakat_beras_col in df_display.columns:
            numeric_beras = pd.to_numeric(df_display[zakat_beras_col], errors='coerce')
            total_zakat_beras = numeric_beras.sum()

        numeric_cols = df_display.select_dtypes(include=np.number)
        if zakat_beras_col in numeric_cols.columns:
            numeric_cols_money = numeric_cols.drop(columns=[zakat_beras_col])
        else:
            numeric_cols_money = numeric_cols
        total_donasi_uang = numeric_cols_money.sum().sum()
        
        jumlah_transaksi = len(df_display)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="card metric-card">
                <span class="icon">💰</span>
                <h3>Total Donasi Uang</h3>
                <p>Rp {total_donasi_uang:,.0f}</p>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="card metric-card">
                <span class="icon">🌾</span>
                <h3>Total Zakat Beras</h3>
                <p>{total_zakat_beras:,.1f} Kg</p>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="card metric-card">
                <span class="icon">🔄</span>
                <h3>Jumlah Transaksi</h3>
                <p>{jumlah_transaksi}</p>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- LINE CHART ---
        st.markdown("<h4>Grafik Donasi Harian (Contoh)</h4>", unsafe_allow_html=True)
        with st.container():
            # Membuat data dummy untuk visualisasi
            chart_data = pd.DataFrame({
                "Tanggal": pd.to_datetime(pd.date_range("2024-06-01", periods=14, freq="D")),
                "Donasi (Rp)": np.random.randint(1000000, 5000000, size=14)
            })
            
            fig = px.line(chart_data, x='Tanggal', y='Donasi (Rp)', markers=True,
                          title="Tren Penerimaan Donasi 14 Hari Terakhir")
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_color='#1E293B',
                xaxis_gridcolor='#e0e0e0',
                yaxis_gridcolor='#e0e0e0'
            )
            st.plotly_chart(fig, use_container_width=True)


    with main_col2:
        # --- TO-DO LIST ---
        st.markdown("<h4>Langkah Analisis Anda</h4>", unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <div class="todo-item">
                <span class="icon">1️⃣</span>
                <span class="text">Lakukan Preprocessing untuk membersihkan data.</span>
            </div>
            <div class="todo-item">
                <span class="icon">2️⃣</span>
                <span class="text">Buat model clustering di halaman Modelling.</span>
            </div>
            <div class="todo-item">
                <span class="icon">3️⃣</span>
                <span class="text">Lihat hasil dan insight dari cluster yang terbentuk.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- DATA PREVIEW ---
        st.markdown("<h4>Pratinjau Data</h4>", unsafe_allow_html=True)
        with st.container():
            st.dataframe(st.session_state.df.head(5), use_container_width=True)

else:
    st.info("Silakan unggah file Excel di sidebar untuk memulai analisis.")
