import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import plotly.express as px

st.set_page_config(page_title="Modelling", layout="wide")

st.title("🤖 Pemodelan Clustering")
st.markdown("Tentukan jumlah cluster (K) yang optimal dan jalankan algoritma K-Means.")

if st.session_state.scaled_data is None:
    st.warning("Data belum dinormalisasi. Silakan selesaikan semua langkah di halaman 'Preprocessing' terlebih dahulu.")
    st.stop()

# --- STEP 4: DETERMINE K ---
with st.expander("Langkah 4: Tentukan Jumlah Cluster (K) Optimal", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Elbow Method")
        if st.button("📈 Jalankan Elbow Method"):
            with st.spinner("Menghitung inertia..."):
                distortions = []
                K_range = range(2, 11)
                for k in K_range:
                    km = KMeans(n_clusters=k, random_state=42, n_init='auto')
                    km.fit(st.session_state.scaled_data)
                    distortions.append(km.inertia_)
                
                fig = px.line(x=K_range, y=distortions, markers=True, labels={'x': 'Jumlah Cluster K', 'y': 'Inertia'})
                fig.update_layout(title="Elbow Method untuk Menentukan K")
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Silhouette Score")
        if st.button("📏 Hitung Silhouette Score"):
             with st.spinner("Menghitung score..."):
                scores = {}
                for k in range(2, 11):
                    model = KMeans(n_clusters=k, random_state=42, n_init='auto')
                    labels = model.fit_predict(st.session_state.scaled_data)
                    scores[k] = silhouette_score(st.session_state.scaled_data, labels)
                
                best_k = max(scores, key=scores.get)
                st.write("Skor Silhouette untuk setiap K:")
                st.json(scores)
                st.success(f"✅ K terbaik menurut Silhouette Score: **{best_k}**")

# --- STEP 5: K-MEANS CLUSTERING ---
with st.expander("Langkah 5: Jalankan Clustering", expanded=True):
    k_value = st.slider("Pilih nilai K final untuk clustering", 2, 10, 3, key="k_slider_final")
    
    if st.button("🚀 Jalankan K-Means Clustering"):
        with st.spinner("Membuat cluster..."):
            model = KMeans(n_clusters=k_value, random_state=42, n_init='auto')
            cluster_labels = model.fit_predict(st.session_state.scaled_data)
            
            # Save results to session state
            result_df = st.session_state.df_processed.copy()
            # Pastikan indeks direset jika ada outlier yang dihapus, agar sesuai dengan cluster_labels
            result_df = result_df.reset_index(drop=True)
            result_df['cluster'] = cluster_labels
            st.session_state.result_df = result_df
            st.session_state.model = model
            
            st.success(f"Clustering dengan K={k_value} berhasil! Silakan lihat hasilnya di halaman 'Hasil Analisis'.")
            st.dataframe(st.session_state.result_df.head())
