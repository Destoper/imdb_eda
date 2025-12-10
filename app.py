import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURAÇÃO DA PÁGINA E DESIGN SYSTEM ---
st.set_page_config(
    page_title="Análise de Filmes utilizando o dataset IMDb",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dicionário de Tradução
genre_translation = {
    "Action": "Ação",
    "Adventure": "Aventura",
    "Animation": "Animação",
    "Biography": "Biografia",
    "Comedy": "Comédia",
    "Crime": "Crime",
    "Documentary": "Documentário",
    "Drama": "Drama",
    "Family": "Família",
    "Fantasy": "Fantasia",
    "Film-Noir": "Noir",
    "History": "História",
    "Horror": "Terror",
    "Music": "Música",
    "Musical": "Musical",
    "Mystery": "Mistério",
    "Romance": "Romance",
    "Sci-Fi": "Ficção Científica",
    "Sport": "Esporte",
    "Thriller": "Suspense",
    "War": "Guerra",
    "Western": "Faroeste"
}

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

    min_year, max_year = int(df['startYear'].min()), int(df['startYear'].max())
    year_range = st.slider("📅 Período", min_year, max_year, (1960, 2023))

    all_genres = sorted(df['genre'].unique())
    
    if 'selected_genres_state' not in st.session_state:
        st.session_state['selected_genres_state'] = ['Action', 'Drama', 'Sci-Fi', 'Horror', 'Romance', 'Comedy']

    # Funções de Callback
    def select_all():
        st.session_state['selected_genres_state'] = all_genres
    
    def deselect_all():
        st.session_state['selected_genres_state'] = []

    st.write("🎭 **Filtro de Gêneros**")
    
    # Botões lado a lado
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
    st.info("💡 Dica: Use os botões acima para alternar rapidamente entre ver tudo ou limpar.")

if not selected_genres:
    st.warning("⚠️ Por favor, selecione pelo menos um gênero no menu lateral.")
    st.stop()

df_filtered = df[
    (df['startYear'].between(year_range[0], year_range[1])) & 
    (df['genre'].isin(selected_genres))
].copy()

# --- APLICAR TRADUÇÃO NOS DADOS FILTRADOS ---
df_filtered['genre'] = df_filtered['genre'].map(genre_translation).fillna(df_filtered['genre'])

selected_genres_pt = [genre_translation.get(g, g) for g in selected_genres]


# --- 4. CABEÇALHO ---
st.title(f"📊 Dashboard de Filmes utilizando o dataset IMDb ({year_range[0]}-{year_range[1]})")

df_unique_movies = df_filtered.drop_duplicates(subset='tconst')

# KPIs Globais
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Produções", f"{df_unique_movies['tconst'].count():,}")
k2.metric("Nota Média", f"{df_unique_movies['averageRating'].mean():.2f}")
k3.metric("Votos Totais", f"{(df_unique_movies['numVotes'].sum()/1000000):.1f}M") # Agora soma corretamente
k4.metric("Duração Média", f"{int(df_unique_movies['runtimeMinutes'].mean())} min")

# Para o "Melhor Ano", mantemos a lógica original ou ajustamos também:
best_year = df_unique_movies.groupby('startYear')['averageRating'].mean().idxmax()
k5.metric("Melhor Ano (Nota)", int(best_year))

st.markdown("---")

# --- 5. NAVEGAÇÃO ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    " 📈 Evolução Temporal ", " 🎭 Gêneros ", " ⏱️ Análise de Duração ", " 🌍 Mapa Mundi ", " 🌟 Hall da Fama "
])


