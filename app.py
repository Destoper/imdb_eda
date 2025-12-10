import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURAÇÃO DA PÁGINA E DESIGN SYSTEM ---
st.set_page_config(
    page_title="IMDb Intelligence v2",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de Cores "Dark Cinema"
COLOR_BG = "#0e1117"
COLOR_ACCENT = "#f5c518"  # Amarelo IMDb
COLOR_SEC = "#262730"
THEME_PLOTLY = "plotly_dark"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_BG}; }}
    h1, h2, h3, h4 {{ color: {COLOR_ACCENT} !important; }}
    .stMetric {{
        background-color: {COLOR_SEC};
        border-left: 5px solid {COLOR_ACCENT};
        padding: 10px;
        border-radius: 5px;
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        background-color: {COLOR_SEC};
        border-radius: 5px 5px 0px 0px;
        padding-top: 10px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLOR_ACCENT};
        color: black !important;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARREGAMENTO DE DADOS ---
@st.cache_data
def load_data():
    df = pd.read_csv('imdb_movies_final.csv')
    crew = pd.read_csv('imdb_crew_profiles.csv')
    return df, crew

try:
    df, df_crew = load_data()
except FileNotFoundError:
    st.error("⚠️ Faltam arquivos CSV na pasta.")
    st.stop()

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🎬 Painel de Controle")
    st.markdown("---")
    
    # Filtros
    min_year, max_year = int(df['startYear'].min()), int(df['startYear'].max())
    year_range = st.slider("📅 Período", min_year, max_year, (1960, 2023))
    
    all_genres = sorted(df['genre'].unique())
    selected_genres = st.multiselect("🎭 Géneros", all_genres, default=['Action', 'Drama', 'Sci-Fi', 'Horror', 'Romance', 'Comedy'])
    
    st.markdown("---")
    st.info("💡 Dica: Use os filtros acima para refinar a análise em todas as abas.")

# Aplicação dos Filtros
df_filtered = df[
    (df['startYear'].between(year_range[0], year_range[1])) & 
    (df['genre'].isin(selected_genres))
]

# --- 4. CABEÇALHO ---
st.title(f"📊 Dashboard Analítico de Cinema ({year_range[0]}-{year_range[1]})")

# KPIs Globais
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Produções", f"{df_filtered['tconst'].nunique():,}")
k2.metric("Nota Média", f"{df_filtered['averageRating'].mean():.2f}")
k3.metric("Votos Totais", f"{(df_filtered['numVotes'].sum()/1000000):.1f}M")
k4.metric("Duração Média", f"{int(df_filtered['runtimeMinutes'].mean())} min")
k5.metric("Melhor Ano (Nota)", int(df_filtered.groupby('startYear')['averageRating'].mean().idxmax()))

st.markdown("---")

# --- 5. NAVEGAÇÃO ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Evolução Temporal", "🎭 Raio-X Gêneros", "⏱️ Análise Duração", "🌍 Mapa Mundi", "🌟 Hall da Fama"
])

