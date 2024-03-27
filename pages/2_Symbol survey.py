from kailo_beewell_dashboard.explore_results import (
    get_chosen_result,
    create_bar_charts)
from kailo_beewell_dashboard.page_setup import (
    blank_lines, page_footer, page_setup)
import pandas as pd
import streamlit as st

page_setup('public')

df_prop = pd.read_csv('data/survey_data/symbol_nd_aggregate_responses.csv')

# Title and introduction
st.title('Symbol #BeeWell Survey')
st.markdown('''
The symbol #BeeWell survey was completed by **N** pupils Years 7 to 11 at
**N** non-mainstream schools. On this page, you can see how young people from
across Northern Devon responded to each of the questions in the survey. You can
view results:
* For all pupils
* By year group
* By gender
* By free school meal (FSM) eligibility

It is not possible to share results by area due to the sample size.''')

# Select pupils to view results for
chosen_group = st.selectbox(
    '**View results:**', [
        'For all pupils', 'By year group', 'By gender', 'By FSM'])
blank_lines(2)

# Set chosen_variable and chosen_variable lab, and add to dataframe
# (We don't currently have any groupings, all on once page, so only adding
# this for simplicity in compatability with the bar chart functions
# used across the standard and symbol survey dashboards)
chosen_variable = 'symbol'
df_prop['group'] = chosen_variable

# Extract results for the chosen school and group
chosen_result = get_chosen_result(
    chosen_variable=chosen_variable,
    chosen_group=chosen_group,
    df=df_prop,
    school=None,
    survey_type='symbol')

# Produce bar charts w/ accompanying chart section descriptions and titles
create_bar_charts(chosen_variable, chosen_result)

page_footer('schools in Northern Devon')
