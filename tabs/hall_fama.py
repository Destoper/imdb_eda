import streamlit as st
import plotly.express as px
from config import COLOR_ACCENT, THEME_PLOTLY

def render_hall_fama(df_crew):
    c_title, c_info = st.columns([1, 2])
    with c_title:
        st.subheader("🌟 Hall da Fama")

    st.info("🔓 **Modo Independente:** Esta seção ignora os filtros laterais para permitir exploração livre.")

    with st.container(border=True):
        st.markdown("##### 🎛️ Configure sua Busca:")
        col_sel1, col_sel2, col_sel3 = st.columns(3)
        with col_sel1: 
            role = st.selectbox("Cargo", ["director", "actor", "actress"], format_func=lambda x: {"director": "Diretor(a)", "actor": "Ator", "actress": "Atriz"}.get(x, x))
        with col_sel2: 
            dec = st.selectbox("Década", sorted(df_crew['decade'].unique(), reverse=True))
        with col_sel3: 
            metric = st.selectbox("Critério de Ordenação", ["Nota Média (Crítica)", "Total Votos (Fama)"])
    
    st.markdown("---")

    sort_col = 'mean_rating' if "Nota" in metric else 'total_votes'
    crew_sub = df_crew[(df_crew['category'] == role) & (df_crew['decade'] == dec)]
    top_15 = crew_sub.sort_values(by=sort_col, ascending=False).head(15)
    
    row_fame1, row_fame2 = st.columns([1, 1])
    
    with row_fame1:
        st.subheader(f"Top 15 Ranking")
        fig_bar = px.bar(top_15, x=sort_col, y='primaryName', orientation='h', text=sort_col, 
                         labels={sort_col: metric, 'primaryName': 'Nome'},
                         template=THEME_PLOTLY, height=600, color_discrete_sequence=[COLOR_ACCENT])
        
        fig_bar.update_yaxes(categoryorder='total ascending', title=None)
        fig_bar.update_xaxes(showticklabels=False, title=None)
        
        fmt = '%{text:.1f}' if "Nota" in metric else '%{text:.2s}'
        fig_bar.update_traces(texttemplate=fmt, textposition='outside', textfont=dict(size=14, color='white'), cliponaxis=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with row_fame2:
        scatter_y = 'total_votes' if "Nota" in metric else 'mean_rating'
        label_y = "Popularidade (Votos)" if "Nota" in metric else "Qualidade (Nota Média)"
        color_seq = ["#842AF8"]

        st.subheader(f"Análise Cruzada: {label_y.split(' ')[0]}")
        st.caption(f"Relacionando Produtividade (X) com {label_y} (Y)")
        
        fig_scat_crew = px.scatter(
            top_15, x='total_movies', y=scatter_y, 
            hover_name='primaryName', text='primaryName', size='total_movies',
            labels={'total_movies': 'Total de Filmes (Escala Log)', scatter_y: label_y},
            template=THEME_PLOTLY, height=600, color_discrete_sequence=color_seq, log_x=True
        )
        fig_scat_crew.update_traces(textposition='top center')
        fig_scat_crew.update_layout(yaxis=dict(autorange=True))
        st.plotly_chart(fig_scat_crew, use_container_width=True)

    st.markdown("### 🏆 Pódio da Década")
    top_3 = top_15.head(3)
    c1, c2, c3 = st.columns(3)
    
    for i, (idx, row) in enumerate(top_3.iterrows()):
        with [c1, c2, c3][i]:
            st.success(f"#{i+1} {row['primaryName']}")
            st.markdown(f"**Obra-Prima:** {row['top_movie_title']}")
            st.caption(f"Ano: {int(row['top_movie_year'])} | Nota: {row['top_movie_rating']}")
            st.progress(row['mean_rating']/10)