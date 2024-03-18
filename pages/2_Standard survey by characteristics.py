from kailo_beewell_dashboard.explore_results import (
    create_topic_dict,
    write_response_section_intro,
    write_topic_intro)
from kailo_beewell_dashboard.page_setup import (
    blank_lines, page_footer, page_setup)
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

st.title('Standard survey results by characteristics')

# Select topic
chosen_variable_lab = st.selectbox(
    '**Topic:**', topic_dict.keys(), index=default)

# Convert from variable_lab to variable
chosen_variable = topic_dict[chosen_variable_lab]

# Select pupils to view results for
chosen_group = st.selectbox(
    '**View results:**', ['For all pupils', 'By year group',
                          'By gender', 'By FSM', 'By SEN'])
blank_lines(2)

# Topic header and description
st.divider()
write_topic_intro(chosen_variable, chosen_variable_lab, df_scores)
blank_lines(1)

#################################
# Responses to each question... #
#################################

# Section header and description
write_response_section_intro(chosen_variable_lab, type='public')

# Next step: create df_prop

page_footer('schools in Northern Devon')
