import streamlit as st
import datetime
import folium
from folium.plugins import HeatMap
import pandas as pd
from streamlit_folium import st_folium

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

@st.cache_data
def load_date_csv(date):
    date = ''.join(str(date).split('-'))
    url = f"https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/diario/Brasil/focos_diario_br_{date}.csv"
    df = pd.read_csv(url)
    return df

RADIUS = 2
BLUR = 1

params = st.experimental_get_query_params()

st.write(params)

today = datetime.datetime.now()

interval = datetime.timedelta(days=30)

first_day = today - interval

st.title('Focos por dia')

select_date = st.container()

with select_date:
    date = st.date_input('Escolha o Dia de Análise dos Focos', min_value=first_day, max_value=today)



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
