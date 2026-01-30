import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Pendidikan Jawa Barat",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    
    df_penduduk = pd.read_csv("dataset\jml_penduduk_tingkat_sekolah_menengah_sma_usia_16__v1_data.csv")
    df_sma = pd.read_csv("dataset\jml_sekolah_menengah_kejuruan_smk_brdsrkn_kategori_v1_data.csv")
    df_smk = pd.read_csv("dataset\jml_sekolah_menengah_sma_brdsrkn_kategori_sekolah_v1_data.csv ")
    
    df_penduduk = df_penduduk.rename(columns={'jumlah_penduduk': 'jumlah'})
    df_sma = df_sma.rename(columns={'jumlah_sekolah': 'jumlah', 'kategori_sekolah': 'kategori'})
    df_smk = df_smk.rename(columns={'jumlah_sekolah': 'jumlah', 'kategori_sekolah': 'kategori'})
    
    def extract_tahun_awal(tahun_value):
        tahun_str = str(tahun_value)
        if '/' in tahun_str:
            tahun_str = tahun_str.split('/')[0]
        return int(tahun_str.strip())
    
    df_sma['tahun_ajaran_asli'] = df_sma['tahun_ajaran'].astype(str)
    df_sma['tahun'] = df_sma['tahun_ajaran'].apply(extract_tahun_awal)
    
    df_smk['tahun_ajaran_asli'] = df_smk['tahun_ajaran'].astype(str)
    df_smk['tahun'] = df_smk['tahun_ajaran'].apply(extract_tahun_awal)
    
    df_penduduk['tahun'] = df_penduduk['tahun'].astype(int)
    
    return df_penduduk, df_sma, df_smk

df_penduduk, df_sma, df_smk = load_data()

def prepare_metadata(df_penduduk, df_sma, df_smk):
    
    tahun_penduduk = set(df_penduduk['tahun'].unique())
    tahun_sma = set(df_sma['tahun'].unique())
    tahun_smk = set(df_smk['tahun'].unique())
    
    tahun_lengkap = sorted(tahun_penduduk & tahun_sma & tahun_smk)
    tahun_sekolah = sorted(tahun_sma & tahun_smk)
    wilayah_list = sorted(df_sma['nama_kabupaten_kota'].unique())
    
    return {
        'tahun_lengkap': tahun_lengkap,
        'tahun_sekolah': tahun_sekolah,
        'tahun_penduduk': sorted(tahun_penduduk),
        'wilayah': wilayah_list
    }

metadata = prepare_metadata(df_penduduk, df_sma, df_smk)

with st.sidebar:
    
    st.header("Filter Data")
    st.divider()
    
    st.subheader("Tahun Analisis")
    
    if len(metadata['tahun_lengkap']) > 0:
        selected_tahun = st.selectbox(
            label="Pilih Tahun",
            options=metadata['tahun_lengkap'],
            index=len(metadata['tahun_lengkap']) - 1
        )
    else:
        st.warning("Tidak ada tahun yang cocok di semua dataset")
        selected_tahun = metadata['tahun_sekolah'][-1] if metadata['tahun_sekolah'] else 2024
    
    st.caption(
        f"Tahun tersedia: Penduduk ({min(metadata['tahun_penduduk'])}-{max(metadata['tahun_penduduk'])}), "
        f"Sekolah ({min(metadata['tahun_sekolah'])}-{max(metadata['tahun_sekolah'])})"
    )
    
    st.subheader("Wilayah")
    
    select_all_wilayah = st.checkbox("Pilih Semua Wilayah", value=True)
    
    if select_all_wilayah:
        selected_wilayah = metadata['wilayah']
    else:
        selected_wilayah = st.multiselect(
            label="Pilih Kabupaten/Kota",
            options=metadata['wilayah'],
            default=metadata['wilayah'][:5]
        )
    
    st.divider()
    st.caption(f"Tahun: {selected_tahun} | Wilayah: {len(selected_wilayah)} kab/kota")

def filter_data(df_penduduk, df_sma, df_smk, tahun, wilayah):
    
    df_pop = df_penduduk[
        (df_penduduk['tahun'] == tahun) &
        (df_penduduk['nama_kabupaten_kota'].isin(wilayah))
    ].copy()
    
    df_sma_filtered = df_sma[df_sma['nama_kabupaten_kota'].isin(wilayah)].copy()
    df_smk_filtered = df_smk[df_smk['nama_kabupaten_kota'].isin(wilayah)].copy()
    
    return df_pop, df_sma_filtered, df_smk_filtered

df_pop_filtered, df_sma_filtered, df_smk_filtered = filter_data(
    df_penduduk, df_sma, df_smk, selected_tahun, selected_wilayah
)

