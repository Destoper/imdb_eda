import streamlit as st
from utils.data_loader import load_data
from utils.styles import apply_custom_styles
from components.sidebar import render_sidebar
from components.kpis import render_kpis
from tabs.evolucao_temporal import render_evolucao_temporal
from tabs.analise_genero import render_analise_genero
from tabs.duracao_formato import render_duracao_formato
from tabs.mercado_global import render_mercado_global
from tabs.hall_fama import render_hall_fama

st.set_page_config(
    page_title="Dashboard de Cinema IMDb",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_styles()

try:
    df, df_crew = load_data()
except FileNotFoundError:
    st.error("⚠️ Arquivos CSV não encontrados. Verifique se 'imdb_movies_final.csv' e 'imdb_crew_profiles.csv' estão na pasta.")
    st.stop()

selected_genres, year_range = render_sidebar(df)

if not selected_genres:
    st.warning("⚠️ Por favor, selecione pelo menos um gênero no menu lateral.")
    st.stop()

df_filtered = df[
    (df['startYear'].between(year_range[0], year_range[1])) & 
    (df['genre'].isin(selected_genres))
].copy()

render_kpis(df_filtered, year_range)

st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    " 🎞️ Visão Geral ", 
    " 🎭 Análise por Gênero ", 
    " ⏱️ Duração & Formato ", 
    " 🌍 Mercado Global ", 
    " 🌟 Hall da Fama "
])

with tab1:
    render_evolucao_temporal(df_filtered, df_crew, selected_genres, df)

with tab2:
    render_analise_genero(df_filtered)

with tab3:
    render_duracao_formato(df_filtered)

with tab4:
    render_mercado_global(df_filtered)

with tab5:
    render_hall_fama(df_crew)
