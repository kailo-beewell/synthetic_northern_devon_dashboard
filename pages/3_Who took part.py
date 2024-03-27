from kailo_beewell_dashboard.page_setup import (
    blank_lines, page_footer, page_setup)
from kailo_beewell_dashboard.who_took_part import (
    demographic_plots)
import pandas as pd
import pickle
import streamlit as st

page_setup('public')

# Import data
with open('data/survey_data/nd_overall_counts.pkl', 'rb') as f:
    school_counts = pickle.load(f)
sta_dem = pd.read_csv('data/survey_data/standard_nd_aggregate_demographic.csv')
sym_dem = pd.read_csv('data/survey_data/symbol_nd_aggregate_demographic.csv')

st.title('Who took part?')

# Set default page
if 'sample_page' not in st.session_state:
    st.session_state.sample_page = 'sta'

# Set button text weight depending on current choice
if st.session_state.sample_page == 'sta':
    btn_sta_txt = '**Standard survey**'
    btn_sym_txt = 'Symbol survey'
elif st.session_state.sample_page == 'sym':
    btn_sta_txt = 'Standard survey'
    btn_sym_txt = '**Symbol survey**'

st.divider()
st.markdown('''
View sample of pupils who completed the:''')
cols = st.columns(2)
with cols[0]:
    if st.button(btn_sta_txt, key='btn_sta', use_container_width=True):
        st.session_state.sample_page = 'sta'
        st.rerun()
with cols[1]:
    if st.button(btn_sym_txt, key='btn_sym', use_container_width=True):
        st.session_state.sample_page = 'sym'
        st.rerun()
st.divider()
blank_lines(2)

if st.session_state.sample_page == 'sta':
    st.subheader('Standard survey respondents')
    st.markdown(f'''
The standard #BeeWell survey was completed by
{school_counts['standard_pupils']} pupils in Years 8 and 10 at
{school_counts['standard_schools']} mainstream schools. This page describes the
sample of young people who completed the standard survey.''')
    # Create the figures (with their titles and descriptions)
    sta_dem['site'] = 'Northern Devon'
    demographic_plots(
        dem_prop=sta_dem,
        chosen_school=None,
        chosen_group=None,
        group_lab='site',
        survey_type='standard',
        dashboard_type='area')


if st.session_state.sample_page == 'sym':
    # Subheader and introduction
    st.subheader('Symbol survey respondents')
    st.markdown(f'''
The symbol #BeeWell survey was completed by {school_counts['symbol_pupils']}
pupils Years 7 to 11 at {school_counts['symbol_schools']} non-mainstream
schools. This page describes the sample of young people who completed the
symbol survey.''')
    # Create the figures (with their titles and descriptions)
    sym_dem['plot_group'] = sym_dem['measure']
    sym_dem['site'] = 'Northern Devon'
    demographic_plots(
        dem_prop=sym_dem,
        chosen_school=None,
        chosen_group=None,
        group_lab='site',
        survey_type='symbol',
        dashboard_type='area')

page_footer('schools in Northern Devon')