# === ABA 1: EVOLUÇÃO TEMPORAL ===
# === ABA 1: EVOLUÇÃO TEMPORAL ===
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("1. Corrida dos Gêneros (Bump Chart)")
        # Bump Chart
        df_rank = df_filtered.groupby(['decade', 'genre']).size().reset_index(name='count')
        df_rank['rank'] = df_rank.groupby('decade')['count'].rank(method='first', ascending=False)
        df_rank = df_rank[df_rank['rank'] <= 10] 
        
        fig_bump = px.line(df_rank, x='decade', y='rank', color='genre', 
                           markers=True, height=450, template=THEME_PLOTLY)
        fig_bump.update_yaxes(autorange="reversed", title="Ranking de Popularidade")
        st.plotly_chart(fig_bump, use_container_width=True)


        
    st.subheader("3. Volume x Qualidade")
    # Linha dupla
    df_year = df_filtered.groupby('startYear').agg({'averageRating':'mean', 'tconst':'count'}).reset_index()
    fig_dual = go.Figure()
    fig_dual.add_trace(go.Bar(x=df_year['startYear'], y=df_year['tconst'], name='Qtd Filmes', marker_color='#333'))
    fig_dual.add_trace(go.Scatter(x=df_year['startYear'], y=df_year['averageRating'], name='Nota Média', yaxis='y2', line=dict(color=COLOR_ACCENT, width=3)))
    fig_dual.update_layout(template=THEME_PLOTLY, yaxis2=dict(overlaying='y', side='right', range=[5,8]), height=300, showlegend=False)
    st.plotly_chart(fig_dual, use_container_width=True)

    # --- NOVA SEÇÃO: ÍCONES POPULARES ---
    st.markdown("---")
    st.subheader("🏆 Os Ícones da Década (Mais Populares)")
    
    # 1. Identificar décadas presentes no filtro atual
    active_decades = sorted(df_filtered['decade'].unique(), reverse=True)
    
    # 2. Criar um dicionário rápido para buscar gêneros pelo TÍTULO do filme
    # (Agrupamos para pegar todos os gêneros únicos de um filme numa string só)
    movie_genre_map = df.groupby('primaryTitle')['genre'].apply(lambda x: ", ".join(set(x))).to_dict()

    # 3. Loop por década
    for dec in active_decades:
        with st.expander(f"🌟 Década de {dec}", expanded=True):
            
            # Filtrar crew desta década
            crew_dec = df_crew[df_crew['decade'] == dec]
            
            if crew_dec.empty:
                st.write("Dados insuficientes para esta década.")
            else:
                c_dir, c_act, c_actress = st.columns(3)
                
                # Função auxiliar para pegar o TOP 1 e montar o card
                def show_top_star(column, role, label, icon):
                    # Pega o mais popular (maior total de votos)
                    top = crew_dec[crew_dec['category'] == role].sort_values(by='total_votes', ascending=False).head(1)
                    
                    with column:
                        if not top.empty:
                            row = top.iloc[0]
                            st.markdown(f"**{icon} {label}**")
                            st.subheader(row['primaryName'])
                            st.caption(f"Total Votos: {(row['total_votes']/1e6):.1f}M")
                            
                            # Busca gêneros
                            movie_title = row['top_movie_title']
                            genres = movie_genre_map.get(movie_title, "Gênero N/A")
                            
                            st.markdown(f"""
                                <div style='background-color: #262730; padding: 10px; border-radius: 5px; font-size: 0.9em;'>
                                🎬 <b>Hit:</b> {movie_title}<br>
                                🎭 <span style='color: #888'>{genres}</span><br>
                                ⭐ Nota: {row['top_movie_rating']}
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.write("N/A")

                # Exibir as 3 categorias
                show_top_star(c_dir, 'director', 'Diretor(a)', '🎥')
                show_top_star(c_act, 'actor', 'Ator', '🕴️')
                show_top_star(c_actress, 'actress', 'Atriz', '💃')

# === ABA 2: RAIO-X GÊNEROS ===
with tab2:

    # Preparar dados agregados por Gênero
    genre_stats = df_filtered.groupby('genre').agg(
        count=('tconst', 'nunique'),
        rating=('averageRating', 'mean'),
        votes=('numVotes', 'mean')
    ).reset_index()

    # --- BLOCO 1 ---
    st.subheader("1. Quadrante Mágico: Popularidade vs Qualidade")
    st.caption("Onde cada gênero se posiciona? Tamanho da bolha = Volume de Produção")

    fig_bubble = px.scatter(
        genre_stats, x="votes", y="rating", 
        size="count", color="genre",
        hover_name="genre", text="genre",
        template=THEME_PLOTLY, height=500
    )
    fig_bubble.update_traces(textposition='top center')
    fig_bubble.update_layout(
        showlegend=False,
        xaxis_title="Média de Votos (Popularidade)",
        yaxis_title="Nota Média (Crítica)"
    )

    st.plotly_chart(fig_bubble, use_container_width=True)

    # --- BLOCO 2 ---
    st.subheader("2. Grid de Volume (Small Multiples)")
    df_genre_year = df_filtered.groupby(['genre', 'decade']).size().reset_index(name='count')

    fig_sm = px.area(
        df_genre_year, x='decade', y='count',
        facet_col='genre', facet_col_wrap=3,
        color_discrete_sequence=[COLOR_ACCENT],
        template=THEME_PLOTLY, height=500
    )
    fig_sm.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig_sm.update_yaxes(showticklabels=False)

    st.plotly_chart(fig_sm, use_container_width=True)

    # Tabela detalhada
    with st.expander("Ver Dados Detalhados por Gênero"):
        st.dataframe(
            genre_stats.sort_values(by='count', ascending=False)
                .style.background_gradient(cmap="YlGn", subset=['rating']),
            use_container_width=True
        )

# === ABA 3: DURAÇÃO ===
with tab3:
    # Categorizar
    def cat_dur(x):
        if x < 90: return 'Curto (<90m)'
        elif x <= 120: return 'Padrão (90-120m)'
        elif x <= 150: return 'Longo (120-150m)'
        else: return 'Épico (>150m)'
    
    df_filtered['duration_class'] = df_filtered['runtimeMinutes'].apply(cat_dur)
    order = ['Curto (<90m)', 'Padrão (90-120m)', 'Longo (120-150m)', 'Épico (>150m)']
    
    row1_1, row1_2 = st.columns(2)
    
    with row1_1:
        st.subheader("1. Evolução do Formato")
        # Stacked Area
        df_dur = df_filtered.groupby(['decade', 'duration_class']).size().reset_index(name='count')
        df_dur['pct'] = df_dur['count'] / df_dur.groupby('decade')['count'].transform('sum')
        fig_stack = px.area(df_dur, x='decade', y='pct', color='duration_class',
                            category_orders={'duration_class': order},
                            color_discrete_sequence=px.colors.sequential.Plasma,
                            template=THEME_PLOTLY, height=400)
        st.plotly_chart(fig_stack, use_container_width=True)

    with row1_2:
        st.subheader("2. Engajamento por Duração")
        # Bar chart de votos médios
        df_eng = df_filtered.groupby('duration_class')['numVotes'].mean().reset_index()
        fig_eng = px.bar(df_eng, x='duration_class', y='numVotes', color='numVotes',
                         category_orders={'duration_class': order},
                         title="Média de Votos por Categoria",
                         color_continuous_scale='Viridis', template=THEME_PLOTLY, height=400)
        st.plotly_chart(fig_eng, use_container_width=True)
    
    st.subheader("3. Dispersão: Duração vs Nota")
    fig_scatter = px.scatter(df_filtered.sample(min(2000, len(df_filtered))), # Sample para não pesar
                             x='runtimeMinutes', y='averageRating', color='genre',
                             opacity=0.6, template=THEME_PLOTLY, height=400,
                             title="Amostra de 2.000 filmes (Scatter)")
    fig_scatter.update_layout(xaxis_range=[60, 200])
    st.plotly_chart(fig_scatter, use_container_width=True)

# === ABA 4: GEOGRAFIA ===
with tab4:
    st.subheader("Análise Geográfica")
    
    geo1, geo2 = st.columns([2, 1])
    
    with geo1:
        st.markdown("#### Top Países (Fora US/UK)")
        # Treemap de Países
        df_world = df_filtered[~df_filtered['region'].isin(['US', 'GB', 'UK', '\\N', 'Unknown'])]
        country_counts = df_world['region'].value_counts().reset_index(name='count')
        country_counts.columns = ['region', 'count']
        
        fig_tree = px.treemap(country_counts.head(20), path=['region'], values='count',
                              color='count', color_continuous_scale='Magma',
                              template=THEME_PLOTLY, height=500)
        st.plotly_chart(fig_tree, use_container_width=True)
        
    with geo2:
        st.markdown("#### Comparativo Macro")
        # Bar Chart US vs World
        df_macro = df_filtered.groupby(['decade', 'macro_region'])['averageRating'].mean().reset_index()
        fig_macro = px.bar(df_macro, x='decade', y='averageRating', color='macro_region',
                           barmode='group', template=THEME_PLOTLY, height=500,
                           color_discrete_map={'Hollywood/UK': '#3b5998', 'World Cinema': COLOR_ACCENT})
        fig_macro.update_yaxes(range=[5, 8])
        st.plotly_chart(fig_macro, use_container_width=True)

# === ABA 5: HALL DA FAMA ===
with tab5:
    col_sel1, col_sel2, col_sel3 = st.columns(3)
    with col_sel1: role = st.selectbox("Cargo", ["director", "actor", "actress"])
    with col_sel2: dec = st.selectbox("Década", sorted(df_crew['decade'].unique(), reverse=True))
    with col_sel3: metric = st.selectbox("Ordenar por", ["Nota Média (Crítica)", "Total Votos (Fama)"])
    
    sort_col = 'mean_rating' if "Nota" in metric else 'total_votes'
    
    # Filtrar
    crew_sub = df_crew[(df_crew['category'] == role) & (df_crew['decade'] == dec)]
    top_15 = crew_sub.sort_values(by=sort_col, ascending=False).head(15)
    
    row_fame1, row_fame2 = st.columns([2, 1])
    
    with row_fame1:
        st.subheader(f"Top 15 {role.capitalize()}s - Anos {dec}")
        fig_bar = px.bar(top_15, x=sort_col, y='primaryName', orientation='h',
                         text=sort_col, color=sort_col, 
                         color_continuous_scale='Viridis', template=THEME_PLOTLY, height=600)
        fig_bar.update_yaxes(categoryorder='total ascending')
        fig_bar.update_traces(texttemplate='%{text:.1f}' if "Nota" in metric else '%{text:.2s}')
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with row_fame2:
        st.subheader("Dispersão: Operário vs Autor")
        st.caption("Eixo X: Quantos filmes fez | Eixo Y: Nota Média")
        fig_scat_crew = px.scatter(crew_sub, x='total_movies', y='mean_rating', 
                                   hover_name='primaryName', size='total_movies',
                                   template=THEME_PLOTLY, height=600, color_discrete_sequence=[COLOR_ACCENT])
        st.plotly_chart(fig_scat_crew, use_container_width=True)

    # Cards de Detalhes
    st.markdown("### 🏆 Destaques do Pódio")
    top_3 = top_15.head(3)
    c1, c2, c3 = st.columns(3)
    
    for i, (idx, row) in enumerate(top_3.iterrows()):
        col = [c1, c2, c3][i]
        with col:
            st.success(f"#{i+1} {row['primaryName']}")
            st.markdown(f"**Filme de Ouro:** {row['top_movie_title']}")
            st.caption(f"Ano: {int(row['top_movie_year'])} | Nota: {row['top_movie_rating']}")
            st.progress(row['mean_rating']/10)

st.markdown("---")
st.caption("© 2025 IMDb Intelligence Project")