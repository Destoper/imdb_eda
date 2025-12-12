import streamlit as st
from config import DEFAULT_GENRES

def render_sidebar(df):
    with st.sidebar:
        st.title("🎬 Painel de Controle")
        st.markdown("---")

        min_year, max_year = int(df['startYear'].min()), int(df['startYear'].max())
        year_range = st.slider("📅 Período de Análise", min_year, max_year, (1960, 2025))

        all_genres = sorted(df['genre'].unique())
        
        if 'selected_genres_state' not in st.session_state:
            st.session_state['selected_genres_state'] = DEFAULT_GENRES

        def select_all():
            st.session_state['selected_genres_state'] = all_genres
        
        def deselect_all():
            st.session_state['selected_genres_state'] = []

        st.write("🎭 **Filtro de Gêneros**")
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.button("✅ Todos", on_click=select_all, help="Selecionar todos os gêneros")
        with col_b2:
            st.button("❌ Limpar", on_click=deselect_all, help="Remover todas as seleções")

        selected_genres = st.multiselect(
            "Selecione:", 
            all_genres, 
            key='selected_genres_state' 
        )
        
        st.markdown("---")
        st.info("💡 **Dica:** Os filtros laterais afetam todas as abas, exceto o 'Hall da Fama'.")
    
    return selected_genres, year_range