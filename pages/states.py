import streamlit as st
import folium
from folium.plugins import HeatMap, FastMarkerCluster
import geopandas as gpd
import pandas as pd
from streamlit_folium import st_folium

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

st.title('Focos por dia')
date = st.date_input('Escolha o Dia de Análise dos Focos')

radius = 2
blur = 1


@st.cache_data
def load_date_csv_inpe(date):
    date = ''.join(str(date).split('-'))
    url = f"https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/diario/Brasil/focos_diario_br_{date}.csv"
    df = pd.read_csv(url)
    return df


df = load_date_csv_inpe(date)
# Filters
lista_estados = df['estado'].unique()
estados_marcados = st.multiselect('Selecionar Estados', options=lista_estados)
if estados_marcados:
    lista_dfs = []
    df_estados = pd.DataFrame()
    for estado in estados_marcados:
        mask = df['estado'] == estado
        lista_dfs.append(df[mask])
    df = pd.concat(lista_dfs, axis=0)

lista_municipios = df['municipio'].unique()
municipios_marcados = st.multiselect('Selecionar Municipios', options=lista_municipios)
if municipios_marcados:
    lista_dfs = []
    df_municipios = pd.DataFrame()
    for municipio in municipios_marcados:
        mask = df['municipio'] == municipio
        lista_dfs.append(df[mask])
    df = pd.concat(lista_dfs, axis=0)

latitude_media = df['lat'].mean()
longitude_media = df['lon'].mean()

# Map Creation
mapa = folium.Map(location=[latitude_media, longitude_media], zoom_start=4)

heatmap_data = df[['lat', 'lon']].values
heatmap = HeatMap(heatmap_data, radius=radius, blur=blur).add_to(mapa)
fastmarker = FastMarkerCluster(heatmap_data).add_to(mapa)


@st.cache_data
def read_shape_files():
    shape_estados_br = gpd.read_file('BR_UF_2022.shp', encoding='utf-8')
    # shape_estados_br = shape_estados_br.explode()
    shape_estados_br.crs = "EPSG:4326"
    shape_municipios_br = gpd.read_file('BR_Municipios_2022.shp', encoding='utf-8')
    shape_municipios_br.crs = "EPSG:4326"
    return shape_estados_br, shape_municipios_br


def title_without_middlearticles(name):
    name = name.split(' ')
    exceptions = ['DA', 'DE', 'DO']
    newtitle = ''
    for i in name:
        if i in exceptions:
            newtitle += i.lower()
        else:
            newtitle += i.title()
        newtitle += ' '
    return newtitle[:len(newtitle) - 1]


shape_estados_br, shape_municipios_br = read_shape_files()
if estados_marcados:
    for estado in estados_marcados:
        mask = shape_estados_br['NM_UF'] == title_without_middlearticles(estado)
        info_estado = folium.features.GeoJson(
            data=shape_estados_br[mask]['geometry'],
            style_function=lambda feature:
            {
                'color': 'blue',
                'weight': 2
            }
        )
        folium.Popup(f'{estado}\n'
                     f'Focos: {df["estado"].value_counts()[estado]}\n').add_to(info_estado)
        info_estado.add_to(mapa)
if municipios_marcados:
    for municipio in municipios_marcados:
        mask = shape_municipios_br['NM_MUN'] == title_without_middlearticles(municipio)
        info_mun = folium.features.GeoJson(
            data=shape_municipios_br[mask]['geometry'],
            style_function=lambda feature:
            {
                'color': 'red',
                'weight': 2
            }
        )
        info_mun.add_to(mapa)
day_map = st_folium(fig=mapa, use_container_width=True)
