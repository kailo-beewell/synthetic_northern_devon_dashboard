import json
from kailo_beewell_dashboard.explore_results import choose_topic
from kailo_beewell_dashboard.map import area_intro
from kailo_beewell_dashboard.page_setup import (
    blank_lines, page_footer, page_setup)
from kailo_beewell_dashboard.reuse_text import caution_comparing
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

##########
# Set-up #
##########

page_setup('public')

# Import data to session state if not already (this will later be done
# upon opening app on first page, with CSV data in TIDB Cloud)
if 'scores_rag' not in st.session_state:
    st.session_state.scores_rag = pd.read_csv(
        'data/survey_data/standard_area_aggregate_scores_rag.csv')
if 'geojson_nd' not in st.session_state:
    f = open('data/area_data/geojson/combined_nd.geojson')
    st.session_state.geojson_nd = json.load(f)

# As we play around this one, import it from session state
df_scores = st.session_state.scores_rag

# Write title, introduction and key to RAG
area_intro()

st.subheader('Results by MSOA')

# Create selectbox and get chosen topic
chosen_variable_lab = choose_topic(df_scores)

# Replace NaN with "n<10", and use full label names for other categories
df_scores['rag'] = df_scores['rag'].map({
    'below': 'Below average',
    'average': 'Average',
    'above': 'Above average',
    np.nan: 'n<10'})

# Filter to chosen topic then filter to only used column (helps map speed)
chosen_result = df_scores[df_scores['variable_lab'] == chosen_variable_lab]
msoa_rag = chosen_result[['msoa', 'rag']]

#######
# Map #
#######

# Create map
fig = px.choropleth_mapbox(
    msoa_rag,
    geojson=st.session_state.geojson_nd,
    locations='msoa',
    featureidkey="properties.MSOA11NM",
    # Colour rules
    color='rag',
    color_discrete_map={'Below average': '#FFB3B3',
                        'Average': '#FFDFA6',
                        'Above average': '#7DD27D',
                        'n<10': '#F6FAFF'},
    opacity=0.75,
    # Base map stryle
    mapbox_style='carto-positron',
    # Positioning of map on load
    center={'lat': 50.955, 'lon': -4.1},
    zoom=8.4,
    labels={'rag': 'Result'},
    # Control legend order
    category_orders={
        'rag': ['Below average', 'Average', 'Above average', 'n<10']})

fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
st.plotly_chart(fig)
blank_lines(1)

# Add caveat for interpretation
st.subheader('Comparing between areas')
st.markdown(caution_comparing('area'))

page_footer('schools in Northern Devon')
