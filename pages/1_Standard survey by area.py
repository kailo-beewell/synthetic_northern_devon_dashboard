import folium
import geopandas as gpd
from kailo_beewell_dashboard.explore_results import (
    create_topic_dict)
from kailo_beewell_dashboard.page_setup import (
    blank_lines, page_footer, page_setup)
from kailo_beewell_dashboard.stylable_container import stylable_container
from kailo_beewell_dashboard.summary_rag import rag_intro_column
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

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

#####################
# Page introduction #
#####################

st.title('Standard survey')

blank_lines(1)
view = st.selectbox('What would you like to view?', [
    'Explore results by area',
    'Explore results by characteristics',
    'Who took part?'])
blank_lines(2)

st.subheader('Introduction')
st.markdown('''This page shows how the results from young people varied
            across Northern Devon by Middle Layer Super Output Area (MSOA).''')

# Write interpretation of each of the RAG boxes
rag_descrip_below = '''
This means that the average scores for young people in that MSOA are **worse**
than average scores for young people in other MSOAs.'''
rag_descrip_average = '''
This means that the average scores for young people in that MSOA are
**similar** than average scores for young people in other MSOAs.'''
rag_descrip_above = '''
This means that the average scores for young people in that MSOA are **better**
than average scores for young people in other MSOAs.'''
rag_descrip_small = '''
This means that **less than ten** young people in an MSOA that completed the
questions for this topic, so the results cannot be shown.'''

rag_intro_column('below', rag_descrip_below)
rag_intro_column('average', rag_descrip_average)
rag_intro_column('above', rag_descrip_above)

# Custom for n<10 as uses different colour to summary
cols = st.columns(2)
with cols[0]:
    with stylable_container(
        key='small',
        css_styles=f'''
    {{
        background-color: {'#f6faff'};
        border-radius: 0.5rem;
        padding: 0px
    }}''',):
        blank_lines(1)
        st.markdown(
            '''<p style='text-align: center; color: #6B7787;'>n<10 </p>''',
            unsafe_allow_html=True)
        blank_lines(1)
with cols[1]:
    st.markdown(rag_descrip_small)

##################
# Getting topics #
##################

st.subheader('Results by MSOA')

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

# Select topic
chosen_variable_lab = st.selectbox(
    '**Topic:**', topic_dict.keys(), index=default)

# Convert from variable_lab to variable
chosen_variable = topic_dict[chosen_variable_lab]

#######
# Map #
#######

# Filter to chosen topic then filter to only used column (helps map speed)
chosen_result = df_scores[df_scores['variable_lab'] == chosen_variable_lab]
msoa_rag = chosen_result[['msoa', 'rag']]

# Merge data on scores per MSOA with the MSOA shapefile
to_plot = pd.merge(st.session_state.shapes, msoa_rag, on='msoa')

# Set centre manually
x_map = -4.075
y_map = 50.955

# Initialise map
map = folium.Map(location=[y_map, x_map], zoom_start=10, tiles=None,
                 scrollWheelZoom=False)

# Add tiles (allows us to superimmpose images over the map tiles)
folium.TileLayer(
    'CartoDB positron', name='Light Map', control=False).add_to(map)


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


# Add polygons to the map
MSOA = folium.features.GeoJson(
    data=to_plot,
    # Function mapping GeoJson Feature to a style dict (normal + mouse events)
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
st_map = st_folium(map, width=700, height=700)

# Add caveat for interpretation
st.subheader('Comparing between areas')
st.markdown('''
Always be mindful when making comparisons between different areas. There are
a number of factors that could explain differences in scores (whether you are
above average, average, or below average). These include:
* Random chance ('one-off' findings).
* Differences in the socio-economic characteristics of young people and the
areas where they live (e.g. income, education, ethnicity, access to services
and amenities).
* The number of young people taking part - areas where fewer people took part
are more likely to have more "extreme" results (i.e. above or below average),
whilst area with a larger number of participants are more likely to
see average results

It's also worth noting that the score will only include results from young
people who completed each of the questions used to calculate that topic - so
does not include any reflection of results from pupils who did not complete
some or all of the questions for that topic.''')

page_footer('schools in Northern Devon')
