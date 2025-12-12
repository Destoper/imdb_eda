import streamlit as st
import plotly.express as px
from config import THEME_PLOTLY

def render_duracao_formato(df_filtered):
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