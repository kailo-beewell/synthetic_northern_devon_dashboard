import folium
import geopandas as gpd
from kailo_beewell_dashboard.map import (
    area_intro, choose_topic)
from kailo_beewell_dashboard.page_setup import (
    page_footer, page_setup)
from kailo_beewell_dashboard.reuse_text import caution_comparing
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

##########
# Set-up #
##########

page_setup('public')

# Import data to session state if not already (this will later be done
# upon opening app on first page, with CSV data in TIDB Cloud)
if 'scores_rag' not in st.session_state:
    st.session_state.scores_rag = pd.read_csv(
        'data/survey_data/standard_area_aggregate_scores_rag.csv')
if 'shapes' not in st.session_state:
    # Import shapefile
    shp_nd = gpd.read_file('data/area_data/shapefile_nd/shp_nd.shp')
    # Filter to required columns (helps map speed)
    shp_nd = (shp_nd[['MSOA21NM', 'geometry']]
              .rename(columns={'MSOA21NM': 'msoa'}))
    # Simplify geometry (helps map speed)
    shp_nd['geometry'] = shp_nd['geometry'].simplify(1)
    # Save to session state
    st.session_state.shapes = shp_nd

# As we play around this one, import it from session state
df_scores = st.session_state.scores_rag

# Write title, introduction and key to RAG
area_intro()

st.subheader('Results by MSOA')

# Create selectbox and get chosen topic
chosen_variable_lab = choose_topic(df_scores)


#######
# Map #
#######


def rag_colormap(feature):
    '''
    Function to produce the RAG colourmap

    Parameters
    ----------
    feature : string
        e.g. x['properties']['mean']
    '''
    if feature == 'below':
        return '#FFB3B3'
    elif feature == 'average':
        return '#FFDFA6'
    elif feature == 'above':
        return '#7DD27D'
    else:
        return '#F6FAFF'


def style_function(x):
    '''
    Style function used to produce colourful polygons in map
    Uncertain on what exactly the positional argument is

    Returns
    -------
    style : dictionary
        Dictionary with attributes of polygons
    '''
    style = {'weight': 0.5,
             'color': 'black',
             'fillColor': rag_colormap(x['properties']['rag']),
             'fillOpacity': 0.75}
    return style


def highlight_function(x):
    '''
    Highlight function to change fill colour when hover mouse over polygon
    Requires positional argument (as GeoJson will provide it one)

    Returns
    -------
    highlight : dictionary
        Dictionary with attributes of polygons when hovered over
    '''
    highlight = {'fillColor': '#32112F',
                 'color': '#32112F',
                 'fillOpacity': 0.50,
                 'weight': 0.1}
    return highlight


def create_map(geo_df):
    '''
    Produce Folium map on Streamlit app

    Parameters
    ----------
    geo_df : geopandas dataframe
        Containing geometries and values for colouring the geometries
    '''
    # Set centre manually
    x_map = -4.075
    y_map = 50.955

    # Initialise map
    map = folium.Map(location=[y_map, x_map], zoom_start=10, tiles=None,
                     scrollWheelZoom=False)

    # Add tiles (allows us to superimmpose images over the map tiles)
    folium.TileLayer(
        'CartoDB positron', name='Light Map', control=False).add_to(map)

    # Add polygons to the map
    MSOA = folium.features.GeoJson(
        data=geo_df,
        # Function mapping GeoJson Feature to style dict (normal + hover)
        style_function=style_function,
        highlight_function=highlight_function,
        # Whether layer will be included in layer controls
        control=False,
        # Whether to Zoom in on polygon when clicked
        zoom_on_click=False,
        # Display text when hovering over object
        tooltip=folium.features.GeoJsonTooltip(
            fields=['msoa', 'rag'],
            aliases=['MSOA:', 'Score:'],
            style=('''
    background-color: white; color: #05291F; font-family: sans-serif;
    font-size: 12px; padding: 10px;'''),
            sticky=True))
    map.add_child(MSOA)

    # Display map on streamlit
    st_folium(map, width=700, height=700)


# Filter to chosen topic then filter to only used column (helps map speed)
chosen_result = df_scores[df_scores['variable_lab'] == chosen_variable_lab]
msoa_rag = chosen_result[['msoa', 'rag']]

# Merge data on scores per MSOA with the MSOA shapefile
to_plot = pd.merge(st.session_state.shapes, msoa_rag, on='msoa')

create_map(to_plot)

# Add caveat for interpretation
st.subheader('Comparing between areas')
st.markdown(caution_comparing('area'))

page_footer('schools in Northern Devon')
