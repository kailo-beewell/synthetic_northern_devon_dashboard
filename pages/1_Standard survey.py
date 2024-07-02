import json
from kailo_beewell_dashboard.explore_results import (
    create_bar_charts,
    create_topic_dict,
    get_chosen_result,
)
from kailo_beewell_dashboard.map import rag_guide
from kailo_beewell_dashboard.page_setup import blank_lines, page_footer, page_setup
from kailo_beewell_dashboard.reuse_text import caution_comparing
from kailo_beewell_dashboard.score_descriptions import score_descriptions
import numpy as np
import pandas as pd
import pickle
import plotly.express as px
import streamlit as st

##########
# Set-up #
##########


def render_area_tab_markup():
    st.subheader("Results by area")
    st.markdown("""

    **Introduction:**

    In this section, an overall score has been calculated for each topic, allowing
    you to compare scores between different areas of Northern Devon. These scores
    are based just on responses from young people who completed all of the
    questions for a given topic.

    Results are presented by Middle Layer Super Output Area (MSOA). These are
    geographic areas that were designed to improve reporting of small area
    statistics.""")
    blank_lines(1)

    # Add key to RAG
    st.markdown("**Guide to the map:**")
    rag_guide()

    # Create selectbox to get chosen topic
    chosen_variable_lab1 = st.selectbox(
        label="**Topic:**", options=topic_dict.keys(), key="topic_map"
    )
    chosen_variable1 = topic_dict[chosen_variable_lab1]

    # Add topic description
    topic_name = chosen_variable_lab1.lower()
    topic_descrip = description[f"{chosen_variable1}_score"].lower().lstrip()
    st.markdown(f"""
    This map is based on overall scores for the topic of '{topic_name}'.
    This topic is about **{topic_descrip}**, with higher scores
    indicating {score_descriptions[chosen_variable1][1]}.""")

    # Filter to chosen topic then filter to only used column (helps map speed)
    chosen_result = df_scores[df_scores["variable_lab"] == chosen_variable_lab1]
    msoa_rag = chosen_result[["msoa", "rag"]].copy()
    msoa_rag["rag"] = msoa_rag["rag"].map(
        {
            "below": "Below average",
            "average": "Average",
            "above": "Above average",
            np.nan: "n<10",
        }
    )

    # Create map
    fig = px.choropleth_mapbox(
        msoa_rag,
        geojson=st.session_state.geojson_nd,
        locations="msoa",
        featureidkey="properties.MSOA11NM",
        # Colour rules
        color="rag",
        color_discrete_map={
            "Below average": "#FFB3B3",
            "Average": "#FFDFA6",
            "Above average": "#7DD27D",
            "n<10": "#F6FAFF",
        },
        opacity=0.75,
        # Base map stryle
        mapbox_style="carto-positron",
        # Positioning of map on load
        center={"lat": 50.955, "lon": -4.1},
        zoom=8.4,
        labels={"rag": "Result"},
        # Control legend order
        category_orders={"rag": ["Below average", "Average", "Above average", "n<10"]},
    )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig)
    blank_lines(1)

    # Add caveat for interpretation
    st.markdown("**Comparing between areas:**")
    st.markdown(caution_comparing("area"))


