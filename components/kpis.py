import streamlit as st

def render_kpis(df_filtered, year_range):
    st.title(f"📊 Dashboard de Cinema IMDb ({year_range[0]}-{year_range[1]})")

    df_unique_movies = df_filtered.drop_duplicates(subset='tconst')

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total de Produções", f"{df_unique_movies['tconst'].count():,}")
    k2.metric("Nota Média Global", f"{df_unique_movies['averageRating'].mean():.2f}")
    k3.metric("Engajamento (Votos)", f"{(df_unique_movies['numVotes'].sum()/1000000):.1f}M")
    k4.metric("Duração Média", f"{int(df_unique_movies['runtimeMinutes'].mean())} min")

    best_year = df_unique_movies.groupby('startYear')['averageRating'].mean().idxmax()
    k5.metric("Melhor Ano (Crítica)", int(best_year))