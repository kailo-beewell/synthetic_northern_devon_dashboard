from kailo_beewell_dashboard.explore_results import (
    create_topic_dict)
from kailo_beewell_dashboard.page_setup import (
    page_footer, page_setup)
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import branca.colormap as cm

page_setup('public')

# Import data
df_scores = pd.read_csv(
    'data/survey_data/standard_area_aggregate_scores_rag.csv')

# Import shapefile, filtering just to data we need
shp_nd = gpd.read_file('data/area_data/shapefile_nd/shp_nd.shp')
shapes = shp_nd[['MSOA21NM', 'geometry']].rename(columns={'MSOA21NM': 'msoa'})

##################
# Getting topics #
##################

# DUPLICATION WITH STANDARD SURVEY, PUBLIC BY AREA, PUBLIC BY CHARACTERISTIC
# Create dictionary of topics
topic_dict = create_topic_dict(df_scores)

# If session state doesn't contain chosen variable, default to Autonomy
# If it does (i.e. set from Summary page), use that
if 'chosen_variable_lab' not in st.session_state:
    st.session_state['chosen_variable_lab'] = 'Autonomy'

# Convert topics to list and find index of the session state variable
topic_list = list(topic_dict.keys())
default = topic_list.index(st.session_state['chosen_variable_lab'])

#####################
# Page introduction #
#####################

st.title('Standard survey results by area')

# Select topic
chosen_variable_lab = st.selectbox(
    '**Topic:**', topic_dict.keys(), index=default)

# Convert from variable_lab to variable
chosen_variable = topic_dict[chosen_variable_lab]

#######
# Map #
#######

# st.map()

# Filter to chosen topic
chosen_result = df_scores[df_scores['variable_lab'] == chosen_variable_lab]

# Merge data on scores per MSOA with the MSOA shapefile
to_plot = pd.merge(shapes, chosen_result, on='msoa')

# Find the centre of our features
# find_centre = shapes.to_crs('+proj=cea')
# x_map = find_centre.centroid.to_crs('4326').x.mean()
# y_map = find_centre.centroid.to_crs('4326').y.mean()

# Set centre manually
x_map = -4.076126
y_map = 50.947349

# Initialise map
map = folium.Map(location=[y_map, x_map], zoom_start=10, tiles=None)

# Add tiles
folium.TileLayer(
    'CartoDB positron', name='Light Map', control=False).add_to(map)

# Create custom colormap
colormap = cm.StepColormap(
    colors=['#FFCCCC', '#FFE8BF', '#B6E6B6'],
    vmin=to_plot['mean'].min(),
    vmax=to_plot['mean'].max()
)
colormap.caption = f'Mean score for topic of "{chosen_variable_lab}"'

# Add colourful polygons
style_function = lambda x: {'weight': 0.5,
                            'color': 'black',
                            'fillColor': colormap(x['properties']['mean']),
                            'fillOpacity': 0.75}
highlight_function = lambda x: {'fillColor': '#000000',
                                'color': '#000000',
                                'fillOpacity': 0.50,
                                'weight': 0.1}
MSOA = folium.features.GeoJson(
    to_plot,
    style_function=style_function,
    control=False,
    highlight_function=highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        fields=['msoa', 'mean'],
        aliases=['MSOA', 'Mean score'],
        style=('''
background-color: white; color: #333333; font-family: arial;
font-size: 12px; padding: 10px;'''),
        sticky=True))
colormap.add_to(map)
map.add_child(MSOA)

# Display map on streamlit
st_map = st_folium(map, width=700, height=700)

page_footer('schools in Northern Devon')
