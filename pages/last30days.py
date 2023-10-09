import streamlit as st
from datetime import datetime, timedelta
import folium
from folium.plugins import HeatMap
import pandas as pd
from streamlit_folium import st_folium
import pytz
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

timezone_brazil = pytz.timezone('America/Sao_Paulo')


#params = st.experimental_get_query_params()
#st.write(params)

today = datetime.now(timezone_brazil) - timedelta(days=1)
interval = timedelta(days=29)
first_day = today - interval

st.markdown("""
            <style>
                div[data-testid="collapsedControl"] {
            display: none
    }
</style>
    """,
    unsafe_allow_html=True
)


select_date = st.container()

st.write(today)
st.write(first_day)

with select_date:
    try:
        date = st.date_input('Select a date')
    except:
        today = today - timedelta(days=1)
        first_day = today - interval
        date = st.date_input('Select a date', min_value=first_day, max_value=today)


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
