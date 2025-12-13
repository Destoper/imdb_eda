import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import COLOR_ACCENT, THEME_PLOTLY

def render_evolucao_temporal(df_filtered, df_crew, selected_genres, df):
    st.subheader("Tendências de Gênero: Popularidade vs. Qualidade")
    st.caption("Como a preferência do público e da crítica mudou ao longo das décadas.")

    col_pop, col_qual = st.columns(2)
    
    with col_pop:
        st.markdown("##### Ranking de Volume (Popularidade de Produção)")
        df_rank_pop = df_filtered.groupby(['decade', 'genre']).size().reset_index(name='count')
        df_rank_pop['rank'] = df_rank_pop.groupby('decade')['count'].rank(method='first', ascending=False)
        df_rank_pop = df_rank_pop[df_rank_pop['rank'] <= 8] 
        
        fig_bump_pop = px.line(df_rank_pop, x='decade', y='rank', color='genre', 
                           markers=True, height=450, template=THEME_PLOTLY)
        fig_bump_pop.update_xaxes(title="Década")
        fig_bump_pop.update_yaxes(title="Ranking (1º = Mais Produzido)", autorange="reversed")
        st.plotly_chart(fig_bump_pop, use_container_width=True)

    with col_qual:
        st.markdown("##### Ranking de Prestígio (Nota Média)")
        df_rank_qual = df_filtered.groupby(['decade', 'genre'])['averageRating'].mean().reset_index()
        df_rank_qual['rank'] = df_rank_qual.groupby('decade')['averageRating'].rank(method='first', ascending=False)
        df_rank_qual = df_rank_qual[df_rank_qual['rank'] <= 8]
        
        fig_bump_qual = px.line(df_rank_qual, x='decade', y='rank', color='genre', 
                           markers=True, height=450, template=THEME_PLOTLY)
        fig_bump_qual.update_xaxes(title="Década")
        fig_bump_qual.update_yaxes(title="Ranking (1º = Maior Nota)", autorange="reversed")
        st.plotly_chart(fig_bump_qual, use_container_width=True)

    st.divider()

    col_stats1, col_stats2 = st.columns(2)
    with col_stats1:
        st.subheader("Histograma de Notas")
        st.caption("Como as avaliações estão distribuídas estatisticamente.")
        fig_hist = px.histogram(df_filtered, x="averageRating", nbins=20, 
                                labels={'averageRating': 'Nota IMDb', 'count': 'Frequência'},
                                color_discrete_sequence=[COLOR_ACCENT], template=THEME_PLOTLY)
        fig_hist.update_layout(bargap=0.1, yaxis_title="Quantidade de Filmes")
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col_stats2:
        st.subheader("Correlação Anual: Volume vs. Qualidade")
        st.caption("Existe relação entre quantidade de filmes lançados e a nota média do ano?")
        df_year = df_filtered.groupby('startYear').agg({'averageRating':'mean', 'tconst':'count'}).reset_index()
        
        fig_dual = go.Figure()
        fig_dual.add_trace(go.Bar(x=df_year['startYear'], y=df_year['tconst'], name='Qtd. Filmes', marker_color='#333', yaxis='y'))
        fig_dual.add_trace(go.Scatter(x=df_year['startYear'], y=df_year['averageRating'], name='Nota Média', yaxis='y2', line=dict(color=COLOR_ACCENT, width=3)))
        
        fig_dual.update_layout(
            template=THEME_PLOTLY, height=420, showlegend=True, legend=dict(orientation="h", y=1.1),
            yaxis=dict(title=dict(text="Volume de Produção", font=dict(color="#888")), tickfont=dict(color="#888")),
            yaxis2=dict(title=dict(text="Nota Média", font=dict(color=COLOR_ACCENT)), tickfont=dict(color=COLOR_ACCENT), anchor="x", overlaying="y", side="right", range=[4, 8.5])
        )
        st.plotly_chart(fig_dual, use_container_width=True)

    st.markdown("---")
    
    render_galeria_icones(df_filtered, df_crew, selected_genres, df)