st.title("Dashboard Pendidikan Jawa Barat")
st.markdown("Analisis ketersediaan sekolah SMA dan SMK berdasarkan populasi penduduk usia 16-18 tahun.")
st.caption(f"Tahun {selected_tahun} merujuk ke tahun ajaran {selected_tahun}/{selected_tahun+1}")
st.divider()

def calculate_kpi(df_pop, df_sma, df_smk, tahun):
    
    total_penduduk = df_pop['jumlah'].sum()
    
    total_sma = df_sma[df_sma['tahun'] == tahun]['jumlah'].sum()
    total_smk = df_smk[df_smk['tahun'] == tahun]['jumlah'].sum()
    total_sekolah = total_sma + total_smk
    
    sma_tahun = df_sma[df_sma['tahun'] == tahun]
    smk_tahun = df_smk[df_smk['tahun'] == tahun]
    
    sma_negeri = sma_tahun[sma_tahun['kategori'] == 'Negeri']['jumlah'].sum()
    sma_swasta = sma_tahun[sma_tahun['kategori'] == 'Swasta']['jumlah'].sum()
    smk_negeri = smk_tahun[smk_tahun['kategori'] == 'Negeri']['jumlah'].sum()
    smk_swasta = smk_tahun[smk_tahun['kategori'] == 'Swasta']['jumlah'].sum()
    
    total_negeri = sma_negeri + smk_negeri
    total_swasta = sma_swasta + smk_swasta
    total_all = total_negeri + total_swasta
    
    persen_swasta = (total_swasta / total_all * 100) if total_all > 0 else 0
    rasio = total_penduduk / total_sekolah if total_sekolah > 0 else 0
    
    return {
        'penduduk': total_penduduk,
        'sma': total_sma,
        'smk': total_smk,
        'total_sekolah': total_sekolah,
        'negeri': total_negeri,
        'swasta': total_swasta,
        'persen_swasta': persen_swasta,
        'rasio': rasio
    }

kpi = calculate_kpi(df_pop_filtered, df_sma_filtered, df_smk_filtered, selected_tahun)

st.subheader(f"Ringkasan Data Tahun {selected_tahun}")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(label="Penduduk Usia SMA", value=f"{kpi['penduduk']:,.0f}")

with col2:
    st.metric(label="Jumlah SMA", value=f"{kpi['sma']:,.0f}")

with col3:
    st.metric(label="Jumlah SMK", value=f"{kpi['smk']:,.0f}")

with col4:
    st.metric(label="Rasio Siswa/Sekolah", value=f"{kpi['rasio']:,.0f}")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "Trend Sekolah",
    "Analisis Rasio",
    "Detail Wilayah",
    "Download Data"
])

with tab1:
    st.subheader("Trend Pertumbuhan Sekolah")
    
    if metadata['tahun_sekolah']:
        tahun_min = min(metadata['tahun_sekolah'])
        tahun_max = max(metadata['tahun_sekolah'])
        st.caption(f"Data: Tahun Ajaran {tahun_min}/{tahun_min+1} sampai {tahun_max}/{tahun_max+1}")
    
    def prepare_trend_data(df_sma, df_smk, wilayah):
        sma = df_sma[df_sma['nama_kabupaten_kota'].isin(wilayah)].copy()
        smk = df_smk[df_smk['nama_kabupaten_kota'].isin(wilayah)].copy()
        
        sma_trend = sma.groupby('tahun')['jumlah'].sum().reset_index()
        sma_trend['jenis'] = 'SMA'
        
        smk_trend = smk.groupby('tahun')['jumlah'].sum().reset_index()
        smk_trend['jenis'] = 'SMK'
        
        return pd.concat([sma_trend, smk_trend], ignore_index=True)
    
    trend_data = prepare_trend_data(df_sma, df_smk, selected_wilayah)
    
    if not trend_data.empty:
        fig_trend = px.line(
            trend_data,
            x='tahun',
            y='jumlah',
            color='jenis',
            markers=True,
            title='Jumlah Sekolah per Tahun',
            labels={'tahun': 'Tahun', 'jumlah': 'Jumlah Sekolah', 'jenis': 'Jenis Sekolah'},
            color_discrete_map={'SMA': '#3498db', 'SMK': '#2ecc71'}
        )
        fig_trend.update_layout(xaxis=dict(dtick=1), hovermode='x unified')
        st.plotly_chart(fig_trend, use_container_width=True)
    
    st.subheader("Komposisi Negeri vs Swasta")
    
    def prepare_kategori_trend(df_sma, df_smk, wilayah):
        sma = df_sma[df_sma['nama_kabupaten_kota'].isin(wilayah)].copy()
        smk = df_smk[df_smk['nama_kabupaten_kota'].isin(wilayah)].copy()
        combined = pd.concat([sma, smk], ignore_index=True)
        return combined.groupby(['tahun', 'kategori'])['jumlah'].sum().reset_index()
    
    kategori_trend = prepare_kategori_trend(df_sma, df_smk, selected_wilayah)
    
    if not kategori_trend.empty:
        fig_kategori = px.bar(
            kategori_trend,
            x='tahun',
            y='jumlah',
            color='kategori',
            title='Jumlah Sekolah: Negeri vs Swasta',
            labels={'tahun': 'Tahun', 'jumlah': 'Jumlah Sekolah', 'kategori': 'Kategori'},
            color_discrete_map={'Negeri': '#2c3e50', 'Swasta': '#95a5a6'},
            barmode='stack'
        )
        fig_kategori.update_layout(xaxis=dict(dtick=1))
        st.plotly_chart(fig_kategori, use_container_width=True)

