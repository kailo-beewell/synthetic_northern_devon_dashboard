from kailo_beewell_dashboard.explore_results import (
    create_topic_dict)
from kailo_beewell_dashboard.page_setup import (
    page_footer, page_setup)
import pandas as pd
import streamlit as st

page_setup('public')

# Import data
df_scores = pd.read_csv(
    'data/survey_data/standard_area_aggregate_scores_rag.csv')

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

st.table(df_scores.head())

page_footer('schools in Northern Devon')