def render_characteristic_tab_markup():
    st.subheader("Results by pupil characteristics")
    st.markdown("""
**Introduction:**

In this section, you can see how young people from across Northern Devon
responded to each of the questions in the survey. You can view results:
* For all pupils
* By year group
* By gender
* By free school meal (FSM) eligibility
* By whether pupils have special educational needs (SEN)""")

    # Create selectbox to get chosen topic
    chosen_variable_lab2 = st.selectbox(
        label="**Topic:**", options=topic_dict.keys(), key="topic_bar"
    )
    chosen_variable2 = topic_dict[chosen_variable_lab2]

    # Select pupils to view results for
    chosen_group = st.selectbox(
        "**View results:**",
        ["For all pupils", "By year group", "By gender", "By FSM", "By SEN"],
    )
    blank_lines(2)

    # Add topic description
    topic_name = chosen_variable_lab2.lower()
    topic_descrip = description[f"{chosen_variable2}_score"].lower().lstrip()
    st.markdown(f"""
**Results:**

The questions below relate to the topic of '**{topic_name}**'. This topic is
about **{topic_descrip}**.""")

    # Get dataframe with results for the chosen variable and group
    chosen_result = get_chosen_result(
        chosen_variable=chosen_variable2,
        chosen_group=chosen_group,
        df=df_prop,
        school=None,
        survey_type="standard",
    )

    # Produce bar charts with accompanying chart section descriptions and titles
    create_bar_charts(chosen_variable2, chosen_result)


def render_msoa_markup():
    st.subheader("Results by MSOA and topic")
    st.markdown("""
**Introduction:**

In this section, you can see survey results by topic across the different Middle Super Output Areas (MSOAs) in Northern Devon.""")


page_setup("public")

# Import data to session state if not already (this will later be done
# upon opening app on first page, with CSV data in TIDB Cloud)
if "scores_rag" not in st.session_state:
    st.session_state.scores_rag = pd.read_csv(
        "data/survey_data/standard_area_aggregate_scores_rag.csv"
    )
if "geojson_nd" not in st.session_state:
    f = open("data/area_data/geojson/combined_nd.geojson")
    st.session_state.geojson_nd = json.load(f)

# Import data
with open("data/survey_data/nd_overall_counts.pkl", "rb") as f:
    school_counts = pickle.load(f)
df_prop = pd.read_csv("data/survey_data/standard_nd_aggregate_responses.csv")

# As we play around this one, import it from session state
df_scores = st.session_state.scores_rag

# Create topic dictionary and convert to list. Get index of autonomy (default).
topic_dict = create_topic_dict(df_scores)
topic_list = list(topic_dict.keys())

# Create dictionary where key is topic name and value is topic description
# (Duplication with explore_results.write_topic_intro())
description = (
    df_scores[["variable", "description"]]
    .drop_duplicates()
    .set_index("variable")
    .to_dict()["description"]
)

# Page title and introduction
st.title("Standard #BeeWell survey")

# Introduction and choose page

# Set default page
if "standard_page" not in st.session_state:
    st.session_state.standard_page = "area"

# Set button text weight depending on current choice
# Determine button labels based on the session state
btn_area_label = (
    "**By area**" if st.session_state.get("standard_page") == "area" else "By area"
)
btn_char_label = (
    "**By pupil characteristics**"
    if st.session_state.get("standard_page") == "char"
    else "By pupil characteristics"
)
msoa_button_label = (
    "**By MSOA**" if st.session_state.get("standard_page") == "msoa" else "By MSOA"
)

st.divider()
st.markdown(f"""
The standard #BeeWell survey was completed by
{school_counts['standard_pupils']} pupils in Years 8 and 10 at
{school_counts['standard_schools']} mainstream schools. You can view results
either:""")


cols = st.columns(3)
with cols[0]:
    if st.button(btn_area_label, key="btn_area", use_container_width=True):
        st.session_state.standard_page = "area"
        st.rerun()
with cols[1]:
    if st.button(btn_char_label, key="btn_char", use_container_width=True):
        st.session_state.standard_page = "char"
        st.rerun()
with cols[2]:
    if st.button(msoa_button_label, key="btn_msoa", use_container_width=True):
        st.session_state.standard_page = "msoa"
        st.rerun()
st.divider()
blank_lines(2)

###################
# Results by area #
###################

if st.session_state.standard_page == "area":
    render_area_tab_markup()

elif st.session_state.standard_page == "char":
    render_characteristic_tab_markup()

elif st.session_state.standard_page == "msoa":
    render_msoa_markup()


page_footer("schools in Northern Devon")
