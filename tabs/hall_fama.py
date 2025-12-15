import streamlit as st
import plotly.express as px
from config import COLOR_ACCENT, THEME_PLOTLY

def render_hall_fama(df_crew):
    c_title, _ = st.columns([1, 2])
    with c_title:
        st.subheader("🌟 Hall da Fama")

    st.info("🔓 **Modo Panorâmico:** Comparativo direto sem filtros laterais.")

    with st.container(border=True):
        col_sel1, col_sel2 = st.columns(2) 
        
        with col_sel1: 
            role = st.selectbox("Cargo", ["director", "actor", "actress"], format_func=lambda x: {"director": "Diretor(a)", "actor": "Ator", "actress": "Atriz"}.get(x, x))
        with col_sel2: 
            dec = st.selectbox("Década", sorted(df_crew['decade'].unique(), reverse=True))
    
    st.markdown("---")

    crew_sub = df_crew[(df_crew['category'] == role) & (df_crew['decade'] == dec)].copy()
    
    top_votes = crew_sub.sort_values(by='total_votes', ascending=False).head(15)
    
    mask_relevance = (crew_sub['total_movies'] >= 2) & (crew_sub['total_votes'] > 1000)
    crew_qualified = crew_sub[mask_relevance]
    if crew_qualified.empty: crew_qualified = crew_sub
    top_rating = crew_qualified.sort_values(by='mean_rating', ascending=False).head(15)

    col_pop, col_qual = st.columns(2)
    
    with col_pop:
        st.subheader("🗳️ Mais Populares")
        st.caption("Os 15 artistas mais votados na década selecionada")
        
        fig_votes = px.bar(
            top_votes, 
            x='total_votes', 
            y='primaryName', 
            orientation='h', 
            text='total_votes', 
            template=THEME_PLOTLY, 
            height=500,
            color_discrete_sequence=["#842AF8"]
        )
        
        fig_votes.update_layout(xaxis_visible=False, xaxis_showgrid=False, yaxis_title=None, margin=dict(l=0, r=0, t=0, b=0))
        fig_votes.update_yaxes(categoryorder='total ascending', showgrid=False)
        fig_votes.update_traces(texttemplate='%{text:.2s}', textposition='outside', textfont=dict(size=14, color='white'), cliponaxis=False)
        st.plotly_chart(fig_votes, use_container_width=True)
        
        st.divider()
        st.markdown("#### Qual a Nota Média do Pódio dos Mais Populares?")
        st.caption("Principal produção e avaliação média para os mais populares.")

        top3_votes = top_votes.head(3).reset_index()
        for i, row in top3_votes.iterrows():
            medals = ["🥇", "🥈", "🥉"]
            rank_icon = medals[i]
            
            with st.container(border=True):
                c_icon, c_det, c_val = st.columns([1, 4, 2])
                with c_icon:
                    st.markdown(f"<h2 style='text-align: center; margin: 0;'>{rank_icon}</h2>", unsafe_allow_html=True)
                with c_det:
                    st.markdown(f"**{row['primaryName']}**")
                    st.caption(f"🎬 {row['top_movie_title']}")
                with c_val:
                    st.markdown(f"<div style='text-align: right; color: {COLOR_ACCENT}; font-weight: bold;'>{row['mean_rating']:.1f}<br><span style='font-size:0.8em; color:#666'>média IMDb</span></div>", unsafe_allow_html=True)

    with col_qual:
        st.subheader("⭐ Mais Aclamados")
        st.caption("Os 15 artistas com maior avaliação média na década selecionada ")

        fig_rate = px.bar(
            top_rating, 
            x='mean_rating', 
            y='primaryName', 
            orientation='h', 
            text='mean_rating', 
            template=THEME_PLOTLY, 
            height=500, 
            color_discrete_sequence=[COLOR_ACCENT]
        )
        
        fig_rate.update_layout(xaxis_visible=False, xaxis_showgrid=False, yaxis_title=None, xaxis_range=[0, 10.5], margin=dict(l=0, r=0, t=0, b=0))
        fig_rate.update_yaxes(categoryorder='total ascending', showgrid=False)
        fig_rate.update_traces(texttemplate='%{text:.2f}', textposition='outside', textfont=dict(size=14, color='white'), cliponaxis=False)
        st.plotly_chart(fig_rate, use_container_width=True)

        st.divider()
        st.markdown("#### Quantos Votos o Pódio dos Aclamados Recebeu?")
        st.caption("Principal produção e reconhecimento para os mais aclamados.")

        top3_rating = top_rating.head(3).reset_index()
        for i, row in top3_rating.iterrows():
            medals = ["🥇", "🥈", "🥉"]
            rank_icon = medals[i]
            
            with st.container(border=True):
                c_icon, c_det, c_val = st.columns([1, 4, 2])
                with c_icon:
                    st.markdown(f"<h2 style='text-align: center; margin: 0;'>{rank_icon}</h2>", unsafe_allow_html=True)
                with c_det:
                    st.markdown(f"**{row['primaryName']}**")
                    st.caption(f"🌟 {row['top_movie_title']}")
                with c_val:
                    st.markdown(f"<div style='text-align: right; color: #842AF8; font-weight: bold;'>{row['total_votes']:.0f}<br><span style='font-size:0.8em; color:#666'>votos</span></div>", unsafe_allow_html=True)