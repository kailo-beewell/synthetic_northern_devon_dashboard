from typing import Literal, Optional

import streamlit as st
import json
import pickle
import numpy as np
import pandas as pd
import plotly.express as px
from kailo_beewell_dashboard.explore_results import (
    create_bar_charts,
    create_topic_dict,
    get_chosen_result,
)
from kailo_beewell_dashboard.map import rag_guide
from kailo_beewell_dashboard.page_setup import page_setup, blank_lines, page_footer
from kailo_beewell_dashboard.reuse_text import caution_comparing
from kailo_beewell_dashboard.score_descriptions import score_descriptions


def create_rag_container(
    rag_text: str, bg_colour: str, font_colour: str, output: str = "streamlit"
):
    if output == "streamlit":
        st.markdown(
            f'<div style="background-color:{bg_colour};color:{font_colour};padding:10px;border-radius:5px;text-align:center;">{rag_text}</div>',
            unsafe_allow_html=True,
        )
    else:
        # Implement other output formats if needed
        pass


def display_rag_dict(rag_dict: list[dict]):
    for entry in rag_dict:
        variable_lab = entry["variable_lab"]
        rag_info = entry["rag"]

        col1, col2 = st.columns(2)

        with col1:
            st.write(variable_lab)

        with col2:
            create_rag_container(
                rag_info["rag_text"],
                rag_info["bg_colour"],
                rag_info["font_colour"],
                output="streamlit",
            )


def rag_for_msoas(dataframe: pd.DataFrame, msoa_name: str) -> list[dict]:
    """
    Filters the dataframe to only include rows which match the MSOA_Name as supplied as an argument.
    Keeps only the columns we need and returns them as list of dictionaries.
    """
    df = dataframe.copy(deep=True)
    # Keep the following columns:
    df = df[["variable", "msoa", "variable_lab", "rag", "count"]]
    # Filter the dataframe to only keep rows where the 'msoa' column matches the msoa_name
    df = df[df["msoa"] == msoa_name]
    result = df.to_dict(orient="records")
    return result


def get_rag_colour_scheme(rag: Optional[Literal["average", "above", "below"]]) -> dict:
    """
    We should be using this in the result-box function in the summary_rag.py
    """
    if rag == "below":
        return {
            "rag_text": "Below average",
            "bg_colour": "#FFCCCC",
            "font_colour": "#95444B",
        }
    elif rag == "average":
        return {"rag_text": "Average", "bg_colour": "#FFE8BF", "font_colour": "#AA7A18"}
    elif rag == "above":
        return {
            "rag_text": "Above average",
            "bg_colour": "#B6E6B6",
            "font_colour": "#2B7C47",
        }
    elif pd.isnull(rag):
        return {"rag_text": "n < 10", "bg_colour": "#DCE4FF", "font_colour": "#19539A"}
    else:
        raise ValueError(f"Unknown rag value: {rag}")


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
        # Base map style
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

In this section, you can see survey results for each topic within individual Middle Layer Super Output Areas (MSOAs) in Northern Devon. MSOAs are geographic areas designed to improve the reporting of small area statistics. An overall score has been calculated for each topic, allowing you to compare scores within a specific area across different topics. These scores are based solely on responses from young people who completed all the questions for a given topic. """)

    # RAG guide
    st.markdown("**Guide to the map:**")
    rag_guide()

    st.markdown("**Explore results**")
    st.markdown(
        "Choose an MSOA from the drop-down menu to see a summary of results by topic for that area. You can hover over the MSOAs on the map to see their names."
    )

    # Create a two-column layout
    select_and_map_cols = st.columns(2)

    # Put the select box in the first column
    with select_and_map_cols[0]:
        selected_msoa = st.selectbox(
            "Select MSOA:", st.session_state.msoa_df["msoa"].unique()
        )

    # Map in the second column
    with select_and_map_cols[1]:
        fig = px.choropleth_mapbox(
            st.session_state.msoa_df,
            geojson=st.session_state.geojson_nd,
            locations="msoa",
            featureidkey="properties.MSOA11NM",
            # Single colour for all areas
            color_discrete_sequence=["#B0B0B0"],  # Light grey colour
            opacity=0.75,
            # Base map style
            mapbox_style="carto-positron",
            # Positioning of map on load
            center={"lat": 50.955, "lon": -4.1},
            zoom=7.8,
            labels={"rag": "Result"},
        )

        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(fig)

    # Import data

    # Display detailed information for the selected MSOA
    st.subheader(f"Summary of Topics for {selected_msoa}")
    # selected_data = msoa_data[msoa_data["msoa"] == selected_msoa]

    # Map (either a static one for reference, or ) to be created here

    # Add caveat for interpretation
    st.markdown("**Comparing between areas:**")
    st.markdown(caution_comparing("area"))

    rag_df = pd.read_csv("data/survey_data/standard_area_aggregate_scores_rag.csv")

    rag_dict = rag_for_msoas(rag_df, selected_msoa)

    # Replace the RAG keys with our nice data structure which contains the button text, text colour and
    # the background colour
    for dict in rag_dict:
        dict["rag"] = get_rag_colour_scheme(dict["rag"])

    display_rag_dict(rag_dict)


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
if "msoa_df" not in st.session_state:
    st.session_state.msoa_df = pd.read_csv(
        "data/survey_data/standard_area_aggregate_scores_rag.csv"
    )


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

# Set default page
if "standard_page" not in st.session_state:
    st.session_state.standard_page = "area"

# Set button text weight depending on current choice
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
The standard #BeeWell survey was completed by {school_counts['standard_pupils']} pupils in Years 8 and 10 at {school_counts['standard_schools']} mainstream schools. You can view results either:""")

cols = st.columns(3)
with cols[0]:
    if st.button(btn_area_label, key="btn_area", use_container_width=True):
        st.session_state.standard_page = "area"
        st.experimental_rerun()
with cols[1]:
    if st.button(msoa_button_label, key="btn_msoa", use_container_width=True):
        st.session_state.standard_page = "msoa"
        st.experimental_rerun()
with cols[2]:
    if st.button(btn_char_label, key="btn_char", use_container_width=True):
        st.session_state.standard_page = "char"
        st.experimental_rerun()

st.divider()
blank_lines(2)

# Render the selected tab
if st.session_state.standard_page == "area":
    render_area_tab_markup()
elif st.session_state.standard_page == "char":
    render_characteristic_tab_markup()
elif st.session_state.standard_page == "msoa":
    render_msoa_markup()

page_footer("schools in Northern Devon")


# def show_msoa_topic_summary(msoa: str, msoa_agg_rag_dict: dict):