def render_galeria_icones(df_filtered, df_crew, selected_genres, df):
    c_head1, c_head2 = st.columns([2, 1])
    with c_head1:
        st.subheader("🏆 Galeria: Destaques da Década")
        st.caption(f"Os nomes que definiram a era (Filtrado por: {', '.join(selected_genres)})")
    with c_head2:
        ranking_metric = st.radio("Critério de Seleção:", ["Popularidade (Votos)", "Prestígio (Nota Média)"], horizontal=True)

    sort_col = 'total_votes' if "Votos" in ranking_metric else 'mean_rating'
    
    df_temp_map = df.copy()
    df_temp_map['startYear'] = pd.to_numeric(df_temp_map['startYear'], errors='coerce').fillna(0).astype(int)
    df_temp_map_grouped = df_temp_map.groupby(['primaryTitle', 'startYear'])['genre'].apply(list).reset_index()
    
    movie_genre_map = df_temp_map_grouped.set_index(['primaryTitle', 'startYear'])['genre'].to_dict()

    def get_winner(decade, role, genre_list_pt, sort_by):
        candidates = df_crew[(df_crew['decade'] == decade) & (df_crew['category'] == role)].copy()
        
        def has_genre(row):
            title = row['top_movie_title']
            try:
                year = int(row['top_movie_year'])
            except:
                year = 0
        
            m_genres = movie_genre_map.get((title, year), [])
            
            if not m_genres:
                return False 

            return not set(m_genres).isdisjoint(genre_list_pt)
        
        candidates = candidates[candidates.apply(has_genre, axis=1)]
        
        if not candidates.empty:
            return candidates.sort_values(by=sort_by, ascending=False).iloc[0]
        return None

    active_decades = sorted(df_filtered['decade'].unique(), reverse=True)

    for dec in active_decades:
        winner_dir = get_winner(dec, 'director', selected_genres, sort_col)
        winner_act = get_winner(dec, 'actor', selected_genres, sort_col)
        winner_actress = get_winner(dec, 'actress', selected_genres, sort_col)
        
        if winner_dir is not None or winner_act is not None or winner_actress is not None:
            st.markdown(f"### 🗓️ Década de {dec}")
            c1, c2, c3 = st.columns(3)
            
            
            draw_card(c1, winner_dir, "🎥", "Direção", ranking_metric, movie_genre_map)
            draw_card(c2, winner_act, "🤵🏿‍♂️", "Ator", ranking_metric, movie_genre_map)
            draw_card(c3, winner_actress, "🤵‍♀️", "Atriz", ranking_metric, movie_genre_map)
            st.divider()

def draw_card(col, row, role_icon, role_name, ranking_metric, movie_genre_map):
    with col:
        if row is not None:
            title = row['top_movie_title']
            try: year = int(row['top_movie_year'])
            except: year = 0
            
            # Busca com chave composta
            genres_real = movie_genre_map.get((title, year), ["Gênero N/A"])
            genres_str = " • ".join(genres_real)
            
            color_vote = "#f5c518" if "Votos" in ranking_metric else "#ddd"
            color_rate = "#f5c518" if "Nota" in ranking_metric else "#ddd"
            
            st.markdown(f"""
            <div style="background-color: #1f2129; border: 1px solid #333; border-radius: 10px; padding: 15px; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
                <div style="color: #888; font-size: 0.8em; text-transform: uppercase; letter-spacing: 1px;">
                    {role_icon} {role_name}
                </div>
                <div style="font-size: 1.2em; font-weight: bold; color: #fff; margin: 5px 0;">
                    {row['primaryName']}
                </div>
                <div style="margin-top: 5px; font-size: 0.9em; color: #aaa;">
                    🎬 <b>{row['top_movie_title']}</b>
                </div>
                <div style="font-size: 0.75em; color: #666; margin-bottom: 10px;">
                    {genres_str}
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.9em; background-color: #0e1117; padding: 8px; border-radius: 5px;">
                    <span style="color: {color_rate}; font-weight: bold;">
                        ⭐ {row['mean_rating']:.1f}
                    </span>
                    <span style="color: {color_vote}; font-weight: bold;">
                        🗳️ {(row['total_votes']/1e6):.1f}M
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='padding: 20px; text-align: center; color: #444; border: 1px dashed #333; border-radius: 10px;'> - </div>", unsafe_allow_html=True)