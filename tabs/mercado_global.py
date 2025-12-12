import streamlit as st
import plotly.express as px
from config import COLOR_ACCENT, THEME_PLOTLY

def render_mercado_global(df_filtered):
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

    st.subheader("Exportabilidade por Gênero")
    st.caption("Quais gêneros viajam mais? Média de países alcançados por categoria.")

    df_export = df_filtered.groupby('genre').agg(
        avg_reach=('distribution_count', 'mean'),
        avg_rating=('averageRating', 'mean'),
        count=('tconst', 'count')
    ).reset_index()

    df_export = df_export[df_export['count'] > 50].sort_values('avg_reach', ascending=True)

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
    
    avg_global = df_geo['distribution_count'].mean()
    
    fig_passport.add_vline(
        x=avg_global, 
        line_width=2, line_dash="dash", line_color="white", 
        annotation_text=f"Média Geral: {avg_global:.1f}", 
        annotation_position="top right", 
        annotation=dict(font=dict(size=12, color="black"), bgcolor="#f0f0f0", opacity=0.9, bordercolor="white", borderwidth=1, yshift=-10)
    )

    st.plotly_chart(fig_passport, use_container_width=True)