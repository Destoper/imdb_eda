import streamlit as st
from config import COLOR_BG, COLOR_ACCENT, COLOR_SEC

def apply_custom_styles():
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