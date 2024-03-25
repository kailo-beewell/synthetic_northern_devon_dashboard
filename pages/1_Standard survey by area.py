import json
from kailo_beewell_dashboard.explore_results import (
    choose_topic,
    create_bar_charts,
    get_chosen_result,
    write_response_section_intro,
    write_topic_intro)
from kailo_beewell_dashboard.map import rag_guide
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

# Page title and introduction
st.title('Standard #BeeWell survey')
st.markdown('''
The standard #BeeWell survey was completed by **N** pupils in Years 8 and 10
at **N** mainstream schools. Use the selectbox below to choose whether you
want to view:
* **Results by area**
* **Results by characteristics** - year group, gender, free school meal
(FSM) eligibility, and special education needs (SEN)
''')

# Select page view
pages = {
    'Results by area': 'area',
    'Results by characteristics': 'demographic'}
chosen_page = st.selectbox('**View:**', list(pages.keys()))

# Create selectbox to get chosen topic, and set default as Autonomy
chosen_variable_lab, chosen_variable = choose_topic(
    df_scores, include_raw_name=True)

blank_lines(1)
st.divider()

###################
# Results by area #
###################

if pages[chosen_page] == 'area':
    st.subheader('Results by area')
    st.markdown('''
This page shows how the results from young people varied across Northern Devon
by Middle Layer Super Output Area (MSOA).''')

    # Filter to chosen topic then filter to only used column (helps map speed)
    chosen_result = df_scores[df_scores['variable_lab'] == chosen_variable_lab]
    msoa_rag = chosen_result[['msoa', 'rag']].copy()
    msoa_rag['rag'] = msoa_rag['rag'].map({
        'below': 'Below average',
        'average': 'Average',
        'above': 'Above average',
        np.nan: 'n<10'})

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

    # Add key to RAG
    st.markdown('**Guide to the map:**')
    rag_guide()

    # Add caveat for interpretation
    st.markdown('**Comparing between areas:**')
    st.markdown(caution_comparing('area'))

#############################
# Results by characteristic #
#############################

if pages[chosen_page] == 'demographic':
    st.subheader('Results by characteristics')

    # Import data
    df_scores = pd.read_csv(
        'data/survey_data/standard_area_aggregate_scores_rag.csv')
    df_prop = pd.read_csv(
        'data/survey_data/standard_nd_aggregate_responses.csv')

    # Select pupils to view results for
    chosen_group = st.selectbox(
        '**View results:**', ['For all pupils', 'By year group',
                              'By gender', 'By FSM', 'By SEN'])
    blank_lines(2)

    # Topic header and description
    st.divider()
    write_topic_intro(chosen_variable, chosen_variable_lab, df_scores)
    blank_lines(1)

    # Section header and description
    write_response_section_intro(chosen_variable_lab, type='public')

    # Get dataframe with results for the chosen variable and group
    chosen_result = get_chosen_result(
        chosen_variable=chosen_variable,
        chosen_group=chosen_group,
        df=df_prop,
        school=None,
        survey_type='standard')

    # Produce bar charts w/ accompanying chart section descriptions and titles
    create_bar_charts(chosen_variable, chosen_result)

page_footer('schools in Northern Devon')
