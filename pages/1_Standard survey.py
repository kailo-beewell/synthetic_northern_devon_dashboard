import json
from kailo_beewell_dashboard.explore_results import (
    choose_topic,
    create_bar_charts,
    create_topic_dict,
    get_chosen_result,
    write_response_section_intro,
    write_topic_intro)
from kailo_beewell_dashboard.map import rag_guide
from kailo_beewell_dashboard.page_setup import (
    blank_lines, page_footer, page_setup)
from kailo_beewell_dashboard.reuse_text import caution_comparing
from kailo_beewell_dashboard.score_descriptions import score_descriptions
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

df_prop = pd.read_csv('data/survey_data/standard_nd_aggregate_responses.csv')

# As we play around this one, import it from session state
df_scores = st.session_state.scores_rag

# Create topic dictionary
topic_dict = create_topic_dict(df_scores)

# Create dictionary where key is topic name and value is topic description
# (Duplication with explore_results.write_topic_intro())
description = (df_scores[['variable', 'description']]
               .drop_duplicates()
               .set_index('variable')
               .to_dict()['description'])

# Page title and introduction
st.title('Standard #BeeWell survey')

# Introduction and choose page

# Set default page
if 'standard_page' not in st.session_state:
    st.session_state.standard_page = 'area'

# Set button text weight depending on current choice
if st.session_state.standard_page == 'area':
    btn_area_txt = '**By area**'
    btn_char_txt = 'By characteristic'
elif st.session_state.standard_page == 'char':
    btn_area_txt = 'By area'
    btn_char_txt = '**By characteristic**'

st.divider()
st.markdown('''
The standard #BeeWell survey was completed by **N** pupils in Years 8 and
10 at **N** mainstream schools. You can view results either:''')
cols = st.columns(2)
with cols[0]:
    if st.button(btn_area_txt, key='btn_area', use_container_width=True):
        st.session_state.standard_page = 'area'
        st.rerun()
with cols[1]:
    if st.button(btn_char_txt, key='btn_char', use_container_width=True):
        st.session_state.standard_page = 'char'
        st.rerun()
st.divider()
blank_lines(2)

###################
# Results by area #
###################

if st.session_state.standard_page == 'area':
    st.subheader('Results by area')
    st.markdown(f'''
**Introduction:**

There were {len(topic_dict)} topics in the standard #BeeWell survey, each
composed of one or several items. In this section, an overall score has been
calculated for each topic, allowing you to compare scores between different
areas of Northern Devon. These are based just on responses from young people
who completed all of the questions for a given topic.

Results are presented by Middle Layer Super Output Area (MSOA). These are
geographic areas that were designed to improve reporting of small area
statistics.''')
    blank_lines(1)

    # Add key to RAG
    st.markdown('**Guide to the map:**')
    rag_guide()

    # Create selectbox to get chosen topic
    chosen_variable_lab, chosen_variable = choose_topic(
        df_scores, include_raw_name=True)

    # Add topic description
    topic_name = chosen_variable_lab.lower()
    topic_descrip = description[f'{chosen_variable}_score'].lower().lstrip()
    st.markdown(f'''
This map is based on overall scores for the topic of '{topic_name}'.
This topic is about **{topic_descrip}**, higher scores
indicating {score_descriptions[chosen_variable][1]}.''')

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

    # Add caveat for interpretation
    st.markdown('**Comparing between areas:**')
    st.markdown(caution_comparing('area'))

#############################
# Results by characteristic #
#############################

if st.session_state.standard_page == 'char':
    st.subheader('Results by characteristics')

    # Create selectbox to get chosen topic
    chosen_variable_lab, chosen_variable = choose_topic(
        df_scores, include_raw_name=True)

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