with tab2:
    st.subheader(f"Analisis Rasio Siswa per Sekolah (Tahun {selected_tahun})")
    
    rasio_data = pd.DataFrame()
    
    if selected_tahun not in metadata['tahun_penduduk']:
        st.warning(f"Data penduduk tahun {selected_tahun} tidak tersedia.")
    else:
        def kategorikan_rasio(rasio):
            if rasio < 500:
                return 'Sangat Baik'
            elif rasio < 768:
                return 'Cukup'
            elif rasio < 1000:
                return 'Perlu Perhatian'
            else:
                return 'Kritis'
        
        def calculate_rasio_per_wilayah(df_pop, df_sma, df_smk, tahun):
            pop_agg = df_pop.groupby('nama_kabupaten_kota')['jumlah'].sum().reset_index()
            pop_agg.columns = ['wilayah', 'penduduk']
            
            sma = df_sma[df_sma['tahun'] == tahun].copy()
            smk = df_smk[df_smk['tahun'] == tahun].copy()
            
            sma_agg = sma.groupby('nama_kabupaten_kota')['jumlah'].sum().reset_index()
            sma_agg.columns = ['wilayah', 'sma']
            
            smk_agg = smk.groupby('nama_kabupaten_kota')['jumlah'].sum().reset_index()
            smk_agg.columns = ['wilayah', 'smk']
            
            result = pop_agg.merge(sma_agg, on='wilayah', how='left')
            result = result.merge(smk_agg, on='wilayah', how='left')
            result = result.fillna(0)
            
            result['total_sekolah'] = result['sma'] + result['smk']
            result['rasio'] = result['penduduk'] / result['total_sekolah']
            result['rasio'] = result['rasio'].replace([float('inf')], 0)
            result['status'] = result['rasio'].apply(kategorikan_rasio)
            result = result.sort_values('rasio', ascending=False)
            
            return result
        
        rasio_data = calculate_rasio_per_wilayah(
            df_pop_filtered, df_sma_filtered, df_smk_filtered, selected_tahun
        )
        
        if not rasio_data.empty:
            color_map = {
                'Sangat Baik': '#27ae60',
                'Cukup': '#3498db',
                'Perlu Perhatian': '#f39c12',
                'Kritis': '#e74c3c'
            }
            
            fig_rasio = px.bar(
                rasio_data,
                y='wilayah',
                x='rasio',
                color='status',
                orientation='h',
                title=f'Rasio Penduduk per Sekolah (Tahun {selected_tahun})',
                labels={'wilayah': 'Kabupaten/Kota', 'rasio': 'Rasio', 'status': 'Status'},
                color_discrete_map=color_map,
                category_orders={'status': ['Kritis', 'Perlu Perhatian', 'Cukup', 'Sangat Baik']}
            )
            
            fig_rasio.add_vline(x=768, line_dash="dash", line_color="red", annotation_text="Batas Ideal (768)")
            fig_rasio.update_layout(
                height=max(400, len(rasio_data) * 25),
                yaxis={'categoryorder': 'total ascending'}
            )
            
            st.plotly_chart(fig_rasio, use_container_width=True)
            

