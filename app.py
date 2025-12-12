import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURAÇÃO DA PÁGINA E DESIGN SYSTEM ---
st.set_page_config(
    page_title="Dashboard de Cinema IMDb",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dicionário de Tradução
genre_translation = {
    "Action": "Ação", "Adventure": "Aventura", "Animation": "Animação",
    "Biography": "Biografia", "Comedy": "Comédia", "Crime": "Crime",
    "Documentary": "Documentário", "Drama": "Drama", "Family": "Família",
    "Fantasy": "Fantasia", "Film-Noir": "Noir", "History": "História",
    "Horror": "Terror", "Music": "Música", "Musical": "Musical",
    "Mystery": "Mistério", "Romance": "Romance", "Sci-Fi": "Ficção Científica",
    "Sport": "Esporte", "Thriller": "Suspense", "War": "Guerra", "Western": "Faroeste"
}

# Paleta e Tema
COLOR_BG = "#0e1117"
COLOR_ACCENT = "#f5c518"  
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
    /* Botões Sidebar */
    div.stButton > button:first-child {{
        width: 100%;
        background-color: #262730;
        color: white;
        border: 1px solid #444;
    }}
    div.stButton > button:hover {{
        border-color: #f5c518;
        color: #f5c518;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARREGAMENTO DE DADOS ---
@st.cache_data
def load_data():
    df = pd.read_csv('imdb_movies_final.csv')
    crew = pd.read_csv('imdb_crew_profiles.csv')
    
    # Limpeza preventiva
    df = df.dropna(subset=['genre'])
    
    return df, crew

try:
    df, df_crew = load_data()
except FileNotFoundError:
    st.error("⚠️ Arquivos CSV não encontrados. Verifique se 'imdb_movies_final.csv' e 'imdb_crew_profiles.csv' estão na pasta.")
    st.stop()

# --- 2.1 TRADUÇÃO GLOBAL ---
# Aplicamos a tradução na fonte, assim o filtro lateral já fica em Português
df['genre'] = df['genre'].map(genre_translation).fillna(df['genre'])

# --- 3. SIDEBAR (PAINEL DE CONTROLE) ---
with st.sidebar:
    st.title("🎬 Painel de Controle")
    st.markdown("---")

    min_year, max_year = int(df['startYear'].min()), int(df['startYear'].max())
    year_range = st.slider("📅 Período de Análise", min_year, max_year, (1960, 2023))

    # Agora o 'unique' já retorna em Português
    all_genres = sorted(df['genre'].unique())
    
    if 'selected_genres_state' not in st.session_state:
        # Defaults em Português para bater com a lista
        st.session_state['selected_genres_state'] = ['Ação', 'Drama', 'Ficção Científica', 'Terror', 'Romance', 'Comédia']

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

if not selected_genres:
    st.warning("⚠️ Por favor, selecione pelo menos um gênero no menu lateral.")
    st.stop()

# Aplicação dos Filtros Globais
df_filtered = df[
    (df['startYear'].between(year_range[0], year_range[1])) & 
    (df['genre'].isin(selected_genres))
].copy()

# A variável selected_genres_pt agora é redundante pois já está em PT, mas mantemos para compatibilidade
selected_genres_pt = selected_genres 

# --- 4. CABEÇALHO (KPIs) ---
st.title(f"📊 Dashboard de Cinema ({year_range[0]}-{year_range[1]})")

df_unique_movies = df_filtered.drop_duplicates(subset='tconst')

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total de Produções", f"{df_unique_movies['tconst'].count():,}")
k2.metric("Nota Média Global", f"{df_unique_movies['averageRating'].mean():.2f}")
k3.metric("Engajamento (Votos)", f"{(df_unique_movies['numVotes'].sum()/1000000):.1f}M")
k4.metric("Duração Média", f"{int(df_unique_movies['runtimeMinutes'].mean())} min")

best_year = df_unique_movies.groupby('startYear')['averageRating'].mean().idxmax()
k5.metric("Melhor Ano (Crítica)", int(best_year))

st.markdown("---")

# --- 5. ABAS DE NAVEGAÇÃO ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    " 📈 Evolução Temporal ", " 🎭 Análise por Gênero ", " ⏱️ Duração & Formato ", " 🌍 Mercado Global ", " 🌟 Hall da Fama "
])

# === ABA 1: EVOLUÇÃO TEMPORAL ===
with tab1:
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
    
    # --- GALERIA DE ÍCONES ---
    c_head1, c_head2 = st.columns([2, 1])
    with c_head1:
        st.subheader("🏆 Galeria: Destaques da Década")
        st.caption(f"Os nomes que definiram a era (Filtrado por: {', '.join(selected_genres_pt)})")
    with c_head2:
        ranking_metric = st.radio("Critério de Seleção:", ["Popularidade (Votos)", "Prestígio (Nota Média)"], horizontal=True)

    sort_col = 'total_votes' if "Votos" in ranking_metric else 'mean_rating'
    
    # Mapas de tradução para cards
    # Como já traduzimos a base principal, precisamos garantir que o mapa de filmes use PT também
    # Mas o título do filme continua igual, o gênero é que muda.
    # Criamos um mapa {Titulo: [Generos_PT]}
    
    df_temp_map = df.copy() # Já está traduzido
    # Agrupa gêneros em lista para o card
    df_temp_map_grouped = df_temp_map.groupby('primaryTitle')['genre'].apply(list).reset_index()
    movie_genre_map = df_temp_map_grouped.set_index('primaryTitle')['genre'].to_dict()

    def get_winner(decade, role, genre_list_pt, sort_by):
        candidates = df_crew[(df_crew['decade'] == decade) & (df_crew['category'] == role)].copy()
        
        def has_genre(movie_title):
            m_genres = movie_genre_map.get(movie_title, [])
            # Interseção entre gêneros do filme e gêneros selecionados
            return not set(m_genres).isdisjoint(genre_list_pt)
        
        candidates = candidates[candidates['top_movie_title'].apply(has_genre)]
        
        if not candidates.empty:
            return candidates.sort_values(by=sort_by, ascending=False).iloc[0]
        return None

    active_decades = sorted(df_filtered['decade'].unique(), reverse=True)

    for dec in active_decades:
        winner_dir = get_winner(dec, 'director', selected_genres_pt, sort_col)
        winner_act = get_winner(dec, 'actor', selected_genres_pt, sort_col)
        winner_actress = get_winner(dec, 'actress', selected_genres_pt, sort_col)
        
        if winner_dir is not None or winner_act is not None or winner_actress is not None:
            st.markdown(f"### 🗓️ Década de {dec}")
            c1, c2, c3 = st.columns(3)
            
            def draw_card(col, row, role_icon, role_name):
                with col:
                    if row is not None:
                        # Busca lista de gêneros reais (já em PT)
                        genres_real = movie_genre_map.get(row['top_movie_title'], ["N/A"])
                        # Junta os 2 primeiros
                        genres_str = " • ".join(genres_real[:2])
                        
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

            draw_card(c1, winner_dir, "🎥", "Direção")
            draw_card(c2, winner_act, "🕴️", "Ator")
            draw_card(c3, winner_actress, "💃", "Atriz")
            st.divider()

# === ABA 2: ANÁLISE POR GÊNERO ===
with tab2:
    st.info("ℹ️ **Nota Metodológica:** Filmes com múltiplos gêneros (ex: 'Ação, Sci-Fi') são contabilizados individualmente em cada categoria correspondente.")
    
    # Preparação dos dados
    genre_stats = df_filtered.groupby('genre').agg(
        count=('tconst', 'nunique'), 
        rating=('averageRating', 'mean'), 
        votes=('numVotes', 'mean')
    ).reset_index()

    # GRÁFICO 1
    st.subheader("Popularidade vs. Prestígio")
    st.caption("O tamanho da bolha representa o volume de filmes por gênero.")
    fig_bubble = px.scatter(genre_stats, x="votes", y="rating", size="count", color="genre", 
                            hover_name="genre", text="genre", template=THEME_PLOTLY, height=500,
                            labels={'votes': 'Média de Votos (Popularidade)', 'rating': 'Nota Média (Crítica)', 'count': 'Qtd. Filmes'})
    fig_bubble.update_traces(textposition='top center')
    st.plotly_chart(fig_bubble, use_container_width=True)

    st.markdown("---")

    # Lógica Altura Dinâmica
    n_genres = df_filtered['genre'].nunique()
    n_rows = (n_genres // 3) + (1 if n_genres % 3 > 0 else 0)
    dynamic_height = max(500, n_rows * 250) 

    # GRÁFICO 2
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

    # GRÁFICO 3
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

# === ABA 3: DURAÇÃO & FORMATO ===
with tab3:
    def cat_dur(x):
        if x < 90: return 'Curto (<90m)'
        elif x <= 120: return 'Padrão (90-120m)'
        elif x <= 150: return 'Longo (120-150m)'
        else: return 'Épico (>150m)'
    
    df_filtered = df_filtered.copy()
    df_filtered['duration_class'] = df_filtered['runtimeMinutes'].apply(cat_dur)
    
    # Ordem lógica das categorias
    order = ['Curto (<90m)', 'Padrão (90-120m)', 'Longo (120-150m)', 'Épico (>150m)']
    palette = px.colors.sequential.Plasma
    color_map = {'Curto (<90m)': palette[1], 'Padrão (90-120m)': palette[3], 'Longo (120-150m)': palette[5], 'Épico (>150m)': palette[7]}

    row1_1, row1_2 = st.columns(2)
    with row1_1:
        st.subheader("Evolução do Formato")
        df_dur = df_filtered.groupby(['decade', 'duration_class']).size().reset_index(name='count')
        df_dur['pct'] = df_dur['count'] / df_dur.groupby('decade')['count'].transform('sum')
        
        fig_stack = px.area(df_dur, x='decade', y='pct', color='duration_class', 
                            category_orders={'duration_class': order}, color_discrete_map=color_map, 
                            labels={'pct': 'Proporção (%)', 'decade': 'Década'},
                            template=THEME_PLOTLY, height=400)
        st.plotly_chart(fig_stack, use_container_width=True)

    with row1_2:
        st.subheader("Engajamento por Duração")
        df_eng = df_filtered.groupby('duration_class')['numVotes'].mean().reset_index()
        fig_eng = px.bar(df_eng, x='duration_class', y='numVotes', color='duration_class', 
                         category_orders={'duration_class': order}, color_discrete_map=color_map, 
                         labels={'numVotes': 'Média de Votos', 'duration_class': 'Categoria'},
                         template=THEME_PLOTLY, height=400)
        st.plotly_chart(fig_eng, use_container_width=True)

    st.subheader("Densidade de Notas por Duração")
    fig_rating_dur = px.violin(df_filtered, x='duration_class', y='averageRating', color='duration_class', 
                               category_orders={'duration_class': order}, color_discrete_map=color_map, 
                               box=True, points=False, labels={'averageRating': 'Nota IMDb', 'duration_class': 'Duração'},
                               template=THEME_PLOTLY, height=400)
    st.plotly_chart(fig_rating_dur, use_container_width=True)

    st.subheader("Dispersão Detalhada (Amostra)")
    fig_scatter = px.scatter(df_filtered.sample(min(2000, len(df_filtered))), x='runtimeMinutes', y='averageRating', 
                             color='genre', opacity=0.6, template=THEME_PLOTLY, height=400, 
                             labels={'runtimeMinutes': 'Duração (min)', 'averageRating': 'Nota IMDb'},
                             title="Amostra aleatória de 2.000 filmes")
    fig_scatter.update_layout(xaxis_range=[60, 200])
    st.plotly_chart(fig_scatter, use_container_width=True)

# === ABA 4: MERCADO GLOBAL ===
with tab4:
    df_geo = df_filtered.drop_duplicates(subset='tconst')
    st.subheader("🌍 Alcance de Mercado & Distribuição")
    st.caption("Análise baseada na quantidade de países onde o filme foi oficialmente distribuído.")

    st.subheader("Comparativo de Mercado: 🇺🇸 vs 🇧🇷")
    c_kpi1, c_kpi2, _ = st.columns(3)

    total_filmes = len(df_geo)
    if total_filmes > 0 and 'released_in_br' in df_geo.columns:
        br_count = df_geo[df_geo['released_in_br'] == True].shape[0]
        us_count = df_geo[df_geo['released_in_us'] == True].shape[0]
        
        br_pct = (br_count / total_filmes) * 100
        us_pct = (us_count / total_filmes) * 100
        ratio = us_count / br_count if br_count > 0 else 0
        
        c_kpi1.metric("Lançados no Brasil", f"{br_count:,}", f"{br_pct:.1f}% do total")
        c_kpi2.metric("Lançados nos EUA", f"{us_count:,}", f"{us_pct:.1f}% do total")
        
        st.info(f"📊 Estatisticamente, o mercado americano recebe **{ratio:.1f}x** mais filmes (do recorte atual) do que o mercado brasileiro.")
    else:
        st.warning("Dados de mercado indisponíveis para este cálculo.")
    
    col_m1, col_m2 = st.columns([1, 1])
    
    with col_m1:
        st.markdown("#### Grau de Globalização")
        if 'distribution_count' in df_geo.columns:
            fig_hist_dist = px.histogram(
                df_geo, 
                x='distribution_count', 
                nbins=30,
                title="Distribuição de Filmes por Nº de Países",
                labels={'distribution_count': 'Países Alcançados', 'count': 'Qtd. Filmes'},
                color_discrete_sequence=[COLOR_ACCENT], 
                template=THEME_PLOTLY,
                height=400
            )
            fig_hist_dist.update_layout(bargap=0.1)
            st.plotly_chart(fig_hist_dist, use_container_width=True)
        else:
            st.error("Erro nos dados de distribuição.")

    with col_m2:
        st.markdown("#### Alcance vs. Qualidade")
        if 'market_reach' in df_geo.columns:
            order_reach = ['Local (1 país)', 'Regional (2-5)', 'Internacional (6-20)', 'Global Blockbuster (20+)']
            
            # Cores consistentes com Aba 3
            palette = px.colors.sequential.Plasma
            color_map_reach = {
                'Local (1 país)': palette[1],
                'Regional (2-5)': palette[3],
                'Internacional (6-20)': palette[5],
                'Global Blockbuster (20+)': palette[7]
            }

            fig_box_reach = px.box(
                df_geo,
                x='market_reach',
                y='averageRating',
                color='market_reach',
                category_orders={'market_reach': order_reach},
                color_discrete_map=color_map_reach,
                title="Distribuição de Notas por Categoria de Alcance",
                labels={'market_reach': 'Categoria de Alcance', 'averageRating': 'Nota IMDb'},
                template=THEME_PLOTLY,  
                height=400
            )
            st.plotly_chart(fig_box_reach, use_container_width=True)
        else:
            st.error("Erro nos dados de alcance.")
    
    st.divider()

    st.subheader(" Exportabilidade por Gênero")
    st.caption("Quais gêneros viajam mais? Média de países alcançados por categoria.")

    # 1. Preparação
    df_export = df_filtered.groupby('genre').agg(
        avg_reach=('distribution_count', 'mean'),
        avg_rating=('averageRating', 'mean'),
        count=('tconst', 'count')
    ).reset_index()

    # 2. Filtro de Relevância (>50 filmes)
    df_export = df_export[df_export['count'] > 50].sort_values('avg_reach', ascending=True)

    # 3. Gráfico
    fig_passport = px.bar(
        df_export, 
        x='avg_reach', 
        y='genre', 
        orientation='h',
        text='avg_reach',
        labels={'avg_reach': 'Alcance Médio (Nº Países)', 'genre': 'Gênero'},
        template=THEME_PLOTLY,
        height=600
    )
    fig_passport.update_traces(marker_color=COLOR_ACCENT, texttemplate='%{text:.1f}', textposition='outside')
    fig_passport.update_layout(xaxis_title="Média de Países por Lançamento")
    
    # Linha Média
    avg_global = df_geo['distribution_count'].mean()
    
    fig_passport.add_vline(
        x=avg_global, 
        line_width=2, line_dash="dash", line_color="white", 
        annotation_text=f"Média Geral: {avg_global:.1f}", 
        annotation_position="top right", 
        annotation=dict(font=dict(size=12, color="black"), bgcolor="#f0f0f0", opacity=0.9, bordercolor="white", borderwidth=1, yshift=-10)
    )

    st.plotly_chart(fig_passport, use_container_width=True)

# === ABA 5: HALL DA FAMA ===
with tab5:
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

    # Lógica
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
        # Inversão inteligente
        scatter_y = 'total_votes' if "Nota" in metric else 'mean_rating'
        label_y = "Popularidade (Votos)" if "Nota" in metric else "Qualidade (Nota Média)"
        color_seq = ["#842AF8"] # Roxo para contraste

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

    # Cards
    st.markdown("### 🏆 Pódio da Década")
    top_3 = top_15.head(3)
    c1, c2, c3 = st.columns(3)
    
    for i, (idx, row) in enumerate(top_3.iterrows()):
        with [c1, c2, c3][i]:
            st.success(f"#{i+1} {row['primaryName']}")
            st.markdown(f"**Obra-Prima:** {row['top_movie_title']}")
            st.caption(f"Ano: {int(row['top_movie_year'])} | Nota: {row['top_movie_rating']}")
            st.progress(row['mean_rating']/10)