# === ABA 1: EVOLUÇÃO TEMPORAL ===
with tab1:
    st.subheader("Gêneros Mais Populares ao Longo das Décadas")
    st.caption("Comparando a evolução por quantidade de filmes vs qualidade média.")

    col_pop, col_qual = st.columns(2)
    
    # GRÁFICO 1: RANKING DE POPULARIDADE (VOLUME)
    with col_pop:
        st.markdown("##### 🍿 Ranking por Popularidade (Volume)")
        df_rank_pop = df_filtered.groupby(['decade', 'genre']).size().reset_index(name='count')
        # Rankear (Maior volume = Rank 1)
        df_rank_pop['rank'] = df_rank_pop.groupby('decade')['count'].rank(method='first', ascending=False)
        df_rank_pop = df_rank_pop[df_rank_pop['rank'] <= 10] 
        
        fig_bump_pop = px.line(df_rank_pop, x='decade', y='rank', color='genre', 
                           markers=True, height=450, template=THEME_PLOTLY)
        fig_bump_pop.update_xaxes(title="Década")
        fig_bump_pop.update_yaxes(title="Ranking (1º = Mais Produzido)", autorange="reversed")
        st.plotly_chart(fig_bump_pop, use_container_width=True)

    # GRÁFICO 2: RANKING DE QUALIDADE (NOTA)
    with col_qual:
        st.markdown("##### ⭐ Ranking por Qualidade (Nota Média)")
        df_rank_qual = df_filtered.groupby(['decade', 'genre'])['averageRating'].mean().reset_index()
        # Rankear (Maior nota = Rank 1)
        df_rank_qual['rank'] = df_rank_qual.groupby('decade')['averageRating'].rank(method='first', ascending=False)
        df_rank_qual = df_rank_qual[df_rank_qual['rank'] <= 10]
        
        fig_bump_qual = px.line(df_rank_qual, x='decade', y='rank', color='genre', 
                           markers=True, height=450, template=THEME_PLOTLY)
        fig_bump_qual.update_xaxes(title="Década")
        fig_bump_qual.update_yaxes(title="Ranking (1º = Maior Nota)", autorange="reversed")
        st.plotly_chart(fig_bump_qual, use_container_width=True)

    st.divider()

    col_stats1, col_stats2 = st.columns(2)
    with col_stats1:
        st.subheader("Distribuição das Notas")
        # Histograma
        fig_hist = px.histogram(df_filtered, x="averageRating", nbins=20, 
                                title="Frequência de Notas",
                                labels={'averageRating': 'Nota IMDb'},
                                color_discrete_sequence=[COLOR_ACCENT], template=THEME_PLOTLY)
        fig_hist.update_layout(bargap=0.1)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col_stats2:
        st.subheader("3. Volume x Qualidade (Anual)")
        
        # Agrupamento
        df_year = df_filtered.groupby('startYear').agg({'averageRating':'mean', 'tconst':'count'}).reset_index()
        
        fig_dual = go.Figure()
        
        # Barras (Eixo da Esquerda - Y1)
        fig_dual.add_trace(go.Bar(
            x=df_year['startYear'], 
            y=df_year['tconst'], 
            name='Quantidade', 
            marker_color='#333',
            yaxis='y'
        ))
        
        # Linha (Eixo da Direita - Y2)
        fig_dual.add_trace(go.Scatter(
            x=df_year['startYear'], 
            y=df_year['averageRating'], 
            name='Nota Média', 
            yaxis='y2',
            line=dict(color=COLOR_ACCENT, width=3)
        ))
        
        # Layout Corrigido (Sintaxe Robusta)
        fig_dual.update_layout(
            template=THEME_PLOTLY,
            height=400,
            showlegend=True,
            legend=dict(orientation="h", y=1.1),
            
            # Eixo Y1 (Esquerda)
            yaxis=dict(
                title=dict(text="Qtd. Produções", font=dict(color="#888")),
                tickfont=dict(color="#888")
            ),
            
            # Eixo Y2 (Direita)
            yaxis2=dict(
                title=dict(text="Nota IMDb", font=dict(color=COLOR_ACCENT)),
                tickfont=dict(color=COLOR_ACCENT),
                anchor="x",
                overlaying="y",
                side="right",
                range=[5, 8.5]
            )
        )
        
        st.plotly_chart(fig_dual, use_container_width=True)

    st.markdown("---")
    
    # --- CABEÇALHO COM CONTROLE ---
    c_head1, c_head2 = st.columns([2, 1])
    with c_head1:
        st.subheader("🏆 Galeria: Os Ícones da Década")
        st.caption(f"Filtrando por gêneros: {', '.join(selected_genres_pt)}")
    with c_head2:
        # SELETOR DE CRITÉRIO
        ranking_metric = st.radio("Critério do Pódio:", 
                                  ["Popularidade (Votos)", "Prestígio (Nota Média)"], 
                                  horizontal=True)


    sort_col = 'total_votes' if "Votos" in ranking_metric else 'mean_rating'
    
    def translate_list(genre_str):
        if pd.isna(genre_str): return []
        return [genre_translation.get(g, g) for g in str(genre_str).split(',')]

    df_temp_map = df.copy()
    df_temp_map['genres_list'] = df_temp_map['genre'].apply(translate_list)
    movie_genre_map = df_temp_map.set_index('primaryTitle')['genres_list'].to_dict()

    # 2. Função de Filtro Dinâmica
    def get_winner(decade, role, genre_list_pt, sort_by):
        # Filtra pessoas da década e função
        candidates = df_crew[(df_crew['decade'] == decade) & (df_crew['category'] == role)].copy()
        
        # Filtra: O "Top Movie" TEM que ter um dos gêneros selecionados (em PT)
        def has_genre(movie_title):
            m_genres = movie_genre_map.get(movie_title, [])
            return not set(m_genres).isdisjoint(genre_list_pt)
        
        candidates = candidates[candidates['top_movie_title'].apply(has_genre)]
        
        if not candidates.empty:
            return candidates.sort_values(by=sort_by, ascending=False).iloc[0]
        return None

    # --- RENDERIZAÇÃO VISUAL (CARDS) ---
    active_decades = sorted(df_filtered['decade'].unique(), reverse=True)

    for dec in active_decades:
        # Busca vencedores com o critério escolhido (sort_col)
        winner_dir = get_winner(dec, 'director', selected_genres_pt, sort_col)
        winner_act = get_winner(dec, 'actor', selected_genres_pt, sort_col)
        winner_actress = get_winner(dec, 'actress', selected_genres_pt, sort_col)
        
        if winner_dir is not None or winner_act is not None or winner_actress is not None:
            
            st.markdown(f"### 🗓️ Anos {dec}")
            c1, c2, c3 = st.columns(3)
            
            def draw_card(col, row, role_icon, role_name):
                with col:
                    if row is not None:
                        # Busca gêneros reais
                        genres_real = movie_genre_map.get(row['top_movie_title'], ["N/A"])
                        genres_str = " • ".join(genres_real[:2])
                        
                        # Cores dinâmicas para destacar o vencedor
                        color_vote = "#f5c518" if "Votos" in ranking_metric else "#ddd" # Amarelo se for Votos
                        color_rate = "#f5c518" if "Nota" in ranking_metric else "#ddd"  # Amarelo se for Nota
                        
                        # Card HTML
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
                                    ⭐ {row['mean_rating']:.1f} <span style="font-size:0.7em; color:#555">(Média)</span>
                                </span>
                                <span style="color: {color_vote}; font-weight: bold;">
                                    🗳️ {(row['total_votes']/1e6):.1f}M
                                </span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='padding: 20px; text-align: center; color: #444; border: 1px dashed #333; border-radius: 10px;'> - </div>", unsafe_allow_html=True)

            draw_card(c1, winner_dir, "🎥", "Direção")
            draw_card(c2, winner_act, "🕴️", "Ator")
            draw_card(c3, winner_actress, "💃", "Atriz")
            
            st.divider()

