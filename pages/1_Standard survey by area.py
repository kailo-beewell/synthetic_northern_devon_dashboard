import branca.colormap as cm
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

# Import data
df_scores = pd.read_csv(
    'data/survey_data/standard_area_aggregate_scores_rag.csv')

# Import shapefile, filtering just to data we need
shp_nd = gpd.read_file('data/area_data/shapefile_nd/shp_nd.shp')
shapes = shp_nd[['MSOA21NM', 'geometry']].rename(columns={'MSOA21NM': 'msoa'})

#####################
# Page introduction #
#####################

st.title('Standard survey results by area')

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
            '''<p style='text-align: center; color: #19539A'>n<10 </p>''',
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

# Filter to chosen topic
chosen_result = df_scores[df_scores['variable_lab'] == chosen_variable_lab]

# Merge data on scores per MSOA with the MSOA shapefile
to_plot = pd.merge(shapes, chosen_result, on='msoa')

# Set centre manually
x_map = -4.075
y_map = 50.9765

# Initialise map
map = folium.Map(location=[y_map, x_map], zoom_start=10, tiles=None)

# Add tiles
folium.TileLayer(
    'CartoDB positron', name='Light Map', control=False).add_to(map)

# Create custom colormap (use slightly bolder versions of the HEX above
# as they get washed out/less distinct in colour-blind test due to opacity)
# Based on playing around with https://www.colorhexa.com/ and
# https://www.color-blindness.com/coblis-color-blindness-simulator/
# Red #FFCCCC --> #FFB3B3
# Yellow #FFE8BF --> #FFDFA6
# Green #B6E6B6 --> #A3DFA3 --> #90D890 --> #7DD27D
# Blue #DCE4FF --> #C3D0FF
colormap = cm.StepColormap(
    colors=['#FFB3B3', '#FFDFA6', '#7DD27D'],
    vmin=to_plot['mean'].min(),
    vmax=to_plot['mean'].max()
)
colormap.caption = f'Mean score for topic of "{chosen_variable_lab}"'


# Add colourful polygons
def style_function(x):
    return {'weight': 0.5,
            'color': 'black',
            'fillColor': colormap(x['properties']['mean'])
            if x['properties']['mean'] is not None
            else '#f6faff',
            'fillOpacity': 0.75}


def highlight_function(x):
    return {'fillColor': '#000000',
            'color': '#000000',
            'fillOpacity': 0.50,
            'weight': 0.1}


MSOA = folium.features.GeoJson(
    to_plot,
    style_function=style_function,
    control=False,
    highlight_function=highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        fields=['msoa', 'rag'],
        aliases=['MSOA:', 'Score:'],
        style=('''
background-color: white; color: #333333; font-family: arial;
font-size: 12px; padding: 10px;'''),
        sticky=True))
colormap.add_to(map)
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
