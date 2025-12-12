import streamlit as st
import plotly.express as px
from config import COLOR_ACCENT, THEME_PLOTLY

def render_analise_genero(df_filtered):
    st.info("ℹ️ **Nota Metodológica:** Filmes com múltiplos gêneros (ex: 'Ação, Sci-Fi') são contabilizados individualmente em cada categoria correspondente.")
    
    genre_stats = df_filtered.groupby('genre').agg(
        count=('tconst', 'nunique'), 
        rating=('averageRating', 'mean'), 
        votes=('numVotes', 'mean')
    ).reset_index()

    st.subheader("Popularidade vs. Prestígio")
    st.caption("O tamanho da bolha representa o volume de filmes por gênero.")
    fig_bubble = px.scatter(genre_stats, x="votes", y="rating", size="count", color="genre", 
                            hover_name="genre", text="genre", template=THEME_PLOTLY, height=500,
                            labels={'votes': 'Média de Votos (Popularidade)', 'rating': 'Nota Média (Crítica)', 'count': 'Qtd. Filmes'})
    fig_bubble.update_traces(textposition='top center')
    st.plotly_chart(fig_bubble, use_container_width=True)

    st.markdown("---")

    n_genres = df_filtered['genre'].nunique()
    n_rows = (n_genres // 3) + (1 if n_genres % 3 > 0 else 0)
    dynamic_height = max(500, n_rows * 250) 

    st.subheader("Tendência de Produção (Volume)")
    df_genre_count = df_filtered.groupby(['genre', 'decade']).size().reset_index(name='count')
    
    fig_area = px.area(
        df_genre_count, x='decade', y='count', 
        facet_col='genre', facet_col_wrap=3,
        color_discrete_sequence=[COLOR_ACCENT],
        labels={'decade': 'Década', 'count': 'Filmes Produzidos'},
        template=THEME_PLOTLY, height=dynamic_height
    )
    fig_area.update_yaxes(showticklabels=False)
    fig_area.update_xaxes(showticklabels=True)
    fig_area.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    st.plotly_chart(fig_area, use_container_width=True)

    st.subheader("Tendência de Qualidade (Nota)")
    df_genre_rating = df_filtered.groupby(['genre', 'decade'])['averageRating'].mean().reset_index()
    
    fig_line = px.line(
        df_genre_rating, x='decade', y='averageRating', 
        facet_col='genre', facet_col_wrap=3,
        markers=True,
        color_discrete_sequence=['#00CC96'],
        labels={'decade': 'Década', 'averageRating': 'Nota Média'},
        template=THEME_PLOTLY, height=dynamic_height
    )
    fig_line.update_yaxes(range=[3, 9], showticklabels=True) 
    fig_line.update_xaxes(showticklabels=True)
    fig_line.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    st.plotly_chart(fig_line, use_container_width=True)