# === ABA 2: RAIO-X GÊNEROS ===
with tab2:
    st.info("ℹ️ **Nota de Análise:** Nesta aba, filmes com múltiplos gêneros (ex: 'Ação, Sci-Fi') são contabilizados em todas as suas categorias correspondentes. Isso permite analisar a força individual de cada gênero.")
    # Preparar dados agregados por Gênero
    genre_stats = df_filtered.groupby('genre').agg(
        count=('tconst', 'nunique'),
        rating=('averageRating', 'mean'),
        votes=('numVotes', 'mean')
    ).reset_index()

    # --- BLOCO 1 ---
    st.subheader(" Popularidade vs Prestígio")
    st.caption("Onde cada gênero se posiciona? Tamanho da bolha representa o Volume de Produção")

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
    st.subheader("Evolução da Producao por Gênero ao Longo do Tempo")
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

    # Tabela
    with st.expander("Ver Dados Detalhados por Gênero"):
        st.dataframe(
            genre_stats.sort_values(by='count', ascending=False)
                .style.background_gradient(cmap="YlGn", subset=['rating']),
            use_container_width=True
        )

# === ABA 3: DURAÇÃO ===
with tab3:
    def cat_dur(x):
        if x < 90: return 'Curto (<90m)'
        elif x <= 120: return 'Padrão (90-120m)'
        elif x <= 150: return 'Longo (120-150m)'
        else: return 'Épico (>150m)'
    
    df_filtered = df_filtered.copy()
    df_filtered['duration_class'] = df_filtered['runtimeMinutes'].apply(cat_dur)

    order = ['Curto (<90m)', 'Padrão (90-120m)', 'Longo (120-150m)', 'Épico (>150m)']

    palette = px.colors.sequential.Plasma
    color_map = {
        'Curto (<90m)': palette[1],
        'Padrão (90-120m)': palette[3],
        'Longo (120-150m)': palette[5],
        'Épico (>150m)': palette[7]
    }

    # ------------------------
    # 1º LINHA: Evolução + Engajamento
    # ------------------------
    row1_1, row1_2 = st.columns(2)

    with row1_1:
        st.subheader("Evolução do Formato")
        
        # Cálculo de porcentagem
        df_dur = df_filtered.groupby(['decade', 'duration_class']).size().reset_index(name='count')
        df_dur['pct'] = df_dur['count'] / df_dur.groupby('decade')['count'].transform('sum')

        fig_stack = px.area(
            df_dur, x='decade', y='pct',
            color='duration_class',
            category_orders={'duration_class': order},
            color_discrete_map=color_map,
            template=THEME_PLOTLY, height=400
        )
        st.plotly_chart(fig_stack, use_container_width=True)

    with row1_2:
        st.subheader("Engajamento (Votos)")

        df_eng = df_filtered.groupby('duration_class')['numVotes'].mean().reset_index()

        fig_eng = px.bar(
            df_eng, x='duration_class', y='numVotes',
            color='duration_class',
            category_orders={'duration_class': order},
            color_discrete_map=color_map,
            title="Média de Votos por Categoria",
            template=THEME_PLOTLY, height=400
        )
        st.plotly_chart(fig_eng, use_container_width=True)

    # ------------------------
    # 2.5 Nota Média (Violino)
    # ------------------------
    st.subheader("Distribuição de Notas por Duração")

    fig_rating_dur = px.violin(
        df_filtered, 
        x='duration_class', 
        y='averageRating',
        color='duration_class',
        category_orders={'duration_class': order},
        color_discrete_map=color_map,
        box=True,         
        points=False,     
        title="Densidade das Notas por Duração",
        template=THEME_PLOTLY,
        height=400
    )
    st.plotly_chart(fig_rating_dur, use_container_width=True)

    # ------------------------
    # Scatter (Duração vs Nota)
    # ------------------------
    st.subheader("Dispersão Detalhada")

    # Amostragem para performance
    fig_scatter = px.scatter(
        df_filtered.sample(min(2000, len(df_filtered))),
        x='runtimeMinutes', 
        y='averageRating', 
        color='genre', 
        opacity=0.6,
        template=THEME_PLOTLY,
        height=400,
        title="Amostra de 2.000 filmes"
    )
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
        df_macro = df_filtered.groupby(['decade', 'macro_region'])['averageRating'].mean().reset_index()
        fig_macro = px.bar(df_macro, x='decade', y='averageRating', color='macro_region',
                           barmode='group', template=THEME_PLOTLY, height=500,
                           color_discrete_map={'Hollywood/UK': '#3b5998', 'World Cinema': COLOR_ACCENT})
        fig_macro.update_yaxes(range=[5, 8])
        st.plotly_chart(fig_macro, use_container_width=True)

