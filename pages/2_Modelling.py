# ==============================================================================
# File: pages/2_Modelling.py
# Simpan kode ini sebagai 2_Modelling.py di dalam folder 'pages'.
# ==============================================================================
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import plotly.express as px

st.set_page_config(page_title="Modelling", layout="wide")

st.title("🤖 Pemodelan Clustering")
st.markdown("Tentukan jumlah cluster (K) yang optimal dan jalankan algoritma K-Means.")

# Validasi data sebelum memulai
if 'scaled_data' not in st.session_state or st.session_state.scaled_data is None:
    st.warning("Data belum dinormalisasi. Silakan selesaikan semua langkah di halaman 'Preprocessing' terlebih dahulu.")
    st.stop()

# Debug: Tampilkan dimensi data dan statistik
st.sidebar.subheader("🔍 Debug Info")
st.sidebar.write(f"Jumlah baris data: {st.session_state.scaled_data.shape[0]}")
st.sidebar.write(f"Jumlah fitur: {st.session_state.scaled_data.shape[1]}")

# Tampilkan statistik data scaled
scaled_df = pd.DataFrame(st.session_state.scaled_data)
st.sidebar.subheader("Statistik Data Scaled")
st.sidebar.write(scaled_df.describe())

# --- STEP 4: DETERMINE K ---
with st.expander("Langkah 4: Tentukan Jumlah Cluster (K) Optimal", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Elbow Method")
        if st.button("📈 Jalankan Elbow Method"):
            with st.spinner("Menghitung inertia..."):
                distortions = []
                K_range = range(2, 11)
                data_array = np.array(st.session_state.scaled_data)
                
                # Validasi data sebelum clustering
                if np.isnan(data_array).any() or np.isinf(data_array).any():
                    st.error("⚠️ Data mengandung nilai NaN atau Infinity! Silakan periksa kembali preprocessing data.")
                    st.stop()
                
                for k in K_range:
                    km = KMeans(n_clusters=k, 
                                init='k-means++',
                                random_state=42, 
                                n_init=20)  # Tambah n_init untuk stabilitas
                    km.fit(data_array)
                    distortions.append(km.inertia_)
                    st.write(f"K={k}: Inertia = {km.inertia_:.2f}")  # Tampilkan nilai inertia per K
                
                # Buat DataFrame untuk hasil yang lebih jelas
                results = pd.DataFrame({
                    'Jumlah Cluster (K)': K_range,
                    'Inertia': distortions
                })
                
                st.dataframe(results.style.format({'Inertia': '{:.2f}'}))
                
                # Plot hasil
                fig = px.line(
                    results, 
                    x='Jumlah Cluster (K)', 
                    y='Inertia', 
                    markers=True,
                    title="Elbow Method untuk Menentukan K"
                )
                fig.update_traces(line=dict(color='royalblue', width=3))
                fig.update_layout(
                    xaxis_title="Jumlah Cluster K",
                    yaxis_title="Inertia (WCSS)",
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Beri rekomendasi berdasarkan elbow
                if distortions[0] < distortions[1]:
                    st.warning("⚠️ Tren inertia meningkat! Ini tidak normal. Kemungkinan penyebab:")
                    st.markdown("""
                    - Data belum dinormalisasi dengan benar
                    - Terdapat outlier yang ekstrim
                    - Jumlah sampel terlalu sedikit
                    - Fitur yang tidak informatif
                    """)
                    st.markdown("**Solusi:** Periksa halaman preprocessing dan coba gunakan silhouette score.**")

    with col2:
        st.subheader("Silhouette Score")
        if st.button("📏 Hitung Silhouette Score"):
            with st.spinner("Menghitung score..."):
                scores = {}
                data_array = np.array(st.session_state.scaled_data)
                
                for k in range(2, 11):
                    model = KMeans(
                        n_clusters=k, 
                        init='k-means++',
                        random_state=42, 
                        n_init=20
                    )
                    labels = model.fit_predict(data_array)
                    
                    try:
                        score = silhouette_score(data_array, labels)
                        scores[k] = score
                    except ValueError:
                        st.error(f"Tidak dapat menghitung silhouette score untuk K={k}")
                        scores[k] = -1
                
                # Format hasil
                results = pd.DataFrame({
                    'Jumlah Cluster (K)': list(scores.keys()),
                    'Silhouette Score': list(scores.values())
                })
                
                st.dataframe(results.style.format({'Silhouette Score': '{:.4f}'}))
                
                # Cari K terbaik (abaikan nilai negatif)
                valid_scores = {k: v for k, v in scores.items() if v >= 0}
                if valid_scores:
                    best_k = max(valid_scores, key=valid_scores.get)
                    st.success(f"✅ K terbaik menurut Silhouette Score: **{best_k}** (Score: {scores[best_k]:.4f})")
                    
                    # Plot hasil
                    fig = px.bar(
                        results,
                        x='Jumlah Cluster (K)',
                        y='Silhouette Score',
                        title="Silhouette Score untuk Setiap K"
                    )
                    fig.update_traces(marker_color='#4CAF50')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Tidak dapat menghitung silhouette score untuk K manapun.")

# --- STEP 5: K-MEANS CLUSTERING ---
with st.expander("Langkah 5: Jalankan Clustering", expanded=True):
    st.markdown("### Pilih Nilai K")
    k_value = st.slider(
        "Pilih nilai K final untuk clustering", 
        2, 10, 3, 
        key="k_slider_final"
    )
    
    if st.button("🚀 Jalankan K-Means Clustering", key="run_clustering"):
        with st.spinner("Membuat cluster..."):
            # Konversi ke array numpy untuk konsistensi
            data_array = np.array(st.session_state.scaled_data)
            
            model = KMeans(
                n_clusters=k_value,
                init='k-means++',
                random_state=42,
                n_init=20
            )
            cluster_labels = model.fit_predict(data_array)
            
            # Pastikan hasil sesuai dengan data asli
            result_df = st.session_state.df_processed.copy()
            
            # Reset index jika ada perubahan jumlah baris
            if len(result_df) != len(cluster_labels):
                result_df = result_df.reset_index(drop=True)
            
            result_df['cluster'] = cluster_labels
            st.session_state.result_df = result_df
            st.session_state.model = model
            
            st.success(f"Clustering dengan K={k_value} berhasil! Silakan lihat hasilnya di halaman 'Hasil Analisis'.")
            
            # Tampilkan distribusi cluster
            cluster_dist = result_df['cluster'].value_counts().sort_index()
            cluster_dist_df = pd.DataFrame({
                'Cluster': cluster_dist.index,
                'Jumlah Sampel': cluster_dist.values
            })
            
            st.subheader("Distribusi Cluster")
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(cluster_dist_df)
            
            with col2:
                fig = px.pie(
                    cluster_dist_df,
                    values='Jumlah Sampel',
                    names='Cluster',
                    title=f"Distribusi Cluster (K={k_value})",
                    hole=0.3
                )
                st.plotly_chart(fig, use_container_width=True)

# Tampilkan data hasil clustering jika sudah ada
if 'result_df' in st.session_state:
    st.subheader("Preview Data Hasil Clustering")
    st.dataframe(st.session_state.result_df.head())