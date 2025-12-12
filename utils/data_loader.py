import streamlit as st
import pandas as pd
from config import GENRE_TRANSLATION

@st.cache_data
def load_data():
    df = pd.read_csv('imdb_movies_final.csv')
    crew = pd.read_csv('imdb_crew_profiles.csv')
    
    df = df.dropna(subset=['genre'])
    df['genre'] = df['genre'].map(GENRE_TRANSLATION).fillna(df['genre'])
    
    return df, crew