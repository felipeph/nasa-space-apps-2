import streamlit as st
from datetime import datetime
import folium
from folium.plugins import HeatMap
import pandas as pd
from streamlit_folium import st_folium

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(
    page_title="GeoGuardians",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def load_date_csv(date):
    date = ''.join(str(date).split('-'))
    url = f"https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/diario/Brasil/focos_diario_br_{date}.csv"
    df = pd.read_csv(url)
    return df

RADIUS = 2
BLUR = 1

params = st.experimental_get_query_params()

date_input = params["date"][0]

date_obj = datetime.strptime(date_input, "%d/%m/%Y")

date = date_obj.strftime("%Y-%m-%d")


df = load_date_csv(date)


latitude_media = df['lat'].mean()
longitude_media = df['lon'].mean()

# Criar o mapa
mapa = folium.Map(location=[latitude_media, longitude_media], zoom_start=4)

heatmap_data = df[['lat', 'lon']].values
HeatMap(heatmap_data, radius=RADIUS, blur=BLUR).add_to(mapa)

display_map = st.container()
with display_map:
    day_map = st_folium(fig=mapa, use_container_width=True)
