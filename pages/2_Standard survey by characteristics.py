from kailo_beewell_dashboard.explore_results import (
    choose_topic,
    create_bar_charts,
    get_chosen_result,
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
df_prop = pd.read_csv(
    'data/survey_data/standard_nd_aggregate_responses.csv')

#####################
# Page introduction #
#####################

st.title('Standard survey results by characteristics')

# Create selectbox to get chosen topic, and set default as Autonomy
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

#################################
# Responses to each question... #
#################################

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