# === ABA 5: HALL DA FAMA ===
with tab5:
    c_title, c_info = st.columns([1, 2])
    with c_title:
        st.subheader("🌟 Hall da Fama")

    st.info("🔓 **Modo Independente:** Esta seção ignora os filtros da barra lateral. Use os controles abaixo para explorar décadas específicas.")

    with st.container(border=True):
        st.markdown("##### 🎛️ Configure sua Busca:")
        
        col_sel1, col_sel2, col_sel3 = st.columns(3)
        
        with col_sel1: 
            role = st.selectbox("Cargo", ["director", "actor", "actress"], help="Escolha a função")
        
        with col_sel2: 
            dec = st.selectbox("Década Específica", sorted(df_crew['decade'].unique(), reverse=True), help="Define o recorte temporal desta análise")
        
        with col_sel3: 
            metric = st.selectbox("Ordenar por", ["Nota Média (Crítica)", "Total Votos (Fama)"])
    
    st.markdown("---")

    # --- Lógica de Dados (Mantida igual) ---
    sort_col = 'mean_rating' if "Nota" in metric else 'total_votes'
    
    # Filtrar
    crew_sub = df_crew[(df_crew['category'] == role) & (df_crew['decade'] == dec)]
    top_15 = crew_sub.sort_values(by=sort_col, ascending=False).head(15)
    
    # --- GRÁFICOS (Seu código ajustado das barras amarelas) ---
    row_fame1, row_fame2 = st.columns([1, 1])
    
    with row_fame1:
        st.subheader(f"Top 15 Ranking")
        
        fig_bar = px.bar(
            top_15, 
            x=sort_col, 
            y='primaryName', 
            orientation='h',
            text=sort_col, 
            template=THEME_PLOTLY, 
            height=600,
            color_discrete_sequence=[COLOR_ACCENT] 
        )
        
        fig_bar.update_yaxes(categoryorder='total ascending', title=None)
        fig_bar.update_xaxes(showticklabels=False, title=None)
        
        text_format = '%{text:.2f}' if "Nota" in metric else '%{text:.2s}'
        
        fig_bar.update_traces(
            texttemplate=text_format,
            textposition='outside',
            textfont=dict(size=14, color='white'),
            cliponaxis=False 
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with row_fame2:
        if "Nota" in metric:
            scatter_y = 'total_votes'
            scatter_label = "Popularidade (Votos)"
            color_seq = ['#FF4B4B']
        else:
            scatter_y = 'mean_rating'
            scatter_label = "Qualidade (Nota Média)"
            color_seq = [COLOR_ACCENT] 

        st.subheader(f"Análise de {scatter_label.split(' ')[0]}")
        st.caption(f"Cruzando produtividade (X) com {scatter_label.lower()} (Y)")
        
        # Gráfico Dinâmico
        fig_scat_crew = px.scatter(
            top_15, 
            x='total_movies', 
            y=scatter_y, 
            hover_name='primaryName',
            text='primaryName',
            size='total_movies',
            template=THEME_PLOTLY, 
            height=600, 
            color_discrete_sequence=color_seq,
            log_x=True,
            labels={scatter_y: scatter_label, 'total_movies': 'Total de Filmes (Log)'}
        )
        
        fig_scat_crew.update_traces(textposition='top center')
        fig_scat_crew.update_layout(yaxis=dict(autorange=True))
        
        st.plotly_chart(fig_scat_crew, use_container_width=True)

    # Cards de Detalhes
    st.markdown("### 🏆 Destaques do Pódio")
    top_3 = top_15.head(3)
    c1, c2, c3 = st.columns(3)
    
    for i, (idx, row) in enumerate(top_3.iterrows()):
        col = [c1, c2, c3][i]
        with col:
            st.success(f"#{i+1} {row['primaryName']}")
            st.markdown(f"**Obra Prima:** {row['top_movie_title']}")
            st.caption(f"Ano: {int(row['top_movie_year'])} | Nota: {row['top_movie_rating']}")
            st.progress(row['mean_rating']/10)