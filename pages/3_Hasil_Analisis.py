import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Hasil Analisis", layout="wide")

st.title("🎯 Hasil & Insight Clustering")
st.markdown("Visualisasikan dan interpretasikan hasil pengelompokan data Anda.")

if st.session_state.result_df is None:
    st.warning("Clustering belum dijalankan. Silakan jalankan model di halaman 'Modelling' terlebih dahulu.")
    st.stop()

# --- VISUALIZATION ---
st.markdown("### Visualisasi Hasil Clustering")
col_viz1, col_viz2 = st.columns(2)

with col_viz1:
    with st.container(border=True):
        st.subheader("Distribusi Cluster (PCA)")
        
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(st.session_state.scaled_data)
        
        pca_df = pd.DataFrame(pca_result, columns=["PC1", "PC2"])
        # Mengambil nilai cluster dan nama secara aman
        pca_df["Cluster"] = st.session_state.result_df['cluster'].values
        
        if 'nama' in st.session_state.result_df.columns:
            pca_df["Nama"] = st.session_state.result_df['nama'].values
        else:
            pca_df["Nama"] = "N/A"

        fig_pca = px.scatter(
            pca_df, x="PC1", y="PC2", color="Cluster", 
            title="Visualisasi Cluster (PCA)", hover_name="Nama",
            color_continuous_scale=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig_pca, use_container_width=True)

with col_viz2:
    with st.container(border=True):
        st.subheader("Karakteristik Cluster")
        model = st.session_state.model
        cluster_centers = model.cluster_centers_
        cluster_centers_df = pd.DataFrame(cluster_centers, columns=st.session_state.feature_names)
        
        fig_radar = go.Figure()
        for i in range(model.n_clusters):
            fig_radar.add_trace(go.Scatterpolar(
                r=cluster_centers_df.iloc[i].values,
                theta=cluster_centers_df.columns,
                fill='toself',
                name=f'Cluster {i}'
            ))
        fig_radar.update_layout(title="Perbandingan Rata-Rata Fitur per Cluster", showlegend=True)
        st.plotly_chart(fig_radar, use_container_width=True)

# --- DISPLAY DATA & DOWNLOAD ---
st.markdown("---")
st.subheader("Data Final dengan Label Cluster")
st.dataframe(st.session_state.result_df)

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df_to_csv(st.session_state.result_df)
st.download_button(
    label="📥 Download Hasil Clustering (CSV)",
    data=csv,
    file_name='hasil_clustering_zis.csv',
    mime='text/csv'
)
