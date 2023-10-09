# Libraries
import streamlit as st
import folium
from folium.plugins import HeatMap, FastMarkerCluster
import geopandas as gpd
import pandas as pd
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import pytz
import plotly.express as px

# Config to correct https verification
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(
    page_title="GeoGuardians",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
            <style>
                div[data-testid="collapsedControl"] {
            display: none
    }
</style>
    """,
    unsafe_allow_html=True
)


timezone_brazil = pytz.timezone('America/Sao_Paulo')


#params = st.experimental_get_query_params()
#st.write(params)

today = datetime.now(timezone_brazil) - timedelta(days=1)
interval = timedelta(days=30)
first_day = today - interval


date = st.date_input('Select a date', value=today)

# Heatmap Configs
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
states_list = df['estado'].unique()
states_list = states_list.tolist()
states_list = sorted(states_list)
marked_states = st.multiselect('Select States', options=states_list)
if marked_states:
    dfs_list = []
    for state in marked_states:
        mask = df['estado'] == state
        dfs_list.append(df[mask])
    df = pd.concat(dfs_list, axis=0)

#st.write(states_list)

#st.write(df)

df_state = df.groupby('estado').size().reset_index(name='num_ocorrencias')

df_state = df_state.sort_values(by='num_ocorrencias', ascending=True)

#st.write(df_state)

fig_state = px.bar(df_state, x='num_ocorrencias', y='estado', orientation='h', 
             title='Wildfires by State',
             labels={'num_ocorrencias': 'Number of Wildfires', 'estado': 'State'},
             color_discrete_sequence=['#8B0000'],
             )

fig_state.update_layout(height=700)


tab_states, tab_cities = st.tabs(["States", "Top 10 Cities"])

with tab_states:
    st.plotly_chart(fig_state, use_container_width=True)

df_cities = df.groupby('municipio').size().reset_index(name='num_ocorrencias')

df_cities = df_cities.sort_values(by='num_ocorrencias', ascending=True)

df_cities = df_cities.tail(10)

#st.write(df_state)

fig_cities = px.bar(df_cities, x='num_ocorrencias', y='municipio', orientation='h', 
             title='Wildfires by City',
             labels={'num_ocorrencias': 'Number of Wildfires', 'municipio': 'City'},
             color_discrete_sequence=['#8B0000'],)

fig_cities.update_layout(height=700)



with tab_cities:
    st.plotly_chart(fig_cities, use_container_width=True)
    
df_county = df.groupby('municipio').size().reset_index(name='num_ocorrencias')

st.write(df_county)






# mean_lat = df['lat'].mean()
# mean_lon = df['lon'].mean()

# # Map Creation
# map = folium.Map(location=[mean_lat, mean_lon], zoom_start=4)

# heatmap_data = df[['lat', 'lon']].values
# heatmap = HeatMap(heatmap_data, radius=radius, blur=blur).add_to(map)
# fastmarker = FastMarkerCluster(heatmap_data).add_to(map)


# @st.cache_data
# def read_shape_files():
#     shp_states = gpd.read_file(r'data/shapes/BR_UF_2022.shp', encoding='utf-8')
#     shp_states.crs = "EPSG:4326"
#     return shp_states


# def title_without_middlearticles(name):
#     name = name.split(' ')
#     exceptions = ['DA', 'DE', 'DO']
#     newtitle = ''
#     for i in name:
#         if i in exceptions:
#             newtitle += i.lower()
#         else:
#             newtitle += i.title()
#         newtitle += ' '
#     return newtitle[:len(newtitle) - 1]


# shp_states = read_shape_files()
# if marked_states:
#     for state in marked_states:
#         mask = shp_states['NM_UF'] == title_without_middlearticles(state)
#         info_state = folium.features.GeoJson(
#             data=shp_states[mask]['geometry'],
#             style_function=lambda feature:
#             {
#                 'color': 'blue',
#                 'weight': 2
#             }
#         )
#         folium.Popup(f'{state}\n'
#                      f'Number of Incidents: {df["estado"].value_counts()[state]}\n').add_to(info_state)
#         info_state.add_to(map)

# day_map = st_folium(fig=map, use_container_width=True)