with tab3:
    st.subheader("Detail per Wilayah")
    
    if len(selected_wilayah) > 0:
        selected_detail_wilayah = st.selectbox(
            "Pilih Kabupaten/Kota",
            options=selected_wilayah,
            key="detail_wilayah"
        )
        
        detail_pop = df_pop_filtered[df_pop_filtered['nama_kabupaten_kota'] == selected_detail_wilayah]
        detail_sma = df_sma_filtered[df_sma_filtered['nama_kabupaten_kota'] == selected_detail_wilayah]
        detail_smk = df_smk_filtered[df_smk_filtered['nama_kabupaten_kota'] == selected_detail_wilayah]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Penduduk Usia SMA", f"{detail_pop['jumlah'].sum():,.0f}")
        
        with col2:
            sma_total = detail_sma[detail_sma['tahun'] == selected_tahun]['jumlah'].sum()
            st.metric("Jumlah SMA", f"{sma_total:,.0f}")
        
        with col3:
            smk_total = detail_smk[detail_smk['tahun'] == selected_tahun]['jumlah'].sum()
            st.metric("Jumlah SMK", f"{smk_total:,.0f}")
        
        st.markdown("---")
        st.markdown("**Komposisi Negeri vs Swasta**")
        
        col_pie1, col_pie2 = st.columns(2)
        
        with col_pie1:
            sma_by_kat = detail_sma[detail_sma['tahun'] == selected_tahun].groupby('kategori')['jumlah'].sum()
            if not sma_by_kat.empty:
                fig_pie_sma = px.pie(
                    values=sma_by_kat.values,
                    names=sma_by_kat.index,
                    title=f'SMA di {selected_detail_wilayah}',
                    color_discrete_map={'Negeri': '#2c3e50', 'Swasta': '#95a5a6'}
                )
                st.plotly_chart(fig_pie_sma, use_container_width=True)
            else:
                st.info("Data SMA tidak tersedia")
        
        with col_pie2:
            smk_by_kat = detail_smk[detail_smk['tahun'] == selected_tahun].groupby('kategori')['jumlah'].sum()
            if not smk_by_kat.empty:
                fig_pie_smk = px.pie(
                    values=smk_by_kat.values,
                    names=smk_by_kat.index,
                    title=f'SMK di {selected_detail_wilayah}',
                    color_discrete_map={'Negeri': '#2c3e50', 'Swasta': '#95a5a6'}
                )
                st.plotly_chart(fig_pie_smk, use_container_width=True)
            else:
                st.info("Data SMK tidak tersedia")
        
        st.markdown("---")
        st.markdown(f"**Trend Sekolah di {selected_detail_wilayah}**")
        
        sma_trend_detail = detail_sma.groupby('tahun')['jumlah'].sum().reset_index()
        sma_trend_detail['jenis'] = 'SMA'
        
        smk_trend_detail = detail_smk.groupby('tahun')['jumlah'].sum().reset_index()
        smk_trend_detail['jenis'] = 'SMK'
        
        trend_detail = pd.concat([sma_trend_detail, smk_trend_detail])
        
        if not trend_detail.empty:
            fig_trend_detail = px.line(
                trend_detail,
                x='tahun',
                y='jumlah',
                color='jenis',
                markers=True,
                title=f'Pertumbuhan Sekolah di {selected_detail_wilayah}',
                color_discrete_map={'SMA': '#3498db', 'SMK': '#2ecc71'}
            )
            fig_trend_detail.update_layout(xaxis=dict(dtick=1))
            st.plotly_chart(fig_trend_detail, use_container_width=True)
    else:
        st.warning("Pilih minimal satu wilayah di sidebar")

with tab4:
    st.subheader("Download Data")
    
    @st.cache_data
    def convert_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Data Rasio per Wilayah**")
        if len(rasio_data) > 0:
            st.download_button(
                label="Download Rasio.csv",
                data=convert_to_csv(rasio_data),
                file_name=f"rasio_wilayah_{selected_tahun}.csv",
                mime="text/csv"
            )
        else:
            st.caption("Data tidak tersedia")
    
    with col2:
        st.markdown("**Data SMA**")
        st.download_button(
            label="Download SMA.csv",
            data=convert_to_csv(df_sma_filtered),
            file_name=f"sma_{selected_tahun}.csv",
            mime="text/csv"
        )
    
    with col3:
        st.markdown("**Data SMK**")
        st.download_button(
            label="Download SMK.csv",
            data=convert_to_csv(df_smk_filtered),
            file_name=f"smk_{selected_tahun}.csv",
            mime="text/csv"
        )
    
    st.markdown("---")
    st.markdown("**Preview Data Rasio:**")
    
    if len(rasio_data) > 0:
        # Gunakan st.table sebagai pengganti st.dataframe
        st.table(rasio_data.head(5))
    else:
        st.info("Data rasio tersedia untuk tahun yang ada di data penduduk")

st.divider()
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Dashboard Pendidikan Jawa Barat"
    "</div>",
    unsafe_allow_html=True
)