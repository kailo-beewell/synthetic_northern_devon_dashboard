import geopandas as gpd
from kailo_beewell_dashboard.map import (
    area_intro, choose_topic)
from kailo_beewell_dashboard.page_setup import (
    page_footer, page_setup)
from kailo_beewell_dashboard.reuse_text import caution_comparing
import pandas as pd
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

# Write title, introduction and key to RAG
area_intro()

st.subheader('Results by MSOA')

# Create selectbox and get chosen topic
chosen_variable_lab = choose_topic(df_scores)

#######
# Map #
#######

# Add caveat for interpretation
st.subheader('Comparing between areas')
st.markdown(caution_comparing('area'))

page_footer('schools in Northern Devon')
