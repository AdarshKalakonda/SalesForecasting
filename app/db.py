import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

@st.cache_resource
def get_engine():
    neon_url = os.getenv("NEON_DB_URL")
    if neon_url:
        return create_engine(neon_url)

    password = quote_plus(os.getenv("DB_PASS", ""))
    url = (
        f"postgresql+psycopg2://"
        f"{os.getenv('DB_USER')}:{password}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
        f"/{os.getenv('DB_NAME')}"
    )
    return create_engine(url